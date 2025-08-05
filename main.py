import asyncio
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from aiogram import Bot
from aiogram.types import FSInputFile
import logging
from datetime import datetime, timedelta

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# قراءة إعدادات تليجرام من متغيرات البيئة
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# التحقق من وجود البيانات
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("❌ بيانات تليجرام غير مضبوطة!")
    sys.exit(1)

# إعداد البوت
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def format_duration(seconds):
    """تحويل الثواني إلى تنسيق مقروء"""
    if seconds < 60:
        return f"{seconds:.1f} ثانية"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} دقيقة"
    else:
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        return f"{hours:.1f} ساعة و {minutes:.0f} دقيقة"

def setup_chrome_driver():
    """إعداد Chrome Driver لـ GitHub Actions"""
    logger.info("🔧 إعداد Chrome Driver...")
    
    chrome_options = Options()
    
    # إعدادات ضرورية لـ GitHub Actions
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    try:
        # استخدام webdriver-manager لتحميل ChromeDriver تلقائياً
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("✅ تم إعداد Chrome Driver بنجاح")
        return driver
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد Chrome: {e}")
        sys.exit(1)

# قائمة أسهم مبسطة للاختبار
STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc", "sector": "Technology"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
    {"symbol": "GOOGL", "name": "Alphabet Inc", "sector": "Technology"},
    {"symbol": "AMZN", "name": "Amazon.com Inc", "sector": "E-commerce"},
    {"symbol": "TSLA", "name": "Tesla Inc", "sector": "Electric Vehicles"}
]

async def capture_tradingview_chart(stock_info, driver):
    """التقاط شارت من TradingView للأسهم الأمريكية"""
    symbol = stock_info["symbol"]
    name = stock_info["name"]
    sector = stock_info["sector"]
    
    chart_start_time = time.time()
    logger.info(f"📈 معالجة {name} ({symbol})...")
    
    try:
        # رابط TradingView مبسط
        url = f"https://www.tradingview.com/symbols/{symbol}/"
        
        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)
        
        # انتظار تحميل الصفحة
        logger.info("⏳ انتظار تحميل الشارت...")
        time.sleep(15)
        
        # أخذ لقطة شاشة
        file_name = f"{symbol}_chart.png"
        driver.save_screenshot(file_name)
        
        # التحقق من وجود الملف
        if os.path.exists(file_name) and os.path.getsize(file_name) > 1000:
            photo = FSInputFile(file_name)
            chart_duration = time.time() - chart_start_time
            
            # إرسال الصورة مع معلومات
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"📊 **{name} ({symbol})**\n🏢 القطاع: {sector}\n⏱️ وقت المعالجة: {format_duration(chart_duration)}",
                parse_mode="Markdown"
            )
            
            # حذف الملف
            os.remove(file_name)
            logger.info(f"✅ تم إرسال شارت {symbol} بنجاح")
            return True, chart_duration
            
        else:
            chart_duration = time.time() - chart_start_time
            logger.error(f"❌ فشل في إنشاء ملف صحيح لـ {symbol}")
            return False, chart_duration
            
    except Exception as e:
        chart_duration = time.time() - chart_start_time
        logger.error(f"❌ خطأ في معالجة {symbol}: {e}")
        return False, chart_duration

async def send_summary_message(successful_charts, total_duration):
    """إرسال رسالة ملخص"""
    try:
        total_stocks = len(STOCKS)
        success_count = len(successful_charts)
        
        summary = f"""
🇺🇸 **تقرير الأسهم الأمريكية**

📊 النتائج:
✅ نجح: {success_count}/{total_stocks}
❌ فشل: {total_stocks - success_count}/{total_stocks}

⏱️ الوقت الإجمالي: {format_duration(total_duration)}
🕒 التاريخ: {time.strftime('%Y-%m-%d %H:%M UTC')}

🤖 المصدر: GitHub Actions Bot
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=summary,
            parse_mode="Markdown"
        )
        
        logger.info("📋 تم إرسال ملخص التقرير")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال الملخص: {e}")

async def main():
    """الدالة الرئيسية"""
    total_start_time = time.time()
    
    logger.info("🇺🇸 بدء تشغيل بوت الأسهم...")
    
    # إرسال رسالة البداية
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text="🚀 **بدء تقرير الأسهم الأمريكية**\n⏳ جاري المعالجة...",
        parse_mode="Markdown"
    )
    
    driver = setup_chrome_driver()
    successful_charts = []
    
    try:
        for i, stock_info in enumerate(STOCKS):
            logger.info(f"🔄 معالجة السهم {i+1}/{len(STOCKS)}: {stock_info['name']}")
            
            success, duration = await capture_tradingview_chart(stock_info, driver)
            
            if success:
                successful_charts.append(stock_info)
            
            # انتظار بين الأسهم
            if i < len(STOCKS) - 1:
                logger.info("⏳ انتظار بين الأسهم...")
                time.sleep(5)
        
        # إرسال الملخص
        total_duration = time.time() - total_start_time
        await send_summary_message(successful_charts, total_duration)
        
    except Exception as e:
        logger.error(f"❌ خطأ عام: {e}")
        
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"❌ **خطأ في بوت الأسهم**\n\n{str(e)}",
                parse_mode="Markdown"
            )
        except:
            logger.error("فشل في إرسال رسالة الخطأ")
    
    finally:
        try:
            driver.quit()
            logger.info("🔒 تم إغلاق Chrome Driver")
        except:
            pass
            
        try:
            await bot.session.close()
            logger.info("🔒 تم إغلاق جلسة البوت")
        except:
            pass
        
        final_duration = time.time() - total_start_time
        logger.info(f"🏁 انتهى التشغيل - الوقت الإجمالي: {format_duration(final_duration)}")

if __name__ == "__main__":
    asyncio.run(main())
