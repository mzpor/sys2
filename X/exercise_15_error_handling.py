 """
تمرین 15: مدیریت خطاها
سطح: متوسط
هدف: آشنایی با مدیریت خطاها و استثناها
"""

import logging
import traceback

def safe_api_call(func, *args, **kwargs):
    """
    اجرای ایمن توابع API
    
    پارامترها:
        func (function): تابع مورد نظر
        *args: آرگومان‌های تابع
        **kwargs: آرگومان‌های کلیدی تابع
    
    خروجی:
        result: نتیجه تابع یا None در صورت خطا
    """
    try:
        return func(*args, **kwargs)
    except requests.exceptions.RequestException as e:
        logging.error(f"خطای شبکه در {func.__name__}: {e}")
        return None
    except Exception as e:
        logging.error(f"خطای غیرمنتظره در {func.__name__}: {e}")
        return None

def handle_message_safely(message):
    """
    پردازش ایمن پیام‌ها
    
    پارامترها:
        message (dict): پیام دریافتی
    """
    try:
        process_message(message)
    except Exception as e:
        logging.error(f"خطا در پردازش پیام: {e}")
        logging.error(traceback.format_exc())
        
        # ارسال پیام خطا به کاربر
        if 'message' in message:
            chat_id = message['message']['chat']['id']
            send_message(chat_id, "متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید.")

def handle_callback_safely(message):
    """
    پردازش ایمن callback ها
    
    پارامترها:
        message (dict): پیام callback
    """
    try:
        handle_callback_query(message)
    except Exception as e:
        logging.error(f"خطا در پردازش callback: {e}")
        logging.error(traceback.format_exc())
        
        # ارسال پیام خطا به کاربر
        if 'callback_query' in message:
            chat_id = message['callback_query']['message']['chat']['id']
            send_message(chat_id, "متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید.")

def validate_user_input(input_type, value):
    """
    اعتبارسنجی ورودی کاربر
    
    پارامترها:
        input_type (str): نوع ورودی
        value (str): مقدار ورودی
    
    خروجی:
        tuple: (is_valid, error_message)
    """
    if input_type == 'name':
        if len(value.strip()) < 2:
            return False, "نام باید حداقل 2 کاراکتر باشد."
        if len(value.split()) < 2:
            return False, "لطفاً نام و نام خانوادگی را وارد کنید."
        return True, ""
    
    elif input_type == 'phone':
        if not value.startswith('09'):
            return False, "شماره تلفن باید با 09 شروع شود."
        if len(value) != 11:
            return False, "شماره تلفن باید 11 رقم باشد."
        if not value[2:].isdigit():
            return False, "شماره تلفن باید فقط شامل اعداد باشد."
        return True, ""
    
    elif input_type == 'national_id':
        if len(value) != 10:
            return False, "کد ملی باید 10 رقم باشد."
        if not value.isdigit():
            return False, "کد ملی باید فقط شامل اعداد باشد."
        return True, ""
    
    return True, ""

def retry_on_failure(func, max_retries=3, delay=1):
    """
    تلاش مجدد در صورت شکست
    
    پارامترها:
        func (function): تابع مورد نظر
        max_retries (int): حداکثر تعداد تلاش‌ها
        delay (int): تاخیر بین تلاش‌ها (ثانیه)
    
    خروجی:
        result: نتیجه تابع یا None
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            logging.warning(f"تلاش {attempt + 1} از {max_retries} ناموفق: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    
    logging.error(f"تابع {func.__name__} پس از {max_retries} تلاش ناموفق بود.")
    return None

def log_user_action(user_id, action, details=None):
    """
    ثبت اقدامات کاربر
    
    پارامترها:
        user_id (int): شناسه کاربر
        action (str): نوع اقدام
        details (dict): جزئیات اقدام
    """
    log_entry = {
        'user_id': user_id,
        'action': action,
        'timestamp': time.time(),
        'details': details or {}
    }
    
    logging.info(f"کاربر {user_id}: {action}")
    if details:
        logging.debug(f"جزئیات: {details}")

def handle_file_errors():
    """
    مدیریت خطاهای فایل
    """
    try:
        load_users_from_file()
    except FileNotFoundError:
        logging.warning("فایل کاربران یافت نشد. شروع با لیست خالی.")
    except json.JSONDecodeError as e:
        logging.error(f"خطا در خواندن فایل کاربران: {e}")
        # پشتیبان‌گیری از فایل خراب
        backup_filename = f"users_backup_{int(time.time())}.json"
        try:
            import shutil
            shutil.copy("users.json", backup_filename)
            logging.info(f"فایل پشتیبان ایجاد شد: {backup_filename}")
        except Exception as backup_error:
            logging.error(f"خطا در ایجاد پشتیبان: {backup_error}")

print("✅ تمرین 15: مدیریت خطاها تکمیل شد!")

# تمرین: تابعی برای بررسی سلامت سیستم بنویسید
# تمرین: تابعی برای بازیابی از خطا بنویسید
# تمرین: تابعی برای گزارش‌گیری خطاها بنویسید