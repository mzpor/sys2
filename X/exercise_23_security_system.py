 """
تمرین 23: سیستم امنیت
سطح: پیشرفته
هدف: آشنایی با مفاهیم امنیت
"""

import hashlib
import hmac
import secrets
import time
from typing import Dict, List, Optional

class SecurityManager:
    """مدیریت امنیت ربات"""
    
    def __init__(self):
        self.secret_key = secrets.token_hex(32)
        self.rate_limits = {}
        self.blocked_users = set()
        self.suspicious_activities = []
    
    def generate_token(self, user_id: int, expires_in: int = 3600) -> str:
        """
        تولید توکن امن
        
        پارامترها:
            user_id (int): شناسه کاربر
            expires_in (int): مدت اعتبار (ثانیه)
        
        خروجی:
            str: توکن تولید شده
        """
        timestamp = int(time.time())
        expires_at = timestamp + expires_in
        
        # ترکیب داده‌ها
        data = f"{user_id}:{expires_at}"
        
        # تولید امضای HMAC
        signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # ترکیب نهایی
        token = f"{data}:{signature}"
        return token
    
    def verify_token(self, token: str) -> Optional[int]:
        """
        تایید توکن
        
        پارامترها:
            token (str): توکن برای تایید
        
        خروجی:
            int: شناسه کاربر یا None
        """
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return None
            
            user_id, expires_at, signature = parts
            user_id = int(user_id)
            expires_at = int(expires_at)
            
            # بررسی انقضا
            if time.time() > expires_at:
                return None
            
            # تایید امضا
            data = f"{user_id}:{expires_at}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                return user_id
            
            return None
        
        except (ValueError, TypeError):
            return None
    
    def check_rate_limit(self, user_id: int, action: str, limit: int = 10, window: int = 60) -> bool:
        """
        بررسی محدودیت نرخ
        
        پارامترها:
            user_id (int): شناسه کاربر
            action (str): نوع اقدام
            limit (int): حداکثر تعداد مجاز
            window (int): پنجره زمانی (ثانیه)
        
        خروجی:
            bool: True اگر مجاز باشد
        """
        current_time = time.time()
        key = f"{user_id}:{action}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # حذف رکوردهای قدیمی
        self.rate_limits[key] = [
            timestamp for timestamp in self.rate_limits[key]
            if current_time - timestamp < window
        ]
        
        # بررسی محدودیت
        if len(self.rate_limits[key]) >= limit:
            return False
        
        # اضافه کردن رکورد جدید
        self.rate_limits[key].append(current_time)
        return True
    
    def is_user_blocked(self, user_id: int) -> bool:
        """
        بررسی مسدودیت کاربر
        
        پارامترها:
            user_id (int): شناسه کاربر
        
        خروجی:
            bool: True اگر کاربر مسدود باشد
        """
        return user_id in self.blocked_users
    
    def block_user(self, user_id: int, reason: str = "Unknown"):
        """
        مسدود کردن کاربر
        
        پارامترها:
            user_id (int): شناسه کاربر
            reason (str): دلیل مسدودیت
        """
        self.blocked_users.add(user_id)
        self.log_suspicious_activity(user_id, f"User blocked: {reason}")
    
    def unblock_user(self, user_id: int):
        """
        رفع مسدودیت کاربر
        
        پارامترها:
            user_id (int): شناسه کاربر
        """
        self.blocked_users.discard(user_id)
    
    def log_suspicious_activity(self, user_id: int, activity: str):
        """
        ثبت فعالیت مشکوک
        
        پارامترها:
            user_id (int): شناسه کاربر
            activity (str): توضیح فعالیت
        """
        self.suspicious_activities.append({
            'user_id': user_id,
            'activity': activity,
            'timestamp': time.time()
        })
    
    def validate_input(self, text: str, max_length: int = 1000) -> bool:
        """
        اعتبارسنجی ورودی
        
        پارامترها:
            text (str): متن ورودی
            max_length (int): حداکثر طول مجاز
        
        خروجی:
            bool: True اگر ورودی معتبر باشد
        """
        if not text or len(text) > max_length:
            return False
        
        # بررسی کاراکترهای خطرناک
        dangerous_patterns = [
            '<script>', 'javascript:', 'data:text/html',
            'vbscript:', 'onload=', 'onerror='
        ]
        
        text_lower = text.lower()
        for pattern in dangerous_patterns:
            if pattern in text_lower:
                return False
        
        return True
    
    def sanitize_filename(self, filename: str) -> str:
        """
        پاکسازی نام فایل
        
        پارامترها:
            filename (str): نام فایل
        
        خروجی:
            str: نام فایل پاک شده
        """
        import re
        
        # حذف کاراکترهای خطرناک
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # محدود کردن طول
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename
    
    def check_admin_permission(self, user_id: int, required_permission: str = "admin") -> bool:
        """
        بررسی دسترسی ادمین
        
        پارامترها:
            user_id (int): شناسه کاربر
            required_permission (str): دسترسی مورد نیاز
        
        خروجی:
            bool: True اگر کاربر دسترسی داشته باشد
        """
        # در اینجا باید با پایگاه داده یا فایل تنظیمات بررسی شود
        admin_ids = [12345, 67890]  # مثال
        return user_id in admin_ids
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        رمزگذاری داده‌های حساس
        
        پارامترها:
            data (str): داده برای رمزگذاری
        
        خروجی:
            str: داده رمزگذاری شده
        """
        # استفاده از HMAC برای رمزگذاری ساده
        return hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def get_security_report(self) -> Dict:
        """
        دریافت گزارش امنیت
        
        خروجی:
            dict: گزارش امنیت
        """
        return {
            'blocked_users_count': len(self.blocked_users),
            'suspicious_activities_count': len(self.suspicious_activities),
            'rate_limits_count': len(self.rate_limits),
            'recent_suspicious_activities': self.suspicious_activities[-10:] if self.suspicious_activities else []
        }

# ایجاد نمونه مدیر امنیت
security_manager = SecurityManager()

def secure_message_processing(message: dict) -> bool:
    """
    پردازش امن پیام
    
    پارامترها:
        message (dict): پیام دریافتی
    
    خروجی:
        bool: True اگر پیام امن باشد
    """
    if 'message' not in message:
        return False
    
    user_id = message['message']['from']['id']
    text = message['message'].get('text', '')
    
    # بررسی مسدودیت
    if security_manager.is_user_blocked(user_id):
        print(f"🚫 کاربر {user_id} مسدود است")
        return False
    
    # بررسی محدودیت نرخ
    if not security_manager.check_rate_limit(user_id, 'message'):
        print(f"⚠️ کاربر {user_id} محدودیت نرخ دارد")
        security_manager.log_suspicious_activity(user_id, "Rate limit exceeded")
        return False
    
    # اعتبارسنجی ورودی
    if not security_manager.validate_input(text):
        print(f"⚠️ ورودی نامعتبر از کاربر {user_id}")
        security_manager.log_suspicious_activity(user_id, "Invalid input")
        return False
    
    return True

def secure_callback_processing(callback_query: dict) -> bool:
    """
    پردازش امن callback
    
    پارامترها:
        callback_query (dict): callback دریافتی
    
    خروجی:
        bool: True اگر callback امن باشد
    """
    user_id = callback_query['from']['id']
    data = callback_query.get('data', '')
    
    # بررسی مسدودیت
    if security_manager.is_user_blocked(user_id):
        return False
    
    # بررسی محدودیت نرخ
    if not security_manager.check_rate_limit(user_id, 'callback'):
        security_manager.log_suspicious_activity(user_id, "Callback rate limit exceeded")
        return False
    
    # اعتبارسنجی داده callback
    if not security_manager.validate_input(data, max_length=100):
        security_manager.log_suspicious_activity(user_id, "Invalid callback data")
        return False
    
    return True

print("✅ تمرین 23: سیستم امنیت تکمیل شد!")

# تمرین: تابعی برای تشخیص حملات بنویسید
# تمرین: تابعی برای مدیریت جلسات امن بنویسید
# تمرین: تابعی برای رمزگذاری پیشرفته بنویسید