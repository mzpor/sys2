import json
import os
import logging

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """بارگذاری کانفیگ از فایل"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"خطا در بارگذاری کانفیگ: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """دریافت کانفیگ پیش‌فرض"""
        return {
            "bot_token": "",
            "admin_id": "",
            "teacher_ids": [],
            "data_file": "room_data.json",
            "attendance_days": ["Thursday"],
            "welcome_message": "🎉 به ربات مدیریت روم خوش آمدید!"
        }
    
    def save_config(self):
        """ذخیره کانفیگ در فایل"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logging.error(f"خطا در ذخیره کانفیگ: {e}")
            return False
    
    def update_config(self, key, value):
        """به‌روزرسانی یک مقدار در کانفیگ"""
        self.config[key] = value
        return self.save_config()
    
    def add_teacher(self, teacher_id):
        """افزودن مربی جدید"""
        if teacher_id not in self.config.get("teacher_ids", []):
            if "teacher_ids" not in self.config:
                self.config["teacher_ids"] = []
            self.config["teacher_ids"].append(teacher_id)
            return self.save_config()
        return True
    
    def remove_teacher(self, teacher_id):
        """حذف مربی"""
        if "teacher_ids" in self.config and teacher_id in self.config["teacher_ids"]:
            self.config["teacher_ids"].remove(teacher_id)
            return self.save_config()
        return True
    
    def add_attendance_day(self, day):
        """افزودن روز حضور و غیاب"""
        if day not in self.config.get("attendance_days", []):
            if "attendance_days" not in self.config:
                self.config["attendance_days"] = []
            self.config["attendance_days"].append(day)
            return self.save_config()
        return True
    
    def remove_attendance_day(self, day):
        """حذف روز حضور و غیاب"""
        if "attendance_days" in self.config and day in self.config["attendance_days"]:
            self.config["attendance_days"].remove(day)
            return self.save_config()
        return True

# مثال استفاده
if __name__ == "__main__":
    config_manager = ConfigManager()
    
    # تغییر توکن ربات
    config_manager.update_config("bot_token", "توکن_جدید")
    
    # افزودن مربی جدید
    config_manager.add_teacher("123456789")
    
    # افزودن روز حضور و غیاب
    config_manager.add_attendance_day("Friday")
    
    print("کانفیگ با موفقیت به‌روزرسانی شد!") 