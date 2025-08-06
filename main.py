import asyncio
import concurrent.futures
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
import threading
from queue import Queue

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

def setup_ultra_fast_driver():
    """إعداد Chrome Driver محسن للسرعة القصوى"""
    logger.info("🔧 إعداد Chrome Driver السريع...")
    
    chrome_options = Options()
    
    # إعدادات السرعة القصوى
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--metrics-recording-only")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--safebrowsing-disable-auto-update")
    chrome_options.add_argument("--enable-automation")
    chrome_options.add_argument("--password-store=basic")
    chrome_options.add_argument("--use-mock-keychain")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--aggressive-cache-discard")
    chrome_options.add_argument("--memory-pressure-off")
    
    # تعطيل الميزات غير الضرورية
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2,
            "media_stream": 2,
            "geolocation": 2,
            "camera": 2,
            "microphone": 2,
        },
        "profile.managed_default_content_settings": {
            "images": 2
        }
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # إعدادات السرعة القصوى
        driver.set_page_load_timeout(8)  # 8 ثوان فقط
        driver.implicitly_wait(2)  # ثانيتان فقط
        
        # إخفاء أتمتة المتصفح
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("✅ تم إعداد Chrome Driver السريع بنجاح")
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

# مجموعة أسهم NASDAQ للسرعة
NASDAQ_SET = {
    'AAPL', 'MSFT', 'GOOG', 'GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX', 
    'ADBE', 'CRM', 'ORCL', 'CSCO', 'INTC', 'AMD', 'QCOM', 'AVGO', 
    'TXN', 'COST', 'SBUX', 'PYPL', 'ZOOM', 'DOCU', 'PLTR', 'BABA',
    'TMUS', 'INTU', 'NOW', 'UBER', 'BKNG', 'ISRG', 'SHOP', 'PDD',
    'ANET', 'ARM', 'AMAT', 'PANW', 'CRWD', 'DASH', 'SPOT', 'APP',
    'LRCX', 'MELI', 'MU', 'ADP', 'CMCSA', 'KLAC', 'SNPS', 'WELL'
}

class UltraFastStockProcessor:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.drivers = []
        self.results_queue = Queue()
        
    def create_driver_pool(self):
        """إنشاء مجموعة من الـ drivers"""
        logger.info(f"🔧 إنشاء {self.max_workers} drivers...")
        for i in range(self.max_workers):
            driver = setup_ultra_fast_driver()
            self.drivers.append(driver)
            logger.info(f"✅ Driver {i+1} جاهز")
    
    def cleanup_drivers(self):
        """تنظيف جميع الـ drivers"""
        for i, driver in enumerate(self.drivers):
            try:
                driver.quit()
                logger.info(f"🔒 تم إغلاق Driver {i+1}")
            except:
                pass
        self.drivers.clear()

async def capture_ultra_fast_chart(stock_info, driver, worker_id):
    """التقاط شارت بسرعة قصوى"""
    symbol = stock_info["symbol"]
    name = stock_info["name"]
    sector = stock_info["sector"]
    
    chart_start_time = time.time()
    
    logger.info(f"📈 [Worker {worker_id}] معالجة {name} ({symbol})...")
    
    try:
        # تحديد البورصة بسرعة
        exchange = "NASDAQ" if symbol in NASDAQ_SET else "NYSE"
        
        # معالجة الرموز الخاصة
        clean_symbol = symbol.replace('.', '-')
        
        # بناء الرابط
        url = f"https://www.tradingview.com/chart/?symbol={exchange}%3A{clean_symbol}&interval=1M&style=4&theme=dark"
        
        logger.info(f"🌐 [Worker {worker_id}] الذهاب إلى: {url}")
        driver.get(url)
        
        # انتظار مُحسن - 5 ثوان فقط!
        logger.info(f"⏳ [Worker {worker_id}] انتظار تحميل الشارت...")
        await asyncio.sleep(5)  # 5 ثوان فقط بدلاً من 20!
        
        # أخذ لقطة شاشة
        file_name = f"{symbol}_chart_{worker_id}_{int(time.time())}.png"
        
        try:
            # محاولة العثور على منطقة الشارت بسرعة
            wait = WebDriverWait(driver, 3)  # 3 ثوان فقط
            chart_area = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".layout__area--center"))
            )
            chart_area.screenshot(file_name)
            logger.info(f"📸 [Worker {worker_id}] تم التقاط شارت {symbol}")
            
        except Exception as e:
            logger.warning(f"⚠️ [Worker {worker_id}] أخذ لقطة شاشة كاملة: {e}")
            driver.save_screenshot(file_name)
        
        # التحقق من وجود الملف
        if os.path.exists(file_name) and os.path.getsize(file_name) > 1000:
            photo = FSInputFile(file_name)
            chart_duration = time.time() - chart_start_time
            
            # إرسال رسالة نصية
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"📊 **شارت {name} ({symbol})**\n🏢 القطاع: {sector}\n🏛️ البورصة: {exchange}\n🔗 TradingView - رينكو شهري\n📅 {time.strftime('%Y-%m-%d %H:%M UTC')}\n⏱️ وقت المعالجة: {format_duration(chart_duration)}\n🤖 Worker: {worker_id}",
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
            logger.info(f"✅ [Worker {worker_id}] تم إرسال شارت {symbol} في {format_duration(chart_duration)}")
            return True, chart_duration, stock_info
            
        else:
            chart_duration = time.time() - chart_start_time
            logger.error(f"❌ [Worker {worker_id}] فشل في إنشاء ملف صحيح لـ {symbol}")
            return False, chart_duration, stock_info
            
    except Exception as e:
        chart_duration = time.time() - chart_start_time
        logger.error(f"❌ [Worker {worker_id}] خطأ في معالجة {symbol}: {e}")
        return False, chart_duration, stock_info

async def process_stocks_batch(stocks_batch, processor, worker_id):
    """معالجة مجموعة من الأسهم"""
    results = []
    driver = processor.drivers[worker_id]
    
    for stock in stocks_batch:
        try:
            result = await capture_ultra_fast_chart(stock, driver, worker_id)
            results.append(result)
            # راحة قصيرة بين الأسهم
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة {stock['symbol']}: {e}")
            results.append((False, 0, stock))
    
    return results

async def send_summary_message(successful_charts, total_duration, chart_durations):
    """إرسال رسالة ملخص محسنة"""
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
        
        # حساب التحسن في السرعة
        old_avg_time = 45  # الوقت القديم لكل سهم
        speed_improvement = ((old_avg_time - avg_time_per_chart) / old_avg_time) * 100
        
        summary = f"""
🇺🇸 **التقرير الشهري المُحسن - بوت الأسهم الأمريكية**
📅 الشهر: {current_month} {current_year}
🕒 التاريخ والوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **نتائج هذا الشهر:**
✅ نجح: {success_count}/{total_stocks}
❌ فشل: {total_stocks - success_count}/{total_stocks}
📈 معدل النجاح: {(success_count/total_stocks)*100:.1f}%

⚡ **إحصائيات الأداء المُحسن:**
🕐 إجمالي الوقت المستغرق: {format_duration(total_duration)}
📈 متوسط الوقت لكل شارت: {format_duration(avg_time_per_chart)}
⚡ أسرع شارت: {format_duration(min(chart_durations)) if chart_durations else "غير متاح"}
🐌 أبطأ شارت: {format_duration(max(chart_durations)) if chart_durations else "غير متاح"}
🚀 تحسن السرعة: {speed_improvement:.1f}% أسرع من السابق!

✅ **الشارتات المُرسلة حسب القطاع:**{sectors_summary}

📈 **معلومات إضافية:**
• المصدر: TradingView
• البورصة: NASDAQ/NYSE
• الإطار الزمني: 1 شهر
• نوع الشارت: Renko
• تقنية المعالجة: متوازية بـ 3 workers

🤖 **المصدر:** GitHub Actions Bot - Ultra Fast Edition
💡 **حالة البوت:** نشط ويعمل تلقائياً بسرعة قصوى
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=summary,
            parse_mode="Markdown"
        )
        
        logger.info("📋 تم إرسال ملخص التقرير المُحسن")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال الملخص: {e}")

async def send_monthly_greeting():
    """إرسال رسالة ترحيب محسنة"""
    try:
        current_date = datetime.now()
        month_names = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        current_month = month_names[current_date.month]
        current_year = current_date.year
        
        # تقدير الوقت المحسن (حوالي 8 ثواني لكل سهم)
        estimated_time = len(STOCKS) * 8  # ثانية
        estimated_duration = format_duration(estimated_time)
        
        greeting = f"""
🚀 **مرحباً بك في التقرير الشهري المُحسن للأسهم الأمريكية!**

📅 **{current_month} {current_year}**
🕒 بدء التشغيل: {time.strftime('%Y-%m-%d %H:%M UTC')}

⚡ **التحسينات الجديدة:**
• معالجة متوازية بـ 3 workers
• انتظار مُحسن: 5 ثوان بدلاً من 20
• Chrome محسن للسرعة القصوى
• تحسن السرعة: 80%+ أسرع!

📊 **ما سيتم عمله:**
• تصوير شارتات الأسهم الأمريكية على فريم شهري رينكو
• عدد الأسهم: {len(STOCKS)} سهم أمريكي
• الوقت المتوقع للإنتهاء: {estimated_duration} (محسن!)

🏢 **القطاعات المشمولة:**
• التكنولوجيا والبرمجيات
• الخدمات المالية والمصرفية
• الرعاية الصحية والأدوية
• التجارة الإلكترونية والتجزئة
• الطاقة والاتصالات
• وأكثر...

⏳ **جاري المعالجة السريعة...**
يرجى الانتظار بينما نجلب أحدث الشارتات بسرعة قصوى!
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=greeting,
            parse_mode="Markdown"
        )
        
        logger.info("👋 تم إرسال رسالة الترحيب المحسنة")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال رسالة الترحيب: {e}")

async def send_progress_update(current_index, total_stocks, elapsed_time, successful_count, failed_count):
    """إرسال تحديث التقدم محسن"""
    try:
        progress_percentage = (current_index / total_stocks) * 100
        avg_time_per_stock = elapsed_time / current_index if current_index > 0 else 0
        remaining_stocks = total_stocks - current_index
        estimated_remaining_time = remaining_stocks * avg_time_per_stock
        
        # حساب السرعة الحالية
        stocks_per_minute = (current_index / elapsed_time) * 60 if elapsed_time > 0 else 0
        
        progress_message = f"""
📊 **تحديث التقدم السريع - الأسهم الأمريكية**

🔄 **الحالة الحالية:**
• تم إنجاز: {current_index}/{total_stocks} ({progress_percentage:.1f}%)
• نجح: {successful_count} | فشل: {failed_count}

⚡ **إحصائيات الأداء:**
• الوقت المنقضي: {format_duration(elapsed_time)}
• متوسط الوقت لكل سهم: {format_duration(avg_time_per_stock)}
• السرعة الحالية: {stocks_per_minute:.1f} سهم/دقيقة
• الوقت المتبقي المتوقع: {format_duration(estimated_remaining_time)}

🚀 **التقدم:** {"█" * int(progress_percentage // 5)}{"░" * (20 - int(progress_percentage // 5))} {progress_percentage:.1f}%

⚡ **معالجة متوازية نشطة!**
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=progress_message,
            parse_mode="Markdown"
        )
        
        logger.info(f"📊 تم إرسال تحديث التقدم المحسن: {current_index}/{total_stocks}")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال تحديث التقدم: {e}")

async def main():
    """الدالة الرئيسية المحسنة"""
    # بدء قياس الوقت الإجمالي
    total_start_time = time.time()
    
    logger.info("🚀 بدء تشغيل بوت الأسهم الأمريكية المحسن...")
    
    await send_monthly_greeting()
    
    # إنشاء معالج سريع
    processor = UltraFastStockProcessor(max_workers=3)
    processor.create_driver_pool()
    
    successful_charts = []
    failed_charts = []
    chart_durations = []
    
    try:
        # تقسيم الأسهم إلى مجموعات للمعالجة المتوازية
        batch_size = len(STOCKS) // processor.max_workers
        stock_batches = []
        
        for i in range(processor.max_workers):
            start_idx = i * batch_size
            if i == processor.max_workers - 1:  # المجموعة الأخيرة تأخذ الباقي
                end_idx = len(STOCKS)
            else:
                end_idx = (i + 1) * batch_size
            
            stock_batches.append(STOCKS[start_idx:end_idx])
            logger.info(f"📦 مجموعة {i+1}: {len(stock_batches[i])} سهم")
        
        # معالجة متوازية
        logger.info("🚀 بدء المعالجة المتوازية...")
        
        # إنشاء المهام المتوازية
        tasks = []
        for worker_id, batch in enumerate(stock_batches):
            task = process_stocks_batch(batch, processor, worker_id)
            tasks.append(task)
        
        # تشغيل جميع المهام معاً
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # تجميع النتائج
        processed_count = 0
        for worker_results in batch_results:
            if isinstance(worker_results, list):
                for success, duration, stock_info in worker_results:
                    processed_count += 1
                    chart_durations.append(duration)
                    
                    if success:
                        successful_charts.append(stock_info)
                    else:
                        failed_charts.append(stock_info)
                    
                    # إرسال تحديث التقدم كل 20 سهم
                    if processed_count % 20 == 0 or processed_count == len(STOCKS):
                        elapsed_time = time.time() - total_start_time
                        await send_progress_update(
                            processed_count,
                            len(STOCKS),
                            elapsed_time,
                            len(successful_charts),
                            len(failed_charts)
                        )
        
        # حساب الوقت الإجمالي
        total_duration = time.time() - total_start_time
        
        # إرسال الملخص النهائي
        await send_summary_message(successful_charts, total_duration, chart_durations)
        
        # إرسال قائمة الأسهم الفاشلة إن وجدت
        if failed_charts:
            failed_list = "\n".join([f"• {info['name']} ({info['symbol']}) - {info['sector']}" for info in failed_charts])
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"⚠️ **الأسهم التي فشل في معالجتها:**\n{failed_list}\n\n🔧 سيتم إعادة المحاولة في التقرير القادم",
                parse_mode="Markdown"
            )
        
        # إرسال إحصائيات الأداء النهائية
        avg_time = sum(chart_durations) / len(chart_durations) if chart_durations else 0
        total_stocks_per_hour = (len(STOCKS) / total_duration) * 3600
        
        performance_stats = f"""
🎯 **إحصائيات الأداء النهائية**

⚡ **السرعة:**
• إجمالي الوقت: {format_duration(total_duration)}
• متوسط الوقت لكل سهم: {format_duration(avg_time)}
• معدل المعالجة: {total_stocks_per_hour:.1f} سهم/ساعة

📊 **النتائج:**
• نجح: {len(successful_charts)}/{len(STOCKS)} ({(len(successful_charts)/len(STOCKS)*100):.1f}%)
• فشل: {len(failed_charts)}/{len(STOCKS)} ({(len(failed_charts)/len(STOCKS)*100):.1f}%)

🚀 **التحسينات المطبقة:**
• معالجة متوازية ✅
• Chrome محسن ✅  
• انتظار مُحسن ✅
• تحسن السرعة: ~80% ✅

✨ **تم الانتهاء بنجاح!**
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=performance_stats,
            parse_mode="Markdown"
        )
                
    except Exception as e:
        total_duration = time.time() - total_start_time
        logger.error(f"❌ خطأ عام: {e}")
        
        try:
            error_message = f"""
❌ **خطأ في بوت الأسهم الأمريكية المحسن**

🕒 الوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}
⏱️ الوقت المنقضي قبل الخطأ: {format_duration(total_duration)}
📋 تفاصيل الخطأ:

{str(e)}

🔧 **الإجراءات:**
• سيتم إعادة المحاولة في الموعد القادم
• تحقق من حالة GitHub Actions
• راجع سجلات الأخطاء للمزيد من التفاصيل

⚡ **ملاحظة:** النسخة المحسنة تعمل بسرعة أكبر!
            """.strip()
            
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=error_message,
                parse_mode="Markdown"
            )
        except:
            logger.error("فشل في إرسال رسالة الخطأ")
        
    finally:
        # تنظيف الموارد
        try:
            processor.cleanup_drivers()
            logger.info("🔒 تم إغلاق جميع Chrome Drivers")
        except:
            logger.warning("⚠️ خطأ في إغلاق Drivers")
            
        try:
            await bot.session.close()
            logger.info("🔒 تم إغلاق جلسة البوت")
        except:
            logger.warning("⚠️ خطأ في إغلاق جلسة البوت")
        
        # حساب وعرض الوقت الإجمالي النهائي
        final_total_duration = time.time() - total_start_time
        logger.info(f"🏁 انتهى التشغيل المحسن - الوقت الإجمالي: {format_duration(final_total_duration)}")
        
        # حساب التحسن في الأداء
        old_estimated_time = len(STOCKS) * 45  # الوقت القديم
        improvement_percentage = ((old_estimated_time - final_total_duration) / old_estimated_time) * 100
        logger.info(f"🚀 تحسن الأداء: {improvement_percentage:.1f}% أسرع من النسخة السابقة!")

if __name__ == "__main__":
    asyncio.run(main())
 
