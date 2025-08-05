import os
import sys
import logging
import requests
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import io
import base64

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إعداد matplotlib للعربية
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Tahoma', 'DejaVu Sans']

class StockReporter:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_message(self, text):
        """إرسال رسالة نصية"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=30)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"خطأ في إرسال الرسالة: {e}")
            return False
    
    def send_photo(self, photo_data, caption=""):
        """إرسال صورة"""
        try:
            url = f"{self.base_url}/sendPhoto"
            files = {'photo': ('chart.png', photo_data, 'image/png')}
            data = {
                'chat_id': self.chat_id,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, files=files, data=data, timeout=60)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"خطأ في إرسال الصورة: {e}")
            return False
    
    def get_stock_data(self, symbol, period="1mo"):
        """جلب بيانات السهم"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            info = stock.info
            return data, info
        except Exception as e:
            logger.error(f"خطأ في جلب بيانات {symbol}: {e}")
            return None, None
    
    def create_stock_chart(self, data, symbol, info):
        """إنشاء مخطط السهم"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # رسم السعر
            ax.plot(data.index, data['Close'], linewidth=2, color='#1f77b4', label='سعر الإغلاق')
            ax.fill_between(data.index, data['Close'], alpha=0.3, color='#1f77b4')
            
            # تنسيق المحاور
            ax.set_title(f'{symbol} - آخر 30 يوم', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('التاريخ', fontsize=12)
            ax.set_ylabel('السعر ($)', fontsize=12)
            
            # تنسيق التواريخ
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            plt.xticks(rotation=45)
            
            # شبكة
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # حفظ في الذاكرة
            plt.tight_layout()
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء المخطط: {e}")
            return None
    
    def format_stock_info(self, symbol, data, info):
        """تنسيق معلومات السهم"""
        try:
            current_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
            change = current_price - prev_price
            change_percent = (change / prev_price) * 100
            
            # رمز الاتجاه
            trend_emoji = "📈" if change >= 0 else "📉"
            change_sign = "+" if change >= 0 else ""
            
            # معلومات إضافية
            volume = data['Volume'].iloc[-1] if 'Volume' in data else 0
            high_52w = info.get('fiftyTwoWeekHigh', 'N/A')
            low_52w = info.get('fiftyTwoWeekLow', 'N/A')
            market_cap = info.get('marketCap', 'N/A')
            
            # تنسيق القيم
            if isinstance(market_cap, (int, float)):
                if market_cap >= 1e12:
                    market_cap_str = f"{market_cap/1e12:.2f}T"
                elif market_cap >= 1e9:
                    market_cap_str = f"{market_cap/1e9:.2f}B"
                elif market_cap >= 1e6:
                    market_cap_str = f"{market_cap/1e6:.2f}M"
                else:
                    market_cap_str = f"{market_cap:,.0f}"
            else:
                market_cap_str = "N/A"
            
            text = f"""
🏢 <b>{symbol}</b> - {info.get('longName', symbol)}

💰 <b>السعر الحالي:</b> ${current_price:.2f}
{trend_emoji} <b>التغيير:</b> {change_sign}{change:.2f} ({change_sign}{change_percent:.2f}%)

📊 <b>معلومات إضافية:</b>
• أعلى 52 أسبوع: ${high_52w}
• أقل 52 أسبوع: ${low_52w}
• القيمة السوقية: ${market_cap_str}
• حجم التداول: {volume:,.0f}

⏰ <b>آخر تحديث:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق المعلومات: {e}")
            return f"❌ خطأ في معالجة بيانات {symbol}"
    
    def generate_report(self):
        """إنشاء التقرير الكامل"""
        try:
            # قائمة الأسهم المهمة
            stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
            
            # رسالة البداية
            start_message = f"""
🚀 <b>تقرير الأسهم الشهري</b>
📅 {datetime.now().strftime('%Y-%m-%d')}

📈 سنقوم بتحليل أهم الأسهم في السوق الأمريكي...
            """.strip()
            
            self.send_message(start_message)
            
            # معالجة كل سهم
            for i, symbol in enumerate(stocks, 1):
                logger.info(f"معالجة السهم {i}/{len(stocks)}: {symbol}")
                
                # جلب البيانات
                data, info = self.get_stock_data(symbol)
                
                if data is None or data.empty:
                    self.send_message(f"❌ لم نتمكن من جلب بيانات {symbol}")
                    continue
                
                # إنشاء المخطط
                chart_data = self.create_stock_chart(data, symbol, info)
                
                # تنسيق المعلومات
                stock_info = self.format_stock_info(symbol, data, info)
                
                # إرسال المخطط مع المعلومات
                if chart_data:
                    success = self.send_photo(chart_data, stock_info)
                    if not success:
                        self.send_message(stock_info)
                else:
                    self.send_message(stock_info)
                
                # انتظار قصير بين الأسهم
                import time
                time.sleep(2)
            
            # رسالة الختام
            end_message = f"""
✅ <b>انتهى التقرير</b>

📊 تم تحليل {len(stocks)} أسهم
⏰ وقت التقرير: {datetime.now().strftime('%H:%M')}

💡 <i>هذا التقرير للمعلومات فقط وليس نصيحة استثمارية</i>
            """.strip()
            
            self.send_message(end_message)
            
            logger.info("✅ تم إنشاء التقرير بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء التقرير: {e}")
            self.send_message(f"❌ خطأ في إنشاء التقرير: {str(e)}")
            return False

def main():
    """الدالة الرئيسية"""
    try:
        # جلب متغيرات البيئة
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            logger.error("❌ متغيرات البيئة مفقودة")
            sys.exit(1)
        
        logger.info("🚀 بدء تشغيل بوت الأسهم...")
        
        # إنشاء مولد التقارير
        reporter = StockReporter(bot_token, chat_id)
        
        # إنشاء التقرير
        success = reporter.generate_report()
        
        if success:
            logger.info("🎉 تم إنجاز المهمة بنجاح")
        else:
            logger.error("❌ فشل في إنجاز المهمة")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ خطأ عام: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
