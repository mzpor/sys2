 """
تمرین 9: سیستم ثبت‌نام
سطح: متوسط
هدف: آشنایی با فرآیند ثبت‌نام
"""

def start_registration(chat_id, user_id):
    """
    شروع فرآیند ثبت‌نام
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
    """
    if user_id in user_states and user_states[user_id].get('step') == 'waiting_name_lastname':
        return  # قبلاً درخواست شده
    
    user_states[user_id] = {'step': 'waiting_name_lastname'}
    send_message(chat_id, "نام و نام خانوادگی مثال: محمدی علی).")

def start_name_registration(chat_id, user_id):
    """
    شروع ثبت نام با درخواست نام
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
    """
    user_states[user_id] = {'step': 'waiting_name_lastname'}
    send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: محمدی محمد):")

def show_name_confirmation(chat_id, user_id, first_name, last_name):
    """
    نمایش تایید نام و درخواست شماره تلفن
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
        first_name (str): نام
        last_name (str): نام خانوادگی
    """
    bottom_keyboard = {
        "keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    
    full_name = f"{first_name} {last_name}".strip()
    message_text = f"نام و فامیل: {full_name}\n\nلطفاً شماره تلفن خود را ارسال کنید:"
    
    send_message(chat_id, message_text, reply_markup=bottom_keyboard)
    
    inline_buttons = [
        [{'text': '✏️ تصحیح نام', 'callback_data': 'edit_name'}]
    ]
    inline_keyboard = create_keyboard(inline_buttons, is_inline=True)
    send_message(chat_id, "", reply_markup=inline_keyboard)

def show_phone_input_request(chat_id, user_id):
    """
    درخواست شماره تلفن با دکمه‌های پایین
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
    """
    keyboard = create_keyboard([
        [{'text': '📱 ارسال شماره تلفن', 'request_contact': True}]
    ], is_inline=False)
    send_message(chat_id, "لطفاً شماره تلفن خود را ارسال کنید:", reply_markup=keyboard)

print("✅ تمرین 9: سیستم ثبت‌نام تکمیل شد!")

# تمرین: تابعی برای اعتبارسنجی نام بنویسید
# تمرین: تابعی برای اعتبارسنجی شماره تلفن بنویسید
# تمرین: تابعی برای ذخیره اطلاعات کاربر بنویسید