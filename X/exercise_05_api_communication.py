 """
تمرین 5: ارتباط با API
سطح: مبتدی
هدف: آشنایی با ارسال درخواست‌های HTTP
"""

import requests
import time

def get_updates(offset=None):
    """
    دریافت آپدیت‌های جدید از تلگرام
    
    پارامترها:
        offset (int): شناسه آخرین آپدیت دریافت شده
    
    خروجی:
        dict: پاسخ API
    """
    try:
        params = {"offset": offset} if offset else {}
        response = requests.get(f"{BASE_URL}/getUpdates", params=params)
        return response.json()
    except Exception as e:
        print(f"❌ خطا در دریافت آپدیت‌ها: {e}")
        return {"result": []}

def send_message_api(chat_id, text, reply_markup=None):
    """
    ارسال پیام از طریق API
    
    پارامترها:
        chat_id (int): شناسه چت
        text (str): متن پیام
        reply_markup (dict): کیبورد پاسخ
    
    خروجی:
        dict: پاسخ API
    """
    try:
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        response = requests.post(f"{BASE_URL}/sendMessage", json=payload)
        return response.json()
    except Exception as e:
        print(f"❌ خطا در ارسال پیام: {e}")
        return None

def get_chat_administrators(chat_id):
    """
    دریافت لیست ادمین‌های گروه
    
    پارامترها:
        chat_id (int): شناسه گروه
    
    خروجی:
        list: لیست ادمین‌ها
    """
    try:
        response = requests.get(f"{BASE_URL}/getChatAdministrators", params={"chat_id": chat_id})
        return response.json().get("result", [])
    except Exception as e:
        print(f"❌ خطا در دریافت ادمین‌ها: {e}")
        return []

def get_chat_member_count(chat_id):
    """
    دریافت تعداد اعضای گروه
    
    پارامترها:
        chat_id (int): شناسه گروه
    
    خروجی:
        int: تعداد اعضا
    """
    try:
        response = requests.get(f"{BASE_URL}/getChatMemberCount", params={"chat_id": chat_id})
        return response.json().get("result", 0)
    except Exception as e:
        print(f"❌ خطا در دریافت تعداد اعضا: {e}")
        return 0

print("✅ تمرین 5: ارتباط با API تکمیل شد!")

# تست توابع (بدون ارسال درخواست واقعی)
print("🌐 توابع API آماده هستند!")
print("📡 برای تست واقعی، توکن معتبر نیاز است")

# تمرین: تابعی برای دریافت اطلاعات چت بنویسید
# تمرین: تابعی برای ارسال عکس بنویسید
# تمرین: تابعی برای ارسال فایل بنویسید