 """
تمرین 13: مدیریت callback ها
سطح: متوسط
هدف: آشنایی با پردازش دکمه‌های شیشه‌ای
"""

def handle_callback_query(message):
    """
    مدیریت دکمه‌های شیشه‌ای
    
    پارامترها:
        message (dict): پیام callback
    """
    callback_query = message.get('callback_query', {})
    data = callback_query.get('data', '')
    chat_id = callback_query['message']['chat']['id']
    user_id = callback_query['from']['id']
    
    print(f"دکمه شیشه‌ای از چت {chat_id}: {data}")
    
    # مدیریت منوی اصلی
    if data == 'school_registration':
        start_registration(chat_id, user_id)
    
    elif data == 'user_account':
        handle_user_account(chat_id, user_id)
    
    elif data == 'survey':
        handle_survey(chat_id, user_id)
    
    elif data == 'about_bot':
        handle_about_bot(chat_id, user_id)
    
    elif data == 'new_class_registration':
        show_classes(chat_id, user_id)
    
    elif data == 'edit_user_info':
        start_registration(chat_id, user_id)
    
    elif data == 'back_to_main_menu':
        show_main_menu(chat_id, user_id)
    
    # مدیریت ثبت‌نام
    elif data == 'edit_name':
        start_name_registration(chat_id, user_id)
    
    elif data == 'edit_phone':
        show_phone_input_request(chat_id, user_id)
    
    elif data == 'edit_national_id':
        if user_id in user_states:
            user_states[user_id]['step'] = 'waiting_national_id'
        send_message(chat_id, "لطفاً کد ملی خود را وارد کنید:")
    
    elif data == 'confirm_info':
        show_classes(chat_id, user_id)
    
    elif data == 'edit_info':
        start_registration(chat_id, user_id)
    
    # مدیریت انتخاب کلاس
    elif data.startswith('select_class_'):
        class_id = data.split('_')[-1]
        handle_class_selection(chat_id, user_id, class_id)
    
    elif data.startswith('show_payment_'):
        class_id = data.split('_')[-1]
        show_payment_link(chat_id, user_id, class_id)
    
    elif data == 'payment_completed':
        handle_payment_completion(chat_id, user_id)
    
    elif data == 'cancel_payment':
        show_main_menu(chat_id, user_id)
    
    # مدیریت نظر سنجی
    elif data.startswith('survey_'):
        survey_result = data.split('_')[1]
        handle_survey_response(chat_id, user_id, survey_result)
    
    # مدیریت تمرین
    elif data == 'view_exercise_results':
        generate_exercise_report(chat_id, immediate=True)
    
    else:
        send_message(chat_id, "دکمه انتخابی نامعتبر است.")

def handle_survey_response(chat_id, user_id, response):
    """
    مدیریت پاسخ نظر سنجی
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
        response (str): پاسخ کاربر
    """
    responses = {
        'excellent': '⭐ عالی',
        'good': '👍 خوب',
        'needs_improvement': '👎 نیاز به بهبود'
    }
    
    response_text = responses.get(response, 'نامشخص')
    
    message_text = f"""
📊 <b>نظر سنجی</b>

👤 کاربر: {get_simple_name({'id': user_id})}
⭐ نظر: {response_text}

🙏 از مشارکت شما سپاسگزاریم!
    """
    
    keyboard = create_keyboard([
        [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
    ])
    
    send_message(chat_id, message_text, reply_markup=keyboard)

def handle_about_bot(chat_id, user_id):
    """
    نمایش اطلاعات ربات
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
    """
    about_text = """
🤖 <b>درباره ربات تلاوت</b>

📚 این ربات برای مدیریت کلاس‌های تلاوت قرآن طراحی شده است.

✨ <b>قابلیت‌ها:</b>
• ثبت‌نام در کلاس‌ها
• مدیریت حساب کاربری
• سیستم تمرین
• نظر سنجی
• گزارش‌گیری

👨‍💻 <b>توسعه‌دهنده:</b> تیم تلاوت

📞 <b>پشتیبانی:</b> @support
    """
    
    keyboard = create_keyboard([
        [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
    ])
    
    send_message(chat_id, about_text, reply_markup=keyboard)

print("✅ تمرین 13: مدیریت callback ها تکمیل شد!")

# تمرین: callback جدید برای تنظیمات اضافه کنید
# تمرین: callback برای نمایش راهنما اضافه کنید
# تمرین: callback برای تماس با پشتیبانی اضافه کنید