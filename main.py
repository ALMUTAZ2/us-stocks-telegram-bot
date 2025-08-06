import asyncio
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # إخفاء أتمتة المتصفح
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("✅ تم إعداد Chrome Driver بنجاح")
        return driver
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد Chrome: {e}")
        sys.exit(1)


# 📊 قائمة الأسهم الأمريكية المُحدثة (100 سهم)
STOCKS = [
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Electronic technology"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology services"},
    {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Electronic technology"},
    {"symbol": "GOOG", "name": "Alphabet Inc.", "sector": "Technology services"},
    {"symbol": "AMZN", "name": "Amazon.com, Inc.", "sector": "Retail trade"},
    {"symbol": "META", "name": "Meta Platforms, Inc.", "sector": "Technology services"},
    {"symbol": "AVGO", "name": "Broadcom Inc.", "sector": "Electronic technology"},
    {"symbol": "BRK.A", "name": "Berkshire Hathaway Inc.", "sector": "Finance"},
    {"symbol": "TSLA", "name": "Tesla, Inc.", "sector": "Consumer durables"},
    {"symbol": "JPM", "name": "JP Morgan Chase & Co.", "sector": "Finance"},
    {"symbol": "WMT", "name": "Walmart Inc.", "sector": "Retail trade"},
    {"symbol": "LLY", "name": "Eli Lilly and Company", "sector": "Health technology"},
    {"symbol": "ORCL", "name": "Oracle Corporation", "sector": "Technology services"},
    {"symbol": "V", "name": "Visa Inc.", "sector": "Finance"},
    {"symbol": "MA", "name": "Mastercard Incorporated", "sector": "Finance"},
    {"symbol": "NFLX", "name": "Netflix, Inc.", "sector": "Technology services"},
    {"symbol": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy minerals"},
    {"symbol": "COST", "name": "Costco Wholesale Corporation", "sector": "Retail trade"},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Health technology"},
    {"symbol": "PLTR", "name": "Palantir Technologies Inc.", "sector": "Technology services"},
    {"symbol": "HD", "name": "Home Depot, Inc. (The)", "sector": "Retail trade"},
    {"symbol": "PG", "name": "Procter & Gamble Company (The)", "sector": "Consumer non-durables"},
    {"symbol": "ABBV", "name": "AbbVie Inc.", "sector": "Health technology"},
    {"symbol": "BAC", "name": "Bank of America Corporation", "sector": "Finance"},
    {"symbol": "CVX", "name": "Chevron Corporation", "sector": "Energy minerals"},
    {"symbol": "KO", "name": "Coca-Cola Company (The)", "sector": "Consumer non-durables"},
    {"symbol": "GE", "name": "GE Aerospace", "sector": "Electronic technology"},
    {"symbol": "AMD", "name": "Advanced Micro Devices, Inc.", "sector": "Electronic technology"},
    {"symbol": "BABA", "name": "Alibaba Group Holding Limited", "sector": "Retail trade"},
    {"symbol": "TMUS", "name": "T-Mobile US, Inc.", "sector": "Communications"},
    {"symbol": "CSCO", "name": "Cisco Systems, Inc.", "sector": "Electronic technology"},
    {"symbol": "PM", "name": "Philip Morris International Inc", "sector": "Consumer non-durables"},
    {"symbol": "WFC", "name": "Wells Fargo & Company", "sector": "Finance"},
    {"symbol": "CRM", "name": "Salesforce, Inc.", "sector": "Technology services"},
    {"symbol": "IBM", "name": "International Business Machines Corporation", "sector": "Technology services"},
    {"symbol": "UNH", "name": "UnitedHealth Group Incorporated", "sector": "Health services"},
    {"symbol": "ABT", "name": "Abbott Laboratories", "sector": "Health technology"},
    {"symbol": "MS", "name": "Morgan Stanley", "sector": "Finance"},
    {"symbol": "LIN", "name": "Linde plc", "sector": "Process industries"},
    {"symbol": "GS", "name": "Goldman Sachs Group, Inc. (The)", "sector": "Finance"},
    {"symbol": "INTU", "name": "Intuit Inc.", "sector": "Technology services"},
    {"symbol": "MCD", "name": "McDonald's Corporation", "sector": "Consumer services"},
    {"symbol": "DIS", "name": "Walt Disney Company (The)", "sector": "Consumer services"},
    {"symbol": "RTX", "name": "RTX Corporation", "sector": "Electronic technology"},
    {"symbol": "AXP", "name": "American Express Company", "sector": "Finance"},
    {"symbol": "BX", "name": "Blackstone Inc.", "sector": "Finance"},
    {"symbol": "CAT", "name": "Caterpillar, Inc.", "sector": "Producer manufacturing"},
    {"symbol": "MRK", "name": "Merck & Company, Inc.", "sector": "Health technology"},
    {"symbol": "T", "name": "AT&T Inc.", "sector": "Communications"},
    {"symbol": "PEP", "name": "PepsiCo, Inc.", "sector": "Consumer non-durables"},
    {"symbol": "NOW", "name": "ServiceNow, Inc.", "sector": "Technology services"},
    {"symbol": "UBER", "name": "Uber Technologies, Inc.", "sector": "Transportation"},
    {"symbol": "VZ", "name": "Verizon Communications Inc.", "sector": "Communications"},
    {"symbol": "BKNG", "name": "Booking Holdings Inc.", "sector": "Consumer services"},
    {"symbol": "GEV", "name": "GE Vernova Inc.", "sector": "Producer manufacturing"},
    {"symbol": "TMO", "name": "Thermo Fisher Scientific Inc", "sector": "Health technology"},
    {"symbol": "SCHW", "name": "Charles Schwab Corporation (The)", "sector": "Finance"},
    {"symbol": "BLK", "name": "BlackRock, Inc.", "sector": "Finance"},
    {"symbol": "SPGI", "name": "S&P Global Inc.", "sector": "Commercial services"},
    {"symbol": "ISRG", "name": "Intuitive Surgical, Inc.", "sector": "Health technology"},
    {"symbol": "C", "name": "Citigroup, Inc.", "sector": "Finance"},
    {"symbol": "BA", "name": "Boeing Company (The)", "sector": "Electronic technology"},
    {"symbol": "TXN", "name": "Texas Instruments Incorporated", "sector": "Electronic technology"},
    {"symbol": "SHOP", "name": "Shopify Inc.", "sector": "Commercial services"},
    {"symbol": "AMGN", "name": "Amgen Inc.", "sector": "Health technology"},
    {"symbol": "QCOM", "name": "QUALCOMM Incorporated", "sector": "Electronic technology"},
    {"symbol": "PDD", "name": "PDD Holdings Inc.", "sector": "Retail trade"},
    {"symbol": "BSX", "name": "Boston Scientific Corporation", "sector": "Health technology"},
    {"symbol": "ACN", "name": "Accenture plc", "sector": "Technology services"},
    {"symbol": "ANET", "name": "Arista Networks, Inc.", "sector": "Electronic technology"},
    {"symbol": "NEE", "name": "NextEra Energy, Inc.", "sector": "Utilities"},
    {"symbol": "SYK", "name": "Stryker Corporation", "sector": "Health technology"},
    {"symbol": "ARM", "name": "Arm Holdings plc", "sector": "Electronic technology"},
    {"symbol": "AMAT", "name": "Applied Materials, Inc.", "sector": "Producer manufacturing"},
    {"symbol": "ADBE", "name": "Adobe Inc.", "sector": "Technology services"},
    {"symbol": "TJX", "name": "TJX Companies, Inc. (The)", "sector": "Retail trade"},
    {"symbol": "DHR", "name": "Danaher Corporation", "sector": "Health technology"},
    {"symbol": "PGR", "name": "Progressive Corporation (The)", "sector": "Finance"},
    {"symbol": "PFE", "name": "Pfizer, Inc.", "sector": "Health technology"},
    {"symbol": "HON", "name": "Honeywell International Inc.", "sector": "Electronic technology"},
    {"symbol": "GILD", "name": "Gilead Sciences, Inc.", "sector": "Health technology"},
    {"symbol": "ETN", "name": "Eaton Corporation, PLC", "sector": "Producer manufacturing"},
    {"symbol": "DE", "name": "Deere & Company", "sector": "Producer manufacturing"},
    {"symbol": "COF", "name": "Capital One Financial Corporation", "sector": "Finance"},
    {"symbol": "LOW", "name": "Lowe's Companies, Inc.", "sector": "Retail trade"},
    {"symbol": "UNP", "name": "Union Pacific Corporation", "sector": "Transportation"},
    {"symbol": "APH", "name": "Amphenol Corporation", "sector": "Electronic technology"},
    {"symbol": "SPOT", "name": "Spotify Technology S.A.", "sector": "Technology services"},
    {"symbol": "APP", "name": "Applovin Corporation", "sector": "Technology services"},
    {"symbol": "KKR", "name": "KKR & Co. Inc.", "sector": "Finance"},
    {"symbol": "LRCX", "name": "Lam Research Corporation", "sector": "Producer manufacturing"},
    {"symbol": "MELI", "name": "MercadoLibre, Inc.", "sector": "Retail trade"},
    {"symbol": "MU", "name": "Micron Technology, Inc.", "sector": "Electronic technology"},
    {"symbol": "ADP", "name": "Automatic Data Processing, Inc.", "sector": "Technology services"},
    {"symbol": "CMCSA", "name": "Comcast Corporation", "sector": "Consumer services"},
    {"symbol": "COP", "name": "ConocoPhillips", "sector": "Energy minerals"},
    {"symbol": "KLAC", "name": "KLA Corporation", "sector": "Electronic technology"},
    {"symbol": "SNPS", "name": "Synopsys, Inc.", "sector": "Technology services"},
    {"symbol": "MDT", "name": "Medtronic plc.", "sector": "Health technology"},
    {"symbol": "WELL", "name": "Welltower Inc.", "sector": "Finance"},
    {"symbol": "PANW", "name": "Palo Alto Networks, Inc.", "sector": "Technology services"},
    {"symbol": "BN", "name": "Brookfield Corporation", "sector": "Finance"},
    {"symbol": "CRWD", "name": "CrowdStrike Holdings, Inc.", "sector": "Technology services"},
    {"symbol": "NKE", "name": "Nike, Inc.", "sector": "Consumer non-durables"},
    {"symbol": "ADI", "name": "Analog Devices, Inc.", "sector": "Electronic technology"},
    {"symbol": "DASH", "name": "DoorDash, Inc.", "sector": "Transportation"},
    {"symbol": "CEG", "name": "Constellation Energy Corporation", "sector": "Utilities"},
    {"symbol": "ICE", "name": "Intercontinental Exchange Inc.", "sector": "Finance"}
]

async def capture_tradingview_chart(stock_info, driver):
    """التقاط شارت من TradingView للأسهم الأمريكية"""
    symbol = stock_info["symbol"]
    name = stock_info["name"]
    sector = stock_info["sector"]
    
    # بدء قياس الوقت للسهم الواحد
    chart_start_time = time.time()
    
    logger.info(f"📈 معالجة {name} ({symbol})...")
    
    try:
        # تحديد البورصة بناءً على رمز السهم
        nasdaq_symbols = [
            'AAPL', 'MSFT', 'GOOG', 'GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX', 
            'ADBE', 'CRM', 'ORCL', 'CSCO', 'INTC', 'AMD', 'QCOM', 'AVGO', 
            'TXN', 'COST', 'SBUX', 'PYPL', 'ZOOM', 'DOCU', 'PLTR', 'BABA',
            'TMUS', 'INTU', 'NOW', 'UBER', 'BKNG', 'ISRG', 'SHOP', 'PDD',
            'ANET', 'ARM', 'AMAT', 'PANW', 'CRWD', 'DASH', 'SPOT', 'APP',
            'LRCX', 'MELI', 'MU', 'ADP', 'CMCSA', 'KLAC', 'SNPS', 'WELL'
        ]
        
        # تحديد البورصة
        if symbol in nasdaq_symbols:
            exchange = "NASDAQ"
        else:
            exchange = "NYSE"
        
        # معالجة الرموز الخاصة (مثل BRK.A)
        clean_symbol = symbol.replace('.', '-')
        
        url = f"https://www.tradingview.com/chart/?symbol={exchange}%3A{clean_symbol}&interval=1M&style=4&theme=dark"        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)
        
        # انتظار تحميل الصفحة
        logger.info("⏳ انتظار تحميل الشارت...")
        time.sleep(20)  # انتظار أطول للتأكد من التحميل
        
        # أخذ لقطة شاشة
        file_name = f"{symbol}_chart.png"
        
        try:
            # محاولة العثور على منطقة الشارت
            wait = WebDriverWait(driver, 15)
            chart_area = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".layout__area--center"))
            )
            
            # أخذ لقطة شاشة للشارت فقط
            chart_area.screenshot(file_name)
            logger.info(f"📸 تم التقاط شارت {symbol}")
            
        except Exception as e:
            logger.warning(f"⚠️ فشل في العثور على الشارت، أخذ لقطة شاشة كاملة: {e}")
            driver.save_screenshot(file_name)
        
        # التحقق من وجود الملف
        if os.path.exists(file_name) and os.path.getsize(file_name) > 1000:
            # إرسال الصورة
            photo = FSInputFile(file_name)
            
            # حساب الوقت المستغرق لهذا السهم
            chart_duration = time.time() - chart_start_time
            
            # إرسال رسالة نصية أولاً
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"📊 **شارت {name} ({symbol})**\n🏢 القطاع: {sector}\n🏛️ البورصة: {exchange}\n🔗 TradingView - رينكو شهري\n📅 {time.strftime('%Y-%m-%d %H:%M UTC')}\n⏱️ وقت المعالجة: {format_duration(chart_duration)}",
                parse_mode="Markdown"
            )
            
            # إرسال الصورة
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"📈 {name} ({symbol}) - {sector} | {exchange}"
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
    """إرسال رسالة ملخص شهرية"""
    try:
        total_stocks = len(STOCKS)
        success_count = len(successful_charts)
        
        current_date = datetime.now()
        month_names = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        current_month = month_names[current_date.month]
        current_year = current_date.year
        
        next_month_num = current_date.month + 1 if current_date.month < 12 else 1
        next_year = current_year if current_date.month < 12 else current_year + 1
        next_month = month_names[next_month_num]
        
        # حساب متوسط الوقت لكل سهم
        avg_time_per_chart = sum(chart_durations) / len(chart_durations) if chart_durations else 0
        
        # تجميع الأسهم حسب القطاع
        sectors = {}
        for stock in successful_charts:
            sector = stock['sector']
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(f"{stock['name']} ({stock['symbol']})")
        
        sectors_summary = ""
        for sector, stocks in sectors.items():
            sectors_summary += f"\n🏢 **{sector}:**\n"
            for stock in stocks:
                sectors_summary += f"  • {stock}\n"
        
        summary = f"""
🇺🇸 **التقرير الشهري - بوت الأسهم الأمريكية**
📅 الشهر: {current_month} {current_year}
🕒 التاريخ والوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **نتائج هذا الشهر:**
✅ نجح: {success_count}/{total_stocks}
❌ فشل: {total_stocks - success_count}/{total_stocks}

⏱️ **إحصائيات الوقت:**
🕐 إجمالي الوقت المستغرق: {format_duration(total_duration)}
📈 متوسط الوقت لكل شارت: {format_duration(avg_time_per_chart)}
⚡ أسرع شارت: {format_duration(min(chart_durations)) if chart_durations else "غير متاح"}
🐌 أبطأ شارت: {format_duration(max(chart_durations)) if chart_durations else "غير متاح"}

✅ **الشارتات المُرسلة حسب القطاع:**{sectors_summary}

📈 **معلومات إضافية:**
• المصدر: TradingView
• البورصة: NASDAQ/NYSE
• الإطار الزمني: 1 شهر
• نوع الشارت: Renko

🔄 **الموعد القادم:** 
📅 أول يوم من شهر {next_month} {next_year}
🕒 الساعة 3:00 صباحاً (UTC)

🤖 **المصدر:** GitHub Actions Bot
💡 **حالة البوت:** نشط ويعمل تلقائياً
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=summary,
            parse_mode="Markdown"
        )
        
        logger.info("📋 تم إرسال ملخص التقرير الشهري")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال الملخص: {e}")

async def send_monthly_greeting():
    """إرسال رسالة ترحيب شهرية"""
    try:
        current_date = datetime.now()
        month_names = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        current_month = month_names[current_date.month]
        current_year = current_date.year
        
        # تقدير الوقت المتوقع (حوالي 45 ثانية لكل سهم)
        estimated_time = len(STOCKS) * 45  # ثانية
        estimated_duration = format_duration(estimated_time)
        
        greeting = f"""
