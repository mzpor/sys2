"""
تمرین 8: سیستم منو
سطح: متوسط
هدف: آشنایی با ایجاد منوهای تعاملی
"""

def show_main_menu(chat_id, user_id):
    """
    نمایش منوی اصلی
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
    """
    if is_user_registered(user_id):
        # کاربر ثبت‌نام شده
        welcome_text = f"سلام {get_user_info(user_id).get('first_name', 'کاربر')} عزیز!\n\nبه ربات تلاوت خوش آمدید!"
        keyboard = create_keyboard([
            [{'text': '📚 کلاس جدید', 'callback_data': 'new_class_registration'}],
            [{'text': '👤 حساب کاربری', 'callback_data': 'user_account'}],
            [{'text': '📊 نظر سنجی', 'callback_data': 'survey'}],
            [{'text': 'ℹ️ درباره ربات', 'callback_data': 'about_bot'}]
        ])
    else:
        # کاربر جدید
        welcome_text = "به ربات تلاوت خوش آمدید!\n\nلطفاً برای شروع ثبت‌نام، روی دکمه زیر کلیک کنید."
        keyboard = create_keyboard([
            [{'text': '📚 ثبت نام در مدرسه', 'callback_data': 'school_registration'}],
            [{'text': 'ℹ️ درباره ربات', 'callback_data': 'about_bot'}]
        ])
    
    send_message(chat_id, welcome_text, reply_markup=keyboard)

def handle_user_account(chat_id, user_id):
    """
    مدیریت حساب کاربری
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
    """
    if is_user_registered(user_id):
        user_data = get_user_info(user_id)
        account_info = f"👤 اطلاعات حساب کاربری:\n\n"
        account_info += f"نام: {user_data.get('first_name', '')}\n"
        account_info += f"نام خانوادگی: {user_data.get('last_name', '')}\n"
        account_info += f"موبایل: {user_data.get('mobile', '')}\n"
        account_info += f"کد ملی: {user_data.get('national_id', '')}\n"
        account_info += f"کلاس ثبت شده: {CLASSES.get(user_data.get('registered_class', ''), {}).get('name', 'ثبت نشده')}"
        
        keyboard = create_keyboard([
            [{'text': '📚 کلاس جدید', 'callback_data': 'new_class_registration'}],
            [{'text': '✏️ تصحیح اطلاعات', 'callback_data': 'edit_user_info'}],
            [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
        ])
        send_message(chat_id, account_info, reply_markup=keyboard)
    else:
        keyboard = create_keyboard([
            [{'text': '📚 ثبت نام در مدرسه', 'callback_data': 'school_registration'}],
            [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
        ])
        send_message(chat_id, "شما هنوز ثبت نام نکرده‌اید. لطفاً ابتدا ثبت نام کنید.", reply_markup=keyboard)

def handle_survey(chat_id, user_id):
    """
    مدیریت نظر سنجی
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
    """
    survey_text = "📊 نظر سنجی ربات تلاوت\n\n"
    survey_text += "لطفاً نظر خود را درباره ربات به ما بگویید:\n"
    survey_text += "• کیفیت خدمات\n"
    survey_text += "• سهولت استفاده\n"
    survey_text += "• پیشنهادات بهبود"
    
    inline_buttons = [
        [{'text': '⭐ عالی', 'callback_data': 'survey_excellent'}],
        [{'text': '👍 خوب', 'callback_data': 'survey_good'}],
        [{'text': '👎 نیاز به بهبود', 'callback_data': 'survey_needs_improvement'}]
    ]
    inline_keyboard = create_keyboard(inline_buttons, is_inline=True)
    
    bottom_buttons = [
        [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
    ]
    bottom_keyboard = create_keyboard(bottom_buttons, is_inline=False)
    
    combined_keyboard = {
        "inline_keyboard": inline_keyboard.get("inline_keyboard", []),
        "keyboard": bottom_keyboard.get("keyboard", []),
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    
    send_message(chat_id, survey_text, reply_markup=combined_keyboard)

print("✅ تمرین 8: سیستم منو تکمیل شد!")

# تمرین: منوی جدید برای تنظیمات ایجاد کنید
# تمرین: منوی کمک و راهنما ایجاد کنید
# تمرین: منوی پروفایل کاربر ایجاد کنید