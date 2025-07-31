 """
تمرین 11: سیستم پرداخت
سطح: متوسط
هدف: آشنایی با مدیریت پرداخت‌ها
"""

def show_payment_link(chat_id, user_id, class_id):
    """
    نمایش لینک پرداخت برای کلاس انتخاب شده
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
        class_id (str): شناسه کلاس
    """
    if class_id not in CLASSES:
        send_message(chat_id, "کلاس انتخابی نامعتبر است.")
        return
    
    class_info = CLASSES[class_id]
    payment_link = PAYMENT_LINKS.get(class_id, "لینک پرداخت در دسترس نیست")
    
    message_text = f"""
💳 <b>پرداخت کلاس {class_info['name']}</b>

💰 مبلغ: {class_info['price']}
📅 برنامه: {class_info['schedule']}

🔗 <a href="{payment_link}">لینک پرداخت</a>

⚠️ پس از پرداخت، روی دکمه "پرداخت انجام شد" کلیک کنید.
    """
    
    keyboard = create_keyboard([
        [{'text': '✅ پرداخت انجام شد', 'callback_data': 'payment_completed'}],
        [{'text': '❌ انصراف', 'callback_data': 'cancel_payment'}]
    ])
    
    send_message(chat_id, message_text, reply_markup=keyboard)
    
    if user_id in user_states:
        user_states[user_id]['step'] = 'waiting_for_payment_confirmation'

def handle_payment_completion(chat_id, user_id):
    """
    مدیریت تکمیل پرداخت
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
    """
    if user_id not in user_states:
        send_message(chat_id, "خطا در فرآیند پرداخت. لطفا دوباره تلاش کنید.")
        return
    
    user_data = user_states[user_id]
    selected_class = user_data.get('selected_class')
    
    if not selected_class or selected_class not in CLASSES:
        send_message(chat_id, "کلاس انتخابی نامعتبر است.")
        return
    
    class_info = CLASSES[selected_class]
    
    # ذخیره اطلاعات کاربر
    if user_id not in registered_users:
        registered_users[user_id] = {}
    
    registered_users[user_id].update({
        'first_name': user_data.get('first_name', ''),
        'last_name': user_data.get('last_name', ''),
        'mobile': user_data.get('mobile', ''),
        'national_id': user_data.get('national_id', ''),
        'registered_class': selected_class,
        'registration_date': time.time()
    })
    
    # ذخیره در فایل
    save_users_to_file()
    
    # پیام موفقیت
    success_message = f"""
🎉 <b>تبریک! ثبت‌نام شما با موفقیت تکمیل شد!</b>

👤 نام: {user_data.get('first_name', '')} {user_data.get('last_name', '')}
📚 کلاس: {class_info['name']}
💰 مبلغ: {class_info['price']}
✅ وضعیت: پرداخت شده

🌟 محمد می‌گه: «قدم گذاشتن در مسیر رشد از همین‌جا شروع می‌شه!»

📞 برای اطلاعات بیشتر با پشتیبانی تماس بگیرید.
    """
    
    send_message(chat_id, success_message)
    
    # پاک کردن وضعیت کاربر
    if user_id in user_states:
        del user_states[user_id]

def verify_payment(payment_id):
    """
    تایید پرداخت (در محیط واقعی باید با درگاه پرداخت ارتباط برقرار شود)
    
    پارامترها:
        payment_id (str): شناسه پرداخت
    
    خروجی:
        bool: True اگر پرداخت تایید شده باشد
    """
    # این تابع در محیط واقعی باید با API درگاه پرداخت ارتباط برقرار کند
    # فعلاً برای نمونه، همیشه True برمی‌گرداند
    return True

print("✅ تمرین 11: سیستم پرداخت تکمیل شد!")

# تمرین: تابعی برای بررسی وضعیت پرداخت بنویسید
# تمرین: تابعی برای لغو پرداخت بنویسید
# تمرین: تابعی برای بازپرداخت بنویسید