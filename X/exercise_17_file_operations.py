 """
تمرین 17: عملیات فایل
سطح: متوسط
هدف: آشنایی با خواندن و نوشتن فایل‌ها
"""

import json
import os
import shutil
from datetime import datetime

def save_data_to_file(data, filename, backup=True):
    """
    ذخیره داده در فایل با پشتیبان‌گیری
    
    پارامترها:
        data (dict): داده‌های مورد نظر
        filename (str): نام فایل
        backup (bool): آیا پشتیبان تهیه شود
    """
    try:
        # ایجاد پشتیبان اگر فایل موجود باشد
        if backup and os.path.exists(filename):
            backup_filename = f"{filename}.backup.{int(time.time())}"
            shutil.copy2(filename, backup_filename)
            print(f"📦 پشتیبان ایجاد شد: {backup_filename}")
        
        # ذخیره داده
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ داده‌ها در {filename} ذخیره شد")
        return True
    
    except Exception as e:
        print(f"❌ خطا در ذخیره فایل {filename}: {e}")
        return False

def load_data_from_file(filename, default_data=None):
    """
    بارگذاری داده از فایل
    
    پارامترها:
        filename (str): نام فایل
        default_data: داده پیش‌فرض در صورت عدم وجود فایل
    
    خروجی:
        dict: داده‌های بارگذاری شده
    """
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ داده‌ها از {filename} بارگذاری شد")
            return data
        else:
            print(f"📝 فایل {filename} یافت نشد، استفاده از داده پیش‌فرض")
            return default_data or {}
    
    except json.JSONDecodeError as e:
        print(f"❌ خطا در خواندن فایل {filename}: {e}")
        return default_data or {}
    except Exception as e:
        print(f"❌ خطا در بارگذاری فایل {filename}: {e}")
        return default_data or {}

def save_users_to_file_enhanced():
    """
    ذخیره پیشرفته اطلاعات کاربران
    """
    # اضافه کردن متادیتا
    enhanced_data = {
        'users': registered_users,
        'metadata': {
            'last_updated': datetime.now().isoformat(),
            'total_users': len(registered_users),
            'version': '1.0'
        }
    }
    
    return save_data_to_file(enhanced_data, 'users_enhanced.json')

def load_users_from_file_enhanced():
    """
    بارگذاری پیشرفته اطلاعات کاربران
    """
    global registered_users
    
    data = load_data_from_file('users_enhanced.json')
    
    if 'users' in data:
        registered_users = data['users']
        metadata = data.get('metadata', {})
        print(f"📊 {len(registered_users)} کاربر بارگذاری شد")
        print(f"🕒 آخرین به‌روزرسانی: {metadata.get('last_updated', 'نامشخص')}")
    else:
        registered_users = data  # سازگاری با فرمت قدیمی

def export_users_to_csv():
    """
    صادر کردن اطلاعات کاربران به CSV
    """
    try:
        import csv
        
        filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['user_id', 'first_name', 'last_name', 'mobile', 'national_id', 'registered_class', 'registration_date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for user_id, user_data in registered_users.items():
                row = {
                    'user_id': user_id,
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'mobile': user_data.get('mobile', ''),
                    'national_id': user_data.get('national_id', ''),
                    'registered_class': user_data.get('registered_class', ''),
                    'registration_date': user_data.get('registration_date', '')
                }
                writer.writerow(row)
        
        print(f"📊 اطلاعات کاربران به {filename} صادر شد")
        return filename
    
    except Exception as e:
        print(f"❌ خطا در صادر کردن CSV: {e}")
        return None

def create_backup():
    """
    ایجاد پشتیبان از تمام فایل‌های مهم
    """
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # فایل‌های مهم
        important_files = ['users.json', 'users_enhanced.json']
        
        for filename in important_files:
            if os.path.exists(filename):
                shutil.copy2(filename, os.path.join(backup_dir, filename))
        
        # ذخیره وضعیت فعلی
        current_state = {
            'user_states': user_states,
            'known_members': known_members,
            'recitation_exercises': recitation_exercises,
            'exercise_scores': exercise_scores,
            'timestamp': datetime.now().isoformat()
        }
        
        state_filename = os.path.join(backup_dir, 'current_state.json')
        save_data_to_file(current_state, state_filename, backup=False)
        
        print(f"📦 پشتیبان کامل در {backup_dir} ایجاد شد")
        return backup_dir
    
    except Exception as e:
        print(f"❌ خطا در ایجاد پشتیبان: {e}")
        return None

def restore_from_backup(backup_dir):
    """
    بازیابی از پشتیبان
    
    پارامترها:
        backup_dir (str): مسیر پشتیبان
    """
    try:
        # بازیابی فایل‌های اصلی
        if os.path.exists(os.path.join(backup_dir, 'users_enhanced.json')):
            shutil.copy2(os.path.join(backup_dir, 'users_enhanced.json'), 'users_enhanced.json')
        
        # بازیابی وضعیت
        state_file = os.path.join(backup_dir, 'current_state.json')
        if os.path.exists(state_file):
            state_data = load_data_from_file(state_file)
            global user_states, known_members, recitation_exercises, exercise_scores
            
            user_states = state_data.get('user_states', {})
            known_members = state_data.get('known_members', {})
            recitation_exercises = state_data.get('recitation_exercises', {})
            exercise_scores = state_data.get('exercise_scores', {})
        
        print(f"✅ بازیابی از {backup_dir} تکمیل شد")
        return True
    
    except Exception as e:
        print(f"❌ خطا در بازیابی: {e}")
        return False

print("✅ تمرین 17: عملیات فایل تکمیل شد!")

# تمرین: تابعی برای فشرده‌سازی فایل‌ها بنویسید
# تمرین: تابعی برای بررسی فضای دیسک بنویسید
# تمرین: تابعی برای پاکسازی فایل‌های قدیمی بنویسید