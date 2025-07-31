"""
تمرین 6: مدیریت کاربران
سطح: مبتدی
هدف: آشنایی با ذخیره و مدیریت اطلاعات کاربران
"""

import json
import os

def save_users_to_file():
    """
    ذخیره اطلاعات کاربران در فایل
    """
    try:
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(registered_users, f, ensure_ascii=False, indent=2)
        print("✅ اطلاعات کاربران ذخیره شد")
    except Exception as e:
        print(f"❌ خطا در ذخیره اطلاعات: {e}")

def load_users_from_file():
    """
    بارگذاری اطلاعات کاربران از فایل
    """
    global registered_users
    try:
        if os.path.exists("users.json"):
            with open("users.json", "r", encoding="utf-8") as f:
                registered_users = json.load(f)
            print(f"✅ {len(registered_users)} کاربر بارگذاری شد")
        else:
            print("📝 فایل کاربران یافت نشد، شروع با لیست خالی")
    except Exception as e:
        print(f"❌ خطا در بارگذاری اطلاعات: {e}")

def add_known_member(user_info, chat_id):
    """
    اضافه کردن عضو جدید به لیست اعضای گروه
    
    پارامترها:
        user_info (dict): اطلاعات کاربر
        chat_id (int): شناسه گروه
    """
    if chat_id not in known_members:
        known_members[chat_id] = {}
    
    user_id = user_info.get('id')
    if user_id not in known_members[chat_id]:
        known_members[chat_id][user_id] = {
            'name': get_simple_name(user_info),
            'id': user_id,
            'added_time': time.time()
        }
        print(f"👤 عضو جدید اضافه شد: {get_simple_name(user_info)}")

def is_user_registered(user_id):
    """
    بررسی اینکه آیا کاربر ثبت‌نام کرده است یا نه
    
    پارامترها:
        user_id (int): شناسه کاربر
    
    خروجی:
        bool: True اگر کاربر ثبت‌نام کرده باشد
    """
    return user_id in registered_users

def get_user_info(user_id):
    """
    دریافت اطلاعات کاربر
    
    پارامترها:
        user_id (int): شناسه کاربر
    
    خروجی:
        dict: اطلاعات کاربر یا None
    """
    return registered_users.get(user_id)

print("✅ تمرین 6: مدیریت کاربران تکمیل شد!")

# تست توابع
test_user = {"id": 12345, "first_name": "علی", "username": "ali_user"}
add_known_member(test_user, 67890)
print(f"👥 تعداد اعضای گروه: {len(known_members.get(67890, {}))}")

# تمرین: تابعی برای حذف کاربر از لیست بنویسید
# تمرین: تابعی برای به‌روزرسانی اطلاعات کاربر بنویسید
# تمرین: تابعی برای جستجوی کاربر بر اساس نام بنویسید