🚀 **مرحباً بك في التقرير الشهري للأسهم الأمريكية!**

📅 **{current_month} {current_year}**
🕒 بدء التشغيل: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **ما سيتم عمله:**
• تصوير شارتات الأسهم الأمريكية على فريم شهري رينكو وإرساله على التليجرام بشكل شهري
• عدد الأسهم: {len(STOCKS)} سهم أمريكي
• الوقت المتوقع للإنتهاء: {estimated_duration}

🏢 **القطاعات المشمولة:**
• التكنولوجيا والبرمجيات
• الخدمات المالية والمصرفية
• الرعاية الصحية والأدوية
• التجارة الإلكترونية والتجزئة
• الطاقة والاتصالات
• وأكثر...

⏳ **جاري المعالجة...**
يرجى الانتظار بينما نجلب أحدث الشارتات لك
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=greeting,
            parse_mode="Markdown"
        )
        
        logger.info("👋 تم إرسال رسالة الترحيب الشهرية")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال رسالة الترحيب: {e}")

async def send_progress_update(current_index, total_stocks, elapsed_time, successful_count, failed_count):
    """إرسال تحديث التقدم كل 10 أسهم"""
    try:
        progress_percentage = (current_index / total_stocks) * 100
        avg_time_per_stock = elapsed_time / current_index if current_index > 0 else 0
        remaining_stocks = total_stocks - current_index
        estimated_remaining_time = remaining_stocks * avg_time_per_stock
        
        progress_message = f"""
📊 **تحديث التقدم - الأسهم الأمريكية**

🔄 **الحالة الحالية:**
• تم إنجاز: {current_index}/{total_stocks} ({progress_percentage:.1f}%)
• نجح: {successful_count} | فشل: {failed_count}

⏱️ **إحصائيات الوقت:**
• الوقت المنقضي: {format_duration(elapsed_time)}
• متوسط الوقت لكل سهم: {format_duration(avg_time_per_stock)}
• الوقت المتبقي المتوقع: {format_duration(estimated_remaining_time)}

🚀 **التقدم:** {"█" * int(progress_percentage // 5)}{"░" * (20 - int(progress_percentage // 5))} {progress_percentage:.1f}%
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=progress_message,
            parse_mode="Markdown"
        )
        
        logger.info(f"📊 تم إرسال تحديث التقدم: {current_index}/{total_stocks}")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال تحديث التقدم: {e}")

async def main():
    """الدالة الرئيسية"""
    # بدء قياس الوقت الإجمالي
    total_start_time = time.time()
    
    logger.info("🚀 بدء تشغيل بوت الأسهم الأمريكية الشهري...")
    
    await send_monthly_greeting()
    
    driver = setup_chrome_driver()
    successful_charts = []
    failed_charts = []
    chart_durations = []  # لحفظ أوقات كل شارت
    
    try:
        for i, stock_info in enumerate(STOCKS):
            logger.info(f"🔄 معالجة السهم {i+1}/{len(STOCKS)}: {stock_info['name']}")
            
            success, duration = await capture_tradingview_chart(stock_info, driver)
            chart_durations.append(duration)
            
            if success:
                successful_charts.append(stock_info)
            else:
                failed_charts.append(stock_info)
            
            # إرسال تحديث التقدم كل 10 أسهم
            if (i + 1) % 10 == 0 or (i + 1) == len(STOCKS):
                elapsed_time = time.time() - total_start_time
                await send_progress_update(
                    i + 1, 
                    len(STOCKS), 
                    elapsed_time, 
                    len(successful_charts), 
                    len(failed_charts)
                )
            
            if i < len(STOCKS) - 1:
                logger.info("⏳ انتظار بين الأسهم...")
                time.sleep(10)
        
        # حساب الوقت الإجمالي
        total_duration = time.time() - total_start_time
        
        await send_summary_message(successful_charts, total_duration, chart_durations)
        
        if failed_charts:
            failed_list = "\n".join([f"• {info['name']} ({info['symbol']}) - {info['sector']}" for info in failed_charts])
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"⚠️ **الأسهم التي فشل في معالجتها:**\n{failed_list}\n\n🔧 سيتم إعادة المحاولة في التقرير القادم",
                parse_mode="Markdown"
            )
                
    except Exception as e:
        total_duration = time.time() - total_start_time
        logger.error(f"❌ خطأ عام: {e}")
        
        try:
            error_message = f"""
