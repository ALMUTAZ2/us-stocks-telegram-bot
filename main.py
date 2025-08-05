import os
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
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
