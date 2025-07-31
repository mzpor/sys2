"""
تمرین 7: توابع ادمین
سطح: متوسط
هدف: آشنایی با مدیریت ادمین‌ها
"""

def is_admin(user_id, chat_id):
    """
    بررسی اینکه آیا کاربر ادمین گروه است یا نه
    
    پارامترها:
        user_id (int): شناسه کاربر
        chat_id (int): شناسه گروه
    
    خروجی:
        bool: True اگر کاربر ادمین باشد
    """
    try:
        administrators = get_chat_administrators(chat_id)
        admin_ids = {admin_info.get('user', {}).get('id') for admin_info in administrators}
        return user_id in admin_ids
    except Exception as e:
        print(f"❌ خطا در بررسی ادمین: {e}")
        return False

def get_admin_list(chat_id):
    """
    دریافت لیست ادمین‌های گروه
    
    پارامترها:
        chat_id (int): شناسه گروه
    
    خروجی:
        list: لیست ادمین‌ها
    """
    try:
        administrators = get_chat_administrators(chat_id)
        admin_list = []
        for admin in administrators:
            user = admin.get('user', {})
            admin_list.append({
                'id': user.get('id'),
                'name': get_simple_name(user),
                'status': admin.get('status')
            })
        return admin_list
    except Exception as e:
        print(f"❌ خطا در دریافت لیست ادمین‌ها: {e}")
        return []

def check_admin_permissions(user_id, chat_id, required_permission="administrator"):
    """
    بررسی دسترسی‌های ادمین
    
    پارامترها:
        user_id (int): شناسه کاربر
        chat_id (int): شناسه گروه
        required_permission (str): دسترسی مورد نیاز
    
    خروجی:
        bool: True اگر کاربر دسترسی داشته باشد
    """
    try:
        administrators = get_chat_administrators(chat_id)
        for admin in administrators:
            if admin.get('user', {}).get('id') == user_id:
                return admin.get('status') == required_permission
        return False
    except Exception as e:
        print(f"❌ خطا در بررسی دسترسی‌ها: {e}")
        return False

print("✅ تمرین 7: توابع ادمین تکمیل شد!")

# تست توابع
print("👑 توابع ادمین آماده هستند!")
print("🔐 برای تست واقعی، نیاز به گروه و ادمین است")

# تمرین: تابعی برای ارتقای کاربر به ادمین بنویسید
# تمرین: تابعی برای حذف ادمین بنویسید
# تمرین: تابعی برای بررسی دسترسی‌های خاص بنویسید