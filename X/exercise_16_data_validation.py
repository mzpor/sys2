"""
تمرین 16: اعتبارسنجی داده‌ها
سطح: متوسط
هدف: آشنایی با اعتبارسنجی و پاکسازی داده‌ها
"""

import re

def validate_name(name):
    """
    اعتبارسنجی نام
    
    پارامترها:
        name (str): نام وارد شده
    
    خروجی:
        tuple: (is_valid, cleaned_name, error_message)
    """
    if not name or not name.strip():
        return False, "", "نام نمی‌تواند خالی باشد."
    
    # حذف فاصله‌های اضافی
    cleaned_name = ' '.join(name.strip().split())
    
    if len(cleaned_name) < 2:
        return False, "", "نام باید حداقل 2 کاراکتر باشد."
    
    if len(cleaned_name) > 50:
        return False, "", "نام نمی‌تواند بیش از 50 کاراکتر باشد."
    
    # بررسی کاراکترهای مجاز (فارسی، انگلیسی، فاصله)
    if not re.match(r'^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z\s]+$', cleaned_name):
        return False, "", "نام باید شامل حروف فارسی یا انگلیسی باشد."
    
    return True, cleaned_name, ""

def validate_phone(phone):
    """
    اعتبارسنجی شماره تلفن
    
    پارامترها:
        phone (str): شماره تلفن
    
    خروجی:
        tuple: (is_valid, cleaned_phone, error_message)
    """
    if not phone:
        return False, "", "شماره تلفن نمی‌تواند خالی باشد."
    
    # حذف کاراکترهای غیر عددی
    cleaned_phone = re.sub(r'[^\d]', '', phone)
    
    if len(cleaned_phone) != 11:
        return False, "", "شماره تلفن باید 11 رقم باشد."
    
    if not cleaned_phone.startswith('09'):
        return False, "", "شماره تلفن باید با 09 شروع شود."
    
    return True, cleaned_phone, ""

def validate_national_id(national_id):
    """
    اعتبارسنجی کد ملی
    
    پارامترها:
        national_id (str): کد ملی
    
    خروجی:
        tuple: (is_valid, cleaned_id, error_message)
    """
    if not national_id:
        return False, "", "کد ملی نمی‌تواند خالی باشد."
    
    # حذف کاراکترهای غیر عددی
    cleaned_id = re.sub(r'[^\d]', '', national_id)
    
    if len(cleaned_id) != 10:
        return False, "", "کد ملی باید 10 رقم باشد."
    
    # بررسی الگوریتم کد ملی
    if not is_valid_national_id_algorithm(cleaned_id):
        return False, "", "کد ملی نامعتبر است."
    
    return True, cleaned_id, ""

def is_valid_national_id_algorithm(national_id):
    """
    بررسی الگوریتم کد ملی
    
    پارامترها:
        national_id (str): کد ملی
    
    خروجی:
        bool: True اگر کد ملی معتبر باشد
    """
    if len(national_id) != 10:
        return False
    
    # تبدیل به لیست اعداد
    digits = [int(d) for d in national_id]
    
    # محاسبه کنترل
    control_digit = digits[9]
    sum_digits = 0
    
    for i in range(9):
        sum_digits += digits[i] * (10 - i)
    
    remainder = sum_digits % 11
    
    if remainder < 2:
        return control_digit == remainder
    else:
        return control_digit == (11 - remainder)

def validate_class_id(class_id):
    """
    اعتبارسنجی شناسه کلاس
    
    پارامترها:
        class_id (str): شناسه کلاس
    
    خروجی:
        bool: True اگر کلاس وجود داشته باشد
    """
    return class_id in CLASSES

def validate_payment_amount(amount):
    """
    اعتبارسنجی مبلغ پرداخت
    
    پارامترها:
        amount (str): مبلغ
    
    خروجی:
        tuple: (is_valid, cleaned_amount, error_message)
    """
    if not amount:
        return False, "", "مبلغ نمی‌تواند خالی باشد."
    
    # حذف کاراکترهای غیر عددی
    cleaned_amount = re.sub(r'[^\d]', '', amount)
    
    if not cleaned_amount.isdigit():
        return False, "", "مبلغ باید عدد باشد."
    
    amount_int = int(cleaned_amount)
    
    if amount_int <= 0:
        return False, "", "مبلغ باید بزرگتر از صفر باشد."
    
    if amount_int > 10000000:  # 10 میلیون تومان
        return False, "", "مبلغ نمی‌تواند بیش از 10 میلیون تومان باشد."
    
    return True, str(amount_int), ""

def sanitize_text(text):
    """
    پاکسازی متن از کاراکترهای خطرناک
    
    پارامترها:
        text (str): متن ورودی
    
    خروجی:
        str: متن پاک شده
    """
    if not text:
        return ""
    
    # حذف کاراکترهای خطرناک
    dangerous_chars = ['<', '>', '&', '"', "'"]
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # حذف فاصله‌های اضافی
    text = ' '.join(text.split())
    
    return text

def validate_user_data(user_data):
    """
    اعتبارسنجی کامل داده‌های کاربر
    
    پارامترها:
        user_data (dict): داده‌های کاربر
    
    خروجی:
        tuple: (is_valid, cleaned_data, errors)
    """
    errors = []
    cleaned_data = {}
    
    # اعتبارسنجی نام
    if 'first_name' in user_data and 'last_name' in user_data:
        full_name = f"{user_data['first_name']} {user_data['last_name']}"
        is_valid, cleaned_name, error = validate_name(full_name)
        if is_valid:
            name_parts = cleaned_name.split()
            cleaned_data['first_name'] = name_parts[0]
            cleaned_data['last_name'] = ' '.join(name_parts[1:])
        else:
            errors.append(f"نام: {error}")
    
    # اعتبارسنجی تلفن
    if 'mobile' in user_data:
        is_valid, cleaned_phone, error = validate_phone(user_data['mobile'])
        if is_valid:
            cleaned_data['mobile'] = cleaned_phone
        else:
            errors.append(f"تلفن: {error}")
    
    # اعتبارسنجی کد ملی
    if 'national_id' in user_data:
        is_valid, cleaned_id, error = validate_national_id(user_data['national_id'])
        if is_valid:
            cleaned_data['national_id'] = cleaned_id
        else:
            errors.append(f"کد ملی: {error}")
    
    # اعتبارسنجی کلاس
    if 'registered_class' in user_data:
        if validate_class_id(user_data['registered_class']):
            cleaned_data['registered_class'] = user_data['registered_class']
        else:
            errors.append("کلاس انتخابی نامعتبر است.")
    
    return len(errors) == 0, cleaned_data, errors

print("✅ تمرین 16: اعتبارسنجی داده‌ها تکمیل شد!")

# تست توابع
test_names = ["علی محمدی", "Ali Mohammadi", "ع", "123", ""]
for name in test_names:
    is_valid, cleaned, error = validate_name(name)
    print(f"نام '{name}': {'✅ معتبر' if is_valid else '❌ نامعتبر'} - {error}")

# تمرین: تابعی برای اعتبارسنجی ایمیل بنویسید
# تمرین: تابعی برای اعتبارسنجی تاریخ تولد بنویسید
# تمرین: تابعی برای اعتبارسنجی آدرس بنویسید