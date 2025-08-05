import os
import sys
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """اختبار بسيط"""
    try:
        # التحقق من متغيرات البيئة
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        logger.info("🔍 فحص متغيرات البيئة...")
        
        if not bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN غير موجود!")
            sys.exit(1)
            
        if not chat_id:
            logger.error("❌ TELEGRAM_CHAT_ID غير موجود!")
            sys.exit(1)
            
        logger.info(f"✅ Bot Token: {bot_token[:10]}...")
        logger.info(f"✅ Chat ID: {chat_id}")
        
        # اختبار استيراد المكتبات
        logger.info("📦 اختبار المكتبات...")
        
        try:
            import requests
            logger.info("✅ requests")
        except ImportError as e:
            logger.error(f"❌ requests: {e}")
            
        try:
            import pandas as pd
            logger.info("✅ pandas")
        except ImportError as e:
            logger.error(f"❌ pandas: {e}")
            
        try:
            import yfinance as yf
            logger.info("✅ yfinance")
        except ImportError as e:
            logger.error(f"❌ yfinance: {e}")
            
        # اختبار إرسال رسالة بسيطة
        logger.info("📤 اختبار إرسال رسالة تليجرام...")
        
        import requests
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': f'🧪 اختبار البوت\n⏰ الوقت: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n✅ البوت يعمل بنجاح!'
        }
        
        response = requests.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
            logger.info("✅ تم إرسال الرسالة بنجاح!")
            print("🎉 الاختبار نجح! البوت يعمل.")
        else:
            logger.error(f"❌ فشل الإرسال: {response.status_code}")
            logger.error(f"Response: {response.text}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ خطأ عام: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
        plt.savefig(chart_path, dpi=300, bbox_inches='tight', 
                   facecolor='black', edgecolor='none')
        plt.close()
        
        logger.info(f"✅ تم إنشاء المخطط: {chart_path}")
        return chart_path
        
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء المخطط: {e}")
        return None

def create_report_text(df):
    """إنشاء نص التقرير"""
    try:
        logger.info("📝 جاري إنشاء نص التقرير...")
        
        # ترتيب حسب الأداء
        df_sorted = df.sort_values('Monthly_Change', ascending=False)
        
        report = f"""
📊 **تقرير الأسهم الأمريكية الشهري**
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}
🕐 الوقت: {datetime.now().strftime('%H:%M')} بتوقيت الرياض

🏆 **أفضل 3 أسهم أداءً:**
"""
        
        # أفضل 3 أسهم
        for i, (_, row) in enumerate(df_sorted.head(3).iterrows(), 1):
            report += f"{i}. **{row['Symbol']}** ({row['Name'][:20]}...)\n"
            report += f"   💰 السعر: ${row['Price']:.2f}\n"
            report += f"   📈 التغيير: {row['Monthly_Change']:+.2f}%\n\n"
        
        report += "📉 **أسوأ 3 أسهم أداءً:**\n"
        
        # أسوأ 3 أسهم
        for i, (_, row) in enumerate(df_sorted.tail(3).iterrows(), 1):
            report += f"{i}. **{row['Symbol']}** ({row['Name'][:20]}...)\n"
            report += f"   💰 السعر: ${row['Price']:.2f}\n"
            report += f"   📉 التغيير: {row['Monthly_Change']:+.2f}%\n\n"
        
        # إحصائيات عامة
        avg_change = df['Monthly_Change'].mean()
        positive_count = len(df[df['Monthly_Change'] > 0])
        negative_count = len(df[df['Monthly_Change'] < 0])
        
        report += f"""
📊 **إحصائيات عامة:**
• متوسط التغيير: {avg_change:.2f}%
• أسهم إيجابية: {positive_count} سهم
• أسهم سلبية: {negative_count} سهم
• إجمالي الأسهم: {len(df)} سهم

🤖 تم إنتاج هذا التقرير تلقائياً
"""
        
        logger.info("✅ تم إنشاء نص التقرير")
        return report
        
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء التقرير: {e}")
        return "❌ خطأ في إنشاء التقرير"

async def send_telegram_report(report_text, chart_path=None):
    """إرسال التقرير عبر تليجرام"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    try:
        logger.info("📤 جاري إرسال التقرير عبر تليجرام...")
        
        # إرسال النص
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=report_text,
            parse_mode='Markdown'
        )
        logger.info("✅ تم إرسال النص")
        
        # إرسال المخطط إذا كان متوفراً
        if chart_path and os.path.exists(chart_path):
            with open(chart_path, 'rb') as photo:
                await bot.send_photo(
                    chat_id=TELEGRAM_CHAT_ID,
                    photo=photo,
                    caption="📊 مخطط الأداء الشهري للأسهم الأمريكية"
                )
            logger.info("✅ تم إرسال المخطط")
        
        logger.info("🎉 تم إرسال التقرير كاملاً!")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال التقرير: {e}")
        raise
    finally:
        await bot.session.close()

async def main():
    """الدالة الرئيسية"""
    try:
        logger.info("🚀 بدء تشغيل تقرير الأسهم...")
        
        # جلب البيانات
        df = await get_stock_data()
        
        # إنشاء التقرير
        report_text = create_report_text(df)
        
        # إنشاء المخطط
        chart_path = create_chart(df)
        
        # إرسال التقرير
        await send_telegram_report(report_text, chart_path)
        
        logger.info("✅ تم إنجاز التقرير بنجاح!")
        
    except Exception as e:
        logger.error(f"❌ خطأ عام في التشغيل: {e}")
        
        # إرسال رسالة خطأ
        try:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"❌ خطأ في تقرير الأسهم:\n{str(e)}"
            )
            await bot.session.close()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
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
        
        sectors_summary = "\n".join([f"🏢 **{sector}:**\n" + "\n".join([f"   • {stock}" for stock in stocks]) for sector, stocks in sectors.items()])
        
        summary = f"""
🇺🇸 **التقرير الشهري - الأسهم الأمريكية**
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

✅ **الشارتات المُرسلة حسب القطاع:**
{sectors_summary}

📈 **معلومات إضافية:**
• المصدر: TradingView
• البورصة: NASDAQ/NYSE
• الإطار الزمني: 1 شهر
• نوع الشارت: Candlestick

🔄 **الموعد القادم:** 
📅 أول يوم من شهر {next_month} {next_year}
🕒 الساعة 3:00 صباحاً (UTC)

🤖 **المصدر:** GitHub Actions Bot - US Stocks Monitor
💡 **حالة البوت:** نشط ويعمل تلقائياً
        """.strip()
        
        await bot.send_message(
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
        current_year = current_date.year
        
        # تقدير الوقت المتوقع (حوالي 45 ثانية لكل سهم)
        estimated_time = len(STOCKS) * 45  # ثانية
        estimated_duration = format_duration(estimated_time)
        
        # حساب عدد الأسهم في كل قطاع
        sector_counts = {}
        for stock in STOCKS:
            sector = stock['sector']
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        sectors_info = "\n".join([f"• {sector}: {count} أسهم" for sector, count in sector_counts.items()])
        
        greeting = f"""
🇺🇸 **مرحباً بك في التقرير الشهري للأسهم الأمريكية!**

📅 **{current_month} {current_year}**
🕒 بدء التشغيل: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **ما سيتم عمله:**
• تصوير شارتات الأسهم الأمريكية على فريم شهري وإرسالها على التليجرام
• عدد الأسهم: {len(STOCKS)} سهم
• الوقت المتوقع للإنتهاء: {estimated_duration}

🏢 **القطاعات المشمولة:**
{sectors_info}

📈 **المصادر:**
• البورصة: NASDAQ/NYSE
• منصة الشارتات: TradingView
• نوع التحليل: شارتات شهرية

⏳ **جاري المعالجة...**
يرجى الانتظار بينما نجلب أحدث الشارتات لك
        """.strip()
        
        await bot.send_message(
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
    
    logger.info("🇺🇸 بدء تشغيل بوت الأسهم الأمريكية الشهري...")
    
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
❌ **خطأ في بوت الأسهم الأمريكية**

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
        logger.info(f"🏁 انتهى التشغيل الشهري للأسهم - الوقت الإجمالي: {format_duration(final_total_duration)}")

if __name__ == "__main__":
    asyncio.run(main())
