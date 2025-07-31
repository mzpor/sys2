 """
تمرین 18: سیستم ثبت گزارش
سطح: متوسط
هدف: آشنایی با سیستم لاگینگ پیشرفته
"""

import logging
import logging.handlers
from datetime import datetime
import os

class BotLogger:
    """کلاس مدیریت لاگینگ ربات"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.setup_logging()
    
    def setup_logging(self):
        """راه‌اندازی سیستم لاگینگ"""
        # ایجاد پوشه لاگ‌ها
        os.makedirs(self.log_dir, exist_ok=True)
        
        # تنظیم فرمت لاگ
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # لاگر اصلی
        self.logger = logging.getLogger('BotLogger')
        self.logger.setLevel(logging.INFO)
        
        # حذف handler های قبلی
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Handler برای فایل روزانه
        daily_handler = logging.handlers.TimedRotatingFileHandler(
            os.path.join(self.log_dir, 'bot.log'),
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        daily_handler.setFormatter(formatter)
        self.logger.addHandler(daily_handler)
        
        # Handler برای خطاها
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_dir, 'errors.log'),
            maxBytes=1024*1024,  # 1MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # Handler برای کنسول
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log_user_action(self, user_id, action, details=None):
        """
        ثبت اقدام کاربر
        
        پارامترها:
            user_id (int): شناسه کاربر
            action (str): نوع اقدام
            details (dict): جزئیات
        """
        message = f"USER_ACTION - User {user_id}: {action}"
        if details:
            message += f" - Details: {details}"
        
        self.logger.info(message)
    
    def log_error(self, error, context=None):
        """
        ثبت خطا
        
        پارامترها:
            error (Exception): خطا
            context (str): زمینه خطا
        """
        message = f"ERROR - {error}"
        if context:
            message += f" - Context: {context}"
        
        self.logger.error(message, exc_info=True)
    
    def log_api_call(self, method, url, status_code, response_time=None):
        """
        ثبت فراخوانی API
        
        پارامترها:
            method (str): روش HTTP
            url (str): آدرس
            status_code (int): کد وضعیت
            response_time (float): زمان پاسخ
        """
        message = f"API_CALL - {method} {url} - Status: {status_code}"
        if response_time:
            message += f" - Time: {response_time:.2f}s"
        
        if status_code >= 400:
            self.logger.error(message)
        else:
            self.logger.info(message)
    
    def log_registration(self, user_id, success, details=None):
        """
        ثبت فرآیند ثبت‌نام
        
        پارامترها:
            user_id (int): شناسه کاربر
            success (bool): موفقیت
            details (dict): جزئیات
        """
        status = "SUCCESS" if success else "FAILED"
        message = f"REGISTRATION - User {user_id} - {status}"
        if details:
            message += f" - Details: {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.warning(message)
    
    def log_payment(self, user_id, class_id, amount, success):
        """
        ثبت پرداخت
        
        پارامترها:
            user_id (int): شناسه کاربر
            class_id (str): شناسه کلاس
            amount (str): مبلغ
            success (bool): موفقیت
        """
        status = "SUCCESS" if success else "FAILED"
        message = f"PAYMENT - User {user_id} - Class {class_id} - Amount {amount} - {status}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.warning(message)
    
    def get_statistics(self):
        """
        دریافت آمار لاگ‌ها
        
        خروجی:
            dict: آمار لاگ‌ها
        """
        stats = {
            'total_users': len(registered_users),
            'active_sessions': len(user_states),
            'total_classes': len(CLASSES),
            'log_files': []
        }
        
        # شمارش فایل‌های لاگ
        if os.path.exists(self.log_dir):
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(self.log_dir, filename)
                    stats['log_files'].append({
                        'name': filename,
                        'size': os.path.getsize(filepath),
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath))
                    })
        
        return stats

def create_logger():
    """ایجاد نمونه لاگر"""
    return BotLogger()

# ایجاد لاگر جهانی
bot_logger = create_logger()

def log_message_processing(message, success=True, error=None):
    """
    ثبت پردازش پیام
    
    پارامترها:
        message (dict): پیام
        success (bool): موفقیت
        error (Exception): خطا
    """
    if 'message' in message:
        chat_id = message['message']['chat']['id']
        user_id = message['message']['from']['id']
        text = message['message'].get('text', '')
        
        if success:
            bot_logger.log_user_action(user_id, f"Message sent: {text[:50]}...")
        else:
            bot_logger.log_error(error, f"Message processing failed for user {user_id}")

def log_callback_processing(callback_data, user_id, success=True):
    """
    ثبت پردازش callback
    
    پارامترها:
        callback_data (str): داده callback
        user_id (int): شناسه کاربر
        success (bool): موفقیت
    """
    if success:
        bot_logger.log_user_action(user_id, f"Callback processed: {callback_data}")
    else:
        bot_logger.log_error(Exception(f"Callback processing failed"), f"User {user_id}, Data: {callback_data}")

print("✅ تمرین 18: سیستم ثبت گزارش تکمیل شد!")

# تست لاگر
bot_logger.log_user_action(12345, "Test action", {"test": "data"})
bot_logger.log_error(Exception("Test error"), "Test context")

# تمرین: تابعی برای فیلتر کردن لاگ‌ها بنویسید
# تمرین: تابعی برای جستجو در لاگ‌ها بنویسید
# تمرین: تابعی برای پاکسازی لاگ‌های قدیمی بنویسید