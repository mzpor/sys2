 """
تمرین 14: پردازش پیام‌ها
سطح: متوسط
هدف: آشنایی با پردازش انواع پیام‌ها
"""

def process_message(message):
    """
    پردازش پیام‌های دریافتی
    
    پارامترها:
        message (dict): پیام دریافتی
    """
    if 'message' not in message:
        return
    
    chat_id = message['message']['chat']['id']
    user_id = message['message']['from']['id']
    text = message['message'].get('text', '')
    
    print(f'{log1} ...received message from {chat_id} with: {text}')
    
    # پردازش دستورات
    if text == '/start':
        show_main_menu(chat_id, user_id)
        return
    
    elif text == '/help':
        show_help_menu(chat_id, user_id)
        return
    
    elif text == '/classes':
        show_classes(chat_id, user_id)
        return
    
    elif text == '/account':
        handle_user_account(chat_id, user_id)
        return
    
    # پردازش بر اساس وضعیت کاربر
    if user_id in user_states:
        current_step = user_states[user_id].get('step')
        
        if current_step == 'waiting_name_lastname':
            process_name_input(chat_id, user_id, text)
        
        elif current_step == 'waiting_phone_contact':
            process_phone_input(chat_id, user_id, text)
        
        elif current_step == 'waiting_national_id':
            process_national_id_input(chat_id, user_id, text)
        
        elif current_step == 'waiting_for_class_selection':
            # کاربر در حال انتخاب کلاس است
            send_message(chat_id, "لطفاً از دکمه‌های موجود استفاده کنید.")
        
        elif current_step == 'waiting_for_payment_link_request':
            # کاربر در حال پرداخت است
            send_message(chat_id, "لطفاً از دکمه‌های موجود استفاده کنید.")
        
        elif current_step == 'waiting_for_payment_confirmation':
            # کاربر در حال تایید پرداخت است
            send_message(chat_id, "لطفاً از دکمه‌های موجود استفاده کنید.")
    
    else:
        # کاربر جدید یا بدون وضعیت خاص
        send_message(chat_id, "لطفاً از منوی اصلی استفاده کنید یا /start را ارسال کنید.")

def process_name_input(chat_id, user_id, text):
    """
    پردازش ورودی نام
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
        text (str): متن وارد شده
    """
    if len(text.split()) < 2:
        send_message(chat_id, "لطفاً نام و نام خانوادگی را با فاصله وارد کنید (مثال: محمدی علی):")
        return
    
    name_parts = text.split()
    first_name = name_parts[0]
    last_name = ' '.join(name_parts[1:])
    
    if user_id not in user_states:
        user_states[user_id] = {}
    
    user_states[user_id]['first_name'] = first_name
    user_states[user_id]['last_name'] = last_name
    user_states[user_id]['step'] = 'waiting_phone_contact'
    
    show_phone_confirmation_with_buttons(chat_id, user_id, first_name, last_name, None)

def process_phone_input(chat_id, user_id, text):
    """
    پردازش ورودی شماره تلفن
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
        text (str): متن وارد شده
    """
    # اعتبارسنجی شماره تلفن
    if not text.startswith('09') or len(text) != 11 or not text[2:].isdigit():
        send_message(chat_id, "شماره تلفن نامعتبر است. لطفاً شماره صحیح وارد کنید (مثال: 09123456789):")
        return
    
    if user_id not in user_states:
        user_states[user_id] = {}
    
    user_states[user_id]['mobile'] = text
    user_states[user_id]['step'] = 'waiting_national_id'
    
    send_message(chat_id, "لطفاً کد ملی خود را وارد کنید (10 رقم):")

def process_national_id_input(chat_id, user_id, text):
    """
    پردازش ورودی کد ملی
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
        text (str): متن وارد شده
    """
    # اعتبارسنجی کد ملی
    if len(text) != 10 or not text.isdigit():
        send_message(chat_id, "کد ملی نامعتبر است. لطفاً 10 رقم وارد کنید:")
        return
    
    if user_id not in user_states:
        user_states[user_id] = {}
    
    user_states[user_id]['national_id'] = text
    user_states[user_id]['step'] = 'confirm_info'
    
    show_final_confirmation(chat_id, user_id, 
                           user_states[user_id].get('first_name', ''),
                           user_states[user_id].get('last_name', ''),
                           user_states[user_id].get('mobile', ''),
                           text)

def show_help_menu(chat_id, user_id):
    """
    نمایش منوی راهنما
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
    """
    help_text = """
📖 <b>راهنمای ربات تلاوت</b>

🔹 <b>دستورات اصلی:</b>
/start - شروع ربات
/help - نمایش این راهنما
/classes - مشاهده کلاس‌ها
/account - حساب کاربری

🔹 <b>مراحل ثبت‌نام:</b>
1. وارد کردن نام و نام خانوادگی
2. وارد کردن شماره تلفن
3. وارد کردن کد ملی
4. انتخاب کلاس
5. پرداخت

🔹 <b>نکات مهم:</b>
• شماره تلفن باید با 09 شروع شود
• کد ملی باید 10 رقم باشد
• تمرین‌ها در روزهای شنبه، دوشنبه و چهارشنبه برگزار می‌شود

📞 برای پشتیبانی: @support
    """
    
    keyboard = create_keyboard([
        [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
    ])
    
    send_message(chat_id, help_text, reply_markup=keyboard)

print("✅ تمرین 14: پردازش پیام‌ها تکمیل شد!")

# تمرین: تابعی برای پردازش پیام‌های صوتی بنویسید
# تمرین: تابعی برای پردازش پیام‌های تصویری بنویسید
# تمرین: تابعی برای پردازش فایل‌ها بنویسید