❌ **خطأ في بوت الأسهم الأمريكية الشهري**

🕒 الوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}
⏱️ الوقت المنقضي قبل الخطأ: {format_duration(total_duration)}
📋 تفاصيل الخطأ:

{str(e)}

🔧 **الإجراءات:**
• سيتم إعادة المحاولة في الموعد القادم
• تحقق من حالة GitHub Actions
• راجع سجلات الأخطاء للمزيد من التفاصيل
            """.strip()
            
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=error_message,
                parse_mode="Markdown"
            )
        except:
            logger.error("فشل في إرسال رسالة الخطأ")
        
    finally:
        try:
            driver.quit()
            logger.info("🔒 تم إغلاق Chrome Driver")
        except:
            logger.warning("⚠️ خطأ في إغلاق Driver")
            
        try:
            await bot.session.close()
            logger.info("🔒 تم إغلاق جلسة البوت")
        except:
            logger.warning("⚠️ خطأ في إغلاق جلسة البوت")
        
        # حساب وعرض الوقت الإجمالي النهائي
        final_total_duration = time.time() - total_start_time
        logger.info(f"🏁 انتهى التشغيل الشهري - الوقت الإجمالي: {format_duration(final_total_duration)}")

if __name__ == "__main__":
    asyncio.run(main())
