 """
تمرین 3: توابع پایه
سطح: مبتدی
هدف: آشنایی با تعریف و استفاده از توابع
"""

def create_keyboard(buttons, is_inline=True, resize_keyboard=True, one_time_keyboard=False):
    """
    ایجاد کیبورد برای دکمه‌های پاسخ
    
    پارامترها:
        buttons (list): لیستی از دکمه‌ها
        is_inline (bool): اگر True باشد، کیبورد اینلاین ایجاد می‌شود
        resize_keyboard (bool): تغییر اندازه کیبورد
        one_time_keyboard (bool): پنهان شدن کیبورد پس از استفاده
    
    خروجی:
        dict: ساختار JSON برای کیبورد
    """
    if is_inline:
        inline_keyboard_buttons = []
        for row in buttons:
            row_buttons = []
            for button in row:
                button_data = {"text": button["text"]}
                if "callback_data" in button:
                    button_data["callback_data"] = button["callback_data"]
                if "request_contact" in button:
                    button_data["request_contact"] = button["request_contact"]
                row_buttons.append(button_data)
            inline_keyboard_buttons.append(row_buttons)
        return {"inline_keyboard": inline_keyboard_buttons}
    else:
        keyboard_buttons = []
        for row in buttons:
            row_buttons = []
            for button in row:
                button_data = {"text": button["text"]}
                if "request_contact" in button:
                    button_data["request_contact"] = button["request_contact"]
                row_buttons.append(button_data)
            keyboard_buttons.append(row_buttons)
        return {"keyboard": keyboard_buttons, "resize_keyboard": resize_keyboard, "one_time_keyboard": one_time_keyboard}

def send_message(chat_id, text, reply_markup=None):
    """
    ارسال پیام به کاربر
    
    پارامترها:
        chat_id (int): شناسه چت
        text (str): متن پیام
        reply_markup (dict): کیبورد پاسخ
    """
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    # در اینجا باید درخواست HTTP ارسال شود
    # فعلاً فقط چاپ می‌کنیم
    print(f"📤 ارسال پیام به {chat_id}: {text}")
    if reply_markup:
        print(f"🔘 کیبورد: {reply_markup}")

def get_simple_name(user):
    """
    دریافت نام ساده کاربر
    
    پارامترها:
        user (dict): اطلاعات کاربر
    
    خروجی:
        str: نام کاربر
    """
    if 'first_name' in user and user['first_name']:
        return user['first_name']
    elif 'username' in user and user['username']:
        return user['username']
    else:
        return "کاربر"

print("✅ تمرین 3: توابع پایه تکمیل شد!")

# تست توابع
test_user = {"first_name": "علی", "username": "ali_user"}
print(f"👤 نام کاربر: {get_simple_name(test_user)}")

test_buttons = [
    [{"text": "دکمه 1", "callback_data": "btn1"}],
    [{"text": "دکمه 2", "callback_data": "btn2"}]
]
keyboard = create_keyboard(test_buttons)
print(f"🔘 کیبورد ایجاد شده: {keyboard}")

# تمرین: تابع جدیدی برای محاسبه قیمت کلاس ایجاد کنید
# تمرین: تابعی برای بررسی اعتبار شماره تلفن بنویسید
# تمرین: تابعی برای تولید پیام خوش‌آمدگویی بنویسید