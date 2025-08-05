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
from datetime import datetime, timedeltaإعداد التسجيلlogging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)قراءة إعدادات تليجرام من متغيرات البيئة أو القيم المباشرةTELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7762932301:AAHkbmxRKhvjeKV9uJNfh8t382cO0Ty7i2M")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "521974594")التحقق من وجود البياناتif not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("❌ بيانات تليجرام غير مضبوطة!")
    sys.exit(1)إعداد البوتbot = Bot(token=TELEGRAM_BOT_TOKEN)def format_duration(seconds):
    """تحويل الثواني إلى تنسيق مقروء"""
    if seconds < 60:
        return f"{seconds:.1f} ثانية"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} دقيقة"
    else:
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        return f"{hours:.1f} ساعة و {minutes:.0f} دقيقة"def setup_chrome_driver():
    """إعداد Chrome Driver لـ GitHub Actions"""
    logger.info("🔧 إعداد Chrome Driver...")chrome_options = Options()

# إعدادات ضرورية لـ GitHub Actions
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-plugins")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

try:
    driver = webdriver.Chrome(options=chrome_options)
    logger.info("✅ تم إعداد Chrome Driver بنجاح")
    return driver
except Exception as e:
    logger.error(f"❌ خطأ في إعداد Chrome: {e}")
    sys.exit(1)
الأسهم الأمريكية المطلوبةSTOCKS = [
    # أسهم التكنولوجيا الكبيرة (Big Tech)
    {"symbol": "AAPL", "name": "Apple Inc", "sector": "Technology"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
    {"symbol": "GOOGL", "name": "Alphabet Inc", "sector": "Technology"},
    {"symbol": "AMZN", "name": "Amazon.com Inc", "sector": "E-commerce"},
    {"symbol": "TSLA", "name": "Tesla Inc", "sector": "Electric Vehicles"},
    {"symbol": "META", "name": "Meta Platforms Inc", "sector": "Social Media"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Semiconductors"},
    {"symbol": "NFLX", "name": "Netflix Inc", "sector": "Streaming"},# البنوك والخدمات المالية
{"symbol": "JPM", "name": "JPMorgan Chase & Co", "sector": "Banking"},
{"symbol": "BAC", "name": "Bank of America Corp", "sector": "Banking"},
{"symbol": "WFC", "name": "Wells Fargo & Company", "sector": "Banking"},
{"symbol": "GS", "name": "Goldman Sachs Group Inc", "sector": "Investment Banking"},
{"symbol": "MS", "name": "Morgan Stanley", "sector": "Investment Banking"},
{"symbol": "V", "name": "Visa Inc", "sector": "Payment Systems"},
{"symbol": "MA", "name": "Mastercard Inc", "sector": "Payment Systems"},

# الرعاية الصحية والأدوية
{"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
{"symbol": "PFE", "name": "Pfizer Inc", "sector": "Pharmaceuticals"},
{"symbol": "UNH", "name": "UnitedHealth Group Inc", "sector": "Health Insurance"},
{"symbol": "ABBV", "name": "AbbVie Inc", "sector": "Pharmaceuticals"},
{"symbol": "MRK", "name": "Merck & Co Inc", "sector": "Pharmaceuticals"},

# الطاقة والنفط
{"symbol": "XOM", "name": "Exxon Mobil Corporation", "sector": "Oil & Gas"},
{"symbol": "CVX", "name": "Chevron Corporation", "sector": "Oil & Gas"},
{"symbol": "COP", "name": "ConocoPhillips", "sector": "Oil & Gas"},

# السلع الاستهلاكية
{"symbol": "PG", "name": "Procter & Gamble Co", "sector": "Consumer Goods"},
{"symbol": "KO", "name": "Coca-Cola Company", "sector": "Beverages"},
{"symbol": "PEP", "name": "PepsiCo Inc", "sector": "Beverages"},
{"symbol": "WMT", "name": "Walmart Inc", "sector": "Retail"},
{"symbol": "HD", "name": "Home Depot Inc", "sector": "Retail"},

# الصناعات والطيران
{"symbol": "BA", "name": "Boeing Company", "sector": "Aerospace"},
{"symbol": "CAT", "name": "Caterpillar Inc", "sector": "Heavy Machinery"},
{"symbol": "GE", "name": "General Electric Co", "sector": "Industrial"},

# الاتصالات والإعلام
{"symbol": "VZ", "name": "Verizon Communications Inc", "sector": "Telecommunications"},
{"symbol": "T", "name": "AT&T Inc", "sector": "Telecommunications"},
{"symbol": "DIS", "name": "Walt Disney Company", "sector": "Entertainment"},

# العقارات والمرافق
{"symbol": "NEE", "name": "NextEra Energy Inc", "sector": "Utilities"},
{"symbol": "AMT", "name": "American Tower Corp", "sector": "REITs"},

# أسهم نمو حديثة
{"symbol": "CRM", "name": "Salesforce Inc", "sector": "Cloud Software"},
{"symbol": "ADBE", "name": "Adobe Inc", "sector": "Software"},
{"symbol": "PYPL", "name": "PayPal Holdings Inc", "sector": "Fintech"},
{"symbol": "UBER", "name": "Uber Technologies Inc", "sector": "Transportation"},
{"symbol": "SPOT", "name": "Spotify Technology SA", "sector": "Music Streaming"},
{"symbol": "ZM", "name": "Zoom Video Communications", "sector": "Video Conferencing"}
]async def capture_tradingview_chart(stock_info, driver):
    """التقاط شارت من TradingView للأسهم الأمريكية"""
    symbol = stock_info["symbol"]
    name = stock_info["name"]
    sector = stock_info["sector"]# بدء قياس الوقت للسهم الواحد
chart_start_time = time.time()

logger.info(f"📈 معالجة {name} ({symbol})...")

try:
    # بناء رابط TradingView للأسهم الأمريكية مع الثيم الداكن
    url = f"https://www.tradingview.com/chart/?symbol=NASDAQ:{symbol}&interval=1M&style=1&theme=dark"
    
    logger.info(f"🌐 الذهاب إلى: {url}")
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
            text=f"📊 **شارت {name} ({symbol})**\n🏢 القطاع: {sector}\n🔗 TradingView - NASDAQ\n📅 {time.strftime('%Y-%m-%d %H:%M UTC')}\n⏱️ وقت المعالجة: {format_duration(chart_duration)}",
            parse_mode="Markdown"
        )
        
        # إرسال الصورة
        await bot.send_photo(
            chat_id=TELEGRAM_CHAT_ID,
            photo=photo,
            caption=f"📈 {name} ({sector}) - Monthly Chart"
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
    """إرسال رسالة ملخص شهرية للأسهم"""
    try:
        total_stocks = len(STOCKS)
        success_count = len(successful_charts)    current_date = datetime.now()
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
    
    sectors_summary = "\n".join([f"🏢 **{sector}:**\n" + "\n".join([f"   • {stock}" for stock in stocks]) for sector, stocks in sectors.items()])
    
    summary = f"""
🇺🇸 التقرير الشهري - الأسهم الأمريكية
📅 الشهر: {current_month} {current_year}
🕒 التاريخ والوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}📊 نتائج هذا الشهر:
✅ نجح: {success_count}/{total_stocks}
❌ فشل: {total_stocks - success_count}/{total_stocks}⏱️ إحصائيات الوقت:
🕐 إجمالي الوقت المستغرق: {format_duration(total_duration)}
📈 متوسط الوقت لكل شارت: {format_duration(avg_time_per_chart)}
⚡ أسرع شارت: {format_duration(min(chart_durations)) if chart_durations else "غير متاح"}
🐌 أبطأ شارت: {format_duration(max(chart_durations)) if chart_durations else "غير متاح"}✅ الشارتات المُرسلة حسب القطاع:
{sectors_summary}📈 معلومات إضافية:
• المصدر: TradingView
• البورصة: NASDAQ/NYSE
• الإطار الزمني: 1 شهر
• نوع الشارت: Candlestick🔄 الموعد القادم:
📅 أول يوم من شهر {next_month} {next_year}
🕒 الساعة 3:00 صباحاً (UTC)🤖 المصدر: GitHub Actions Bot - US Stocks Monitor
💡 حالة البوت: نشط ويعمل تلقائياً
        """.strip()    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=summary,
        parse_mode="Markdown"
    )
    
    logger.info("📋 تم إرسال ملخص التقرير الشهري للأسهم")
    
except Exception as e:
    logger.error(f"❌ خطأ في إرسال الملخص: {e}")
async def send_monthly_greeting():
    """إرسال رسالة ترحيب شهرية للأسهم"""
    try:
        current_date = datetime.now()
        month_names = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        current_month = month_names[current_date.month]
        current_year = current_date.year    # تقدير الوقت المتوقع (حوالي 45 ثانية لكل سهم)
    estimated_time = len(STOCKS) * 45  # ثانية
    estimated_duration = format_duration(estimated_time)
    
    # حساب عدد الأسهم في كل قطاع
    sector_counts = {}
    for stock in STOCKS:
        sector = stock['sector']
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    sectors_info = "\n".join([f"• {sector}: {count} أسهم" for sector, count in sector_counts.items()])
    
    greeting = f"""
🇺🇸 مرحباً بك في التقرير الشهري للأسهم الأمريكية!📅 {current_month} {current_year}
🕒 بدء التشغيل: {time.strftime('%Y-%m-%d %H:%M UTC')}📊 ما سيتم عمله:
• تصوير شارتات الأسهم الأمريكية على فريم شهري وإرسالها على التليجرام
• عدد الأسهم: {len(STOCKS)} سهم
• الوقت المتوقع للإنتهاء: {estimated_duration}🏢 القطاعات المشمولة:
{sectors_info}📈 المصادر:
• البورصة: NASDAQ/NYSE
• منصة الشارتات: TradingView
• نوع التحليل: شارتات شهرية⏳ جاري المعالجة...
يرجى الانتظار بينما نجلب أحدث الشارتات لك
        """.strip()    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=greeting,
        parse_mode="Markdown"
    )
    
    logger.info("👋 تم إرسال رسالة الترحيب الشهرية للأسهم")
    
except Exception as e:
    logger.error(f"❌ خطأ في إرسال رسالة الترحيب: {e}")
async def send_progress_update(current_index, total_stocks, elapsed_time, successful_count, failed_count):
    """إرسال تحديث التقدم كل 10 أسهم"""
    try:
        progress_percentage = (current_index / total_stocks) * 100
        avg_time_per_stock = elapsed_time / current_index if current_index > 0 else 0
        remaining_stocks = total_stocks - current_index
        estimated_remaining_time = remaining_stocks * avg_time_per_stockprogress_message = f"""📊 تحديث التقدم - الأسهم الأمريكية🔄 الحالة الحالية:
• تم إنجاز: {current_index}/{total_stocks} ({progress_percentage:.1f}%)
• نجح: {successful_count} | فشل: {failed_count}⏱️ إحصائيات الوقت:
• الوقت المنقضي: {format_duration(elapsed_time)}
• متوسط الوقت لكل سهم: {format_duration(avg_time_per_stock)}
• الوقت المتبقي المتوقع: {format_duration(estimated_remaining_time)}🚀 التقدم: {"█" * int(progress_percentage // 5)}{"░" * (20 - int(progress_percentage // 5))} {progress_percentage:.1f}%
        """.strip()    await bot.send_message(
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
    total_start_time = time.time()logger.info("🇺🇸 بدء تشغيل بوت الأسهم الأمريكية الشهري...")

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
        failed_list = "\n".join([f"• {info['name']} ({info['symbol']})" for info in failed_charts])
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
❌ خطأ في بوت الأسهم الأمريكية🕒 الوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}
⏱️ الوقت المنقضي قبل الخطأ: {format_duration(total_duration)}
📋 تفاصيل الخطأ:{str(e)}🔧 الإجراءات:
• سيتم إعادة المحاولة في الموعد القادم
• تحقق من حالة GitHub Actions
• راجع سجلات الأخطاء للمزيد من التفاصيل
            """.strip()        await bot.send_message(
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
    logger.info(f"🏁 انتهى التشغيل الشهري للأسهم - الوقت الإجمالي: {format_duration(final_total_duration)}")
if name == "main":
    asyncio.run(main())
