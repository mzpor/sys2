import os
import json
import time
import logging
import requests
import jdatetime
from modules.registration import RegistrationModule
from modules.admin import AdminModule
from modules.payment import PaymentModule
from modules.attendance import AttendanceModule
from modules.group_management import GroupManagementModule
from modules.teacher_management import TeacherManagementModule

# تنظیمات لاگینگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تنظیمات اصلی
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
DATA_FILE = "1.json"
PAYMENT_TOKEN = "WALLET-LIiCzxGZnCd58Obr"  # توکن تولید (برای تست: WALLET-TEST-1111111111111111)
GROUP_LINK = "ble.ir/join/Gah9cS9LzQ"

# لیست کاربران مجاز (مربیان)
AUTHORIZED_USER_IDS = [
    574330749,  # محمد زارع ۲
    2045777722,  # رایتل
    1114227010,  # محمد ۱
    1775811194,  # محرابی
]

# user_id مدیر
ADMIN_USER_ID = 1114227010

# دیکشنری برای ذخیره گروه‌ها و مربی‌ها
GROUP_TEACHERS = {}

# دیکشنری برای ذخیره اعضای گروه‌ها
GROUP_MEMBERS = {}

class SchoolBot:
    """کلاس اصلی ربات مدیریت آموزشگاه"""
    
    def __init__(self):
        """مقداردهی اولیه ربات"""
        self.bot_token = BOT_TOKEN
        self.base_url = BASE_URL
        self.data_file = DATA_FILE
        
        # ایجاد نمونه‌های ماژول‌های اصلی
        self.registration_module = RegistrationModule(BOT_TOKEN, BASE_URL, DATA_FILE)
        self.admin_module = AdminModule(BOT_TOKEN, BASE_URL, DATA_FILE)
        self.payment_module = PaymentModule(BOT_TOKEN, BASE_URL, PAYMENT_TOKEN, GROUP_LINK)
        
        # ایجاد نمونه‌های ماژول‌های مدیریت گروه
        self.attendance_module = AttendanceModule()
        self.group_management_module = GroupManagementModule(self.attendance_module)
        self.teacher_management_module = TeacherManagementModule(self, ADMIN_USER_ID, AUTHORIZED_USER_IDS)
        
        logger.info("ربات با موفقیت راه‌اندازی شد.")
        logger.info("ماژول‌های مدیریت گروه و حضور و غیاب فعال شدند.")
    
    def get_updates(self, offset=None):
        """دریافت آپدیت‌ها از API بله"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"timeout": 100}
            if offset:
                params["offset"] = offset
            response = requests.get(url, params=params)
            return response.json().get("result", [])
        except Exception as e:
            logger.error(f"خطا در دریافت آپدیت‌ها: {e}")
            return []
    
    def handle_message(self, message):
        """مدیریت پیام‌های دریافتی"""
        # ابتدا به ماژول ثبت‌نام ارسال می‌کنیم
        if self.registration_module.handle_message(message):
            return
        
        # اگر ماژول ثبت‌نام پردازش نکرد، به ماژول مدیریت ارسال می‌کنیم
        if self.admin_module.handle_message(message):
            return
        
        # اگر ماژول مدیریت هم پردازش نکرد، به ماژول پرداخت ارسال می‌کنیم
        if self.payment_module.handle_message(message):
            return
            
        # ماژول‌های مدیریت گروه و حضور و غیاب
        # بررسی ماژول مدیریت معلمان
        if self.teacher_management_module.handle_message(message):
            return
            
        # بررسی ماژول مدیریت گروه
        if self.group_management_module.handle_message(message):
            return
            
        # بررسی ماژول حضور و غیاب
        if self.attendance_module.handle_message(message):
            return
        
        # اگر هیچ ماژولی پردازش نکرد، پیام پیش‌فرض ارسال می‌کنیم
        chat_id = message["chat"]["id"]
        self.registration_module.send_message(chat_id, "متوجه نشدم! لطفاً از دکمه‌های موجود استفاده کنید.")
    
    def handle_callback(self, callback):
        """مدیریت کال‌بک‌های دریافتی"""
        # ابتدا به ماژول ثبت‌نام ارسال می‌کنیم
        if self.registration_module.handle_callback(callback):
            return
        
        # اگر ماژول ثبت‌نام پردازش نکرد، به ماژول مدیریت ارسال می‌کنیم
        if self.admin_module.handle_callback(callback):
            return
        
        # اگر ماژول مدیریت هم پردازش نکرد، به ماژول پرداخت ارسال می‌کنیم
        if self.payment_module.handle_callback(callback):
            return
            
        # ماژول‌های مدیریت گروه و حضور و غیاب
        # بررسی ماژول مدیریت معلمان
        if self.teacher_management_module.handle_callback(callback):
            return
            
        # بررسی ماژول مدیریت گروه
        if self.group_management_module.handle_callback(callback):
            return
            
        # بررسی ماژول حضور و غیاب
        if self.attendance_module.handle_callback(callback):
            return
    
    def handle_pre_checkout_query(self, pre_checkout_query):
        """مدیریت پیش‌پرداخت"""
        self.payment_module.handle_pre_checkout_query(pre_checkout_query)
    
    def run(self):
        """اجرای اصلی ربات"""
        logger.info("ربات در حال اجرا است...")
        offset = None
        
        while True:
            try:
                updates = self.get_updates(offset)
                for update in updates:
                    offset = update["update_id"] + 1
                    
                    if "message" in update:
                        self.handle_message(update["message"])
                    elif "callback_query" in update:
                        self.handle_callback(update["callback_query"])
                    elif "pre_checkout_query" in update:
                        self.handle_pre_checkout_query(update["pre_checkout_query"])
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"خطا در حلقه اصلی: {e}")
                time.sleep(5)

def main():
    """تابع اصلی برنامه"""
    bot = SchoolBot()
    bot.run()

if __name__ == "__main__":
    main()