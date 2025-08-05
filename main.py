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
from aiogram import Bot
from aiogram.types import FSInputFile
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        # استخدام ChromeDriver المثبت مسبقاً
        service = Service('/usr/local/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # إخفاء أتمتة المتصفح
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
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
    {"symbol": "TSLA", "name": "Tesla Inc", "sector": "Electric Vehicles"},
    {"symbol": "META", "name": "Meta Platforms Inc", "sector": "Social Media"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Semiconductors"}
]

async def capture_tradingview_chart(stock_info, driver):
    """التقاط شارت من TradingView للأسهم الأمريكية"""
    symbol = stock_info["symbol"]
    name = stock_info["name"]
    sector = stock_info["sector"]
    
    chart_start_time = time.time()
    logger.info(f"📈 معالجة {name} ({symbol})...")
    
    try:
        # رابط TradingView مع إعدادات محددة
        url = f"https://www.tradingview.com/chart/?symbol=NASDAQ%3A{symbol}&interval=1M&style=1&theme=dark&hide_side_toolbar=1&hide_top_toolbar=1&hide_legend=1"
        
        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)
        
        # انتظار تحميل الصفحة
        logger.info("⏳ انتظار تحميل الشارت...")
        
        try:
            # انتظار ظهور الشارت
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-name='legend-source-item']")))
            logger.info("📊 تم تحميل الشارت بنجاح")
        except:
            logger.warning("⚠️ لم يتم العثور على عنصر الشارت، المتابعة بأخذ لقطة شاشة")
        
        # انتظار إضافي للتأكد من التحميل
        time.sleep(10)
        
        # أخذ لقطة شاشة
        file_name = f"{symbol}_chart.png"
        driver.save_screenshot(file_name)
        
        # التحقق من وجود الملف
        if os.path.exists(file_name) and os.path.getsize(file_name) > 5000:  # حجم أكبر للتأكد
            photo = FSInputFile(file_name)
            chart_duration = time.time() - chart_start_time
            
            # إرسال الصورة مع معلومات
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"📊 **{name} ({symbol})**\n🏢 القطاع: {sector}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n⏱️ وقت المعالجة: {format_duration(chart_duration)}",
                parse_mode="Markdown"
            )
            
            # حذف الملف
            os.remove(file_name)
            logger.info(f"✅ تم إرسال شارت {symbol} بنجاح في {format_duration(chart_duration)}")
            return True, chart_duration
            
        else:
            chart_duration = time.time() - chart_start_time
            logger.error(f"❌ فشل في إنشاء ملف صحيح لـ {symbol}")
            return False, chart_duration
            
    except Exception as e:
        chart_duration = time.time() - chart_start_time
        logger.error(f"❌ خطأ في معالجة {symbol}: {e}")
        return False, chart_duration

async def send_summary_message(successful_charts, total_duration, chart_durations):
    """إرسال رسالة ملخص"""
    try:
        total_stocks = len(STOCKS)
        success_count = len(successful_charts)
        
        # حساب متوسط الوقت
        avg_time = sum(chart_durations) / len(chart_durations) if chart_durations else 0
        
        # تجميع الأسهم الناجحة
        successful_stocks = "\n".join([f"• {stock['name']} ({stock['symbol']})" for stock in successful_charts])
        
        summary = f"""
🇺🇸 **تقرير الأسهم الأمريكية**

📊 النتائج:
✅ نجح: {success_count}/{total_stocks}
❌ فشل: {total_stocks - success_count}/{total_stocks}

⏱️ إحصائيات الوقت:
• الوقت الإجمالي: {format_duration(total_duration)}
• متوسط الوقت لكل سهم: {format_duration(avg_time)}

✅ الأسهم المُرسلة:
{successful_stocks}

🕒 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
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
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"🚀 **بدء تقرير الأسهم الأمريكية**\n📊 عدد الأسهم: {len(STOCKS)}\n⏳ جاري المعالجة...",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"خطأ في إرسال رسالة البداية: {e}")
    
    driver = setup_chrome_driver()
    successful_charts = []
    chart_durations = []
    
    try:
        for i, stock_info in enumerate(STOCKS):
            logger.info(f"🔄 معالجة السهم {i+1}/{len(STOCKS)}: {stock_info['name']}")
            
            success, duration = await capture_tradingview_chart(stock_info, driver)
            chart_durations.append(duration)
            
            if success:
                successful_charts.append(stock_info)
            
            # انتظار بين الأسهم لتجنب الحظر
            if i < len(STOCKS) - 1:
                logger.info("⏳ انتظار بين الأسهم...")
                time.sleep(8)
        
        # إرسال الملخص
        total_duration = time.time() - total_start_time
        await send_summary_message(successful_charts, total_duration, chart_durations)
        
    except Exception as e:
        logger.error(f"❌ خطأ عام: {e}")
        
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"❌ **خطأ في بوت الأسهم**\n\n```\n{str(e)}\n```",
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
