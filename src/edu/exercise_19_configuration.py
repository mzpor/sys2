 """
تمرین 19: مدیریت تنظیمات
سطح: متوسط
هدف: آشنایی با مدیریت تنظیمات و پیکربندی
"""

import json
import os
from typing import Dict, Any

class BotConfig:
    """کلاس مدیریت تنظیمات ربات"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_default_config()
        self.load_config()
    
    def load_default_config(self):
        """بارگذاری تنظیمات پیش‌فرض"""
        return {
            "bot": {
                "token": "YOUR_BOT_TOKEN",
                "name": "ربات تلاوت",
                "version": "1.0.0",
                "admin_ids": []
            },
            "database": {
                "users_file": "users.json",
                "backup_enabled": True,
                "backup_interval": 24  # ساعت
            },
            "classes": {
                "max_classes_per_user": 3,
                "registration_enabled": True,
                "payment_enabled": True
            },
            "exercises": {
                "enabled": True,
                "exercise_days": ["شنبه", "دوشنبه", "چهارشنبه"],
                "deadline_hours": 24
            },
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "console_enabled": True,
                "max_file_size": 1048576  # 1MB
            },
            "notifications": {
                "welcome_message": True,
                "exercise_reminder": True,
                "payment_reminder": True
            },
            "security": {
                "max_login_attempts": 3,
                "session_timeout": 3600,  # ثانیه
                "input_validation": True
            }
        }
    
    def load_config(self):
        """بارگذاری تنظیمات از فایل"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self.merge_config(file_config)
                print(f"✅ تنظیمات از {self.config_file} بارگذاری شد")
            else:
                self.save_config()
                print(f"📝 فایل تنظیمات جدید ایجاد شد: {self.config_file}")
        except Exception as e:
            print(f"❌ خطا در بارگذاری تنظیمات: {e}")
    
    def merge_config(self, new_config):
        """ادغام تنظیمات جدید با تنظیمات موجود"""
        def merge_dicts(base, update):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value
        
        merge_dicts(self.config, new_config)
    
    def save_config(self):
        """ذخیره تنظیمات در فایل"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"✅ تنظیمات در {self.config_file} ذخیره شد")
            return True
        except Exception as e:
            print(f"❌ خطا در ذخیره تنظیمات: {e}")
            return False
    
    def get(self, key_path, default=None):
        """
        دریافت مقدار تنظیمات
        
        پارامترها:
            key_path (str): مسیر کلید (مثال: "bot.token")
            default: مقدار پیش‌فرض
        
        خروجی:
            Any: مقدار تنظیمات
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path, value):
        """
        تنظیم مقدار
        
        پارامترها:
            key_path (str): مسیر کلید
            value: مقدار جدید
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def update_config(self, updates):
        """
        به‌روزرسانی تنظیمات
        
        پارامترها:
            updates (dict): تنظیمات جدید
        """
        self.merge_config(updates)
        self.save_config()
    
    def validate_config(self):
        """
        اعتبارسنجی تنظیمات
        
        خروجی:
            tuple: (is_valid, errors)
        """
        errors = []
        
        # بررسی توکن
        if not self.get("bot.token") or self.get("bot.token") == "YOUR_BOT_TOKEN":
            errors.append("توکن ربات تنظیم نشده است")
        
        # بررسی فایل‌های مهم
        users_file = self.get("database.users_file")
        if not users_file:
            errors.append("فایل کاربران تنظیم نشده است")
        
        # بررسی تنظیمات امنیت
        max_attempts = self.get("security.max_login_attempts")
        if not isinstance(max_attempts, int) or max_attempts <= 0:
            errors.append("تعداد تلاش‌های ورود نامعتبر است")
        
        return len(errors) == 0, errors
    
    def get_bot_info(self):
        """
        دریافت اطلاعات ربات
        
        خروجی:
            dict: اطلاعات ربات
        """
        return {
            "name": self.get("bot.name"),
            "version": self.get("bot.version"),
            "admin_count": len(self.get("bot.admin_ids", [])),
            "classes_enabled": self.get("classes.registration_enabled"),
            "exercises_enabled": self.get("exercises.enabled"),
            "logging_level": self.get("logging.level")
        }
    
    def export_config(self, filename=None):
        """
        صادر کردن تنظیمات
        
        پارامترها:
            filename (str): نام فایل خروجی
        """
        if not filename:
            filename = f"config_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"📤 تنظیمات به {filename} صادر شد")
            return filename
        except Exception as e:
            print(f"❌ خطا در صادر کردن تنظیمات: {e}")
            return None

# ایجاد نمونه تنظیمات
bot_config = BotConfig()

def get_config_value(key_path, default=None):
    """تابع کمکی برای دریافت تنظیمات"""
    return bot_config.get(key_path, default)

def set_config_value(key_path, value):
    """تابع کمکی برای تنظیم مقدار"""
    bot_config.set(key_path, value)
    bot_config.save_config()

print("✅ تمرین 19: مدیریت تنظیمات تکمیل شد!")

# تست تنظیمات
print(f"🤖 نام ربات: {get_config_value('bot.name')}")
print(f"📚 ثبت‌نام فعال: {get_config_value('classes.registration_enabled')}")
print(f"🏃‍♂️ تمرین فعال: {get_config_value('exercises.enabled')}")

# تمرین: تابعی برای اعتبارسنجی تنظیمات پیشرفته بنویسید
# تمرین: تابعی برای بازیابی تنظیمات پیش‌فرض بنویسید
# تمرین: تابعی برای مقایسه تنظیمات بنویسید