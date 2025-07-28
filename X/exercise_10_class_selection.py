 """
تمرین 10: سیستم انتخاب کلاس
سطح: متوسط
هدف: آشنایی با نمایش و انتخاب کلاس‌ها
"""

def show_classes(chat_id, user_id):
    """
    نمایش لیست کلاس‌ها به کاربر
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
    """
    keyboard_buttons = []
    for class_id, class_info in CLASSES.items():
        keyboard_buttons.append([{'text': class_info['name'], 'callback_data': f'select_class_{class_id}'}])
    
    keyboard = create_keyboard(keyboard_buttons)
    send_message(chat_id, "لطفا کلاس مورد نظر خود را انتخاب کنید:", reply_markup=keyboard)
    
    if user_id in user_states:
        user_states[user_id]['step'] = 'waiting_for_class_selection'

def handle_class_selection(chat_id, user_id, class_id):
    """
    مدیریت انتخاب کلاس توسط کاربر
    
    پارامترها:
        chat_id (int): شناسه چت
        user_id (int): شناسه کاربر
        class_id (str): شناسه کلاس
    """
    if class_id in CLASSES:
        if user_id in user_states:
            user_states[user_id]['selected_class'] = class_id
        
        class_info = CLASSES[class_id]
        message_text = f"شما کلاس *{class_info['name']}* را انتخاب کردید.\n"
        message_text += f"هزینه: {class_info['price']}\n"
        message_text += f"برنامه: {class_info['schedule']}\n\n"
        message_text += "برای ادامه، لطفا پرداخت را انجام دهید."
        
        keyboard = create_keyboard([[{'text': 'لینک پرداخت', 'callback_data': f'show_payment_{class_id}'}]])
        send_message(chat_id, message_text, reply_markup=keyboard)
        
        if user_id in user_states:
            user_states[user_id]['step'] = 'waiting_for_payment_link_request'
    else:
        send_message(chat_id, "کلاس انتخابی نامعتبر است. لطفا دوباره تلاش کنید.")

def show_class_details(class_id):
    """
    نمایش جزئیات کلاس
    
    پارامترها:
        class_id (str): شناسه کلاس
    
    خروجی:
        str: متن جزئیات کلاس
    """
    if class_id not in CLASSES:
        return "کلاس یافت نشد."
    
    class_info = CLASSES[class_id]
    details = f"""
📚 <b>جزئیات کلاس:</b>

📖 نام: {class_info['name']}
💰 قیمت: {class_info['price']}
📅 برنامه: {class_info['schedule']}
    """
    return details

def get_available_classes():
    """
    دریافت لیست کلاس‌های موجود
    
    خروجی:
        dict: لیست کلاس‌های موجود
    """
    return CLASSES

print("✅ تمرین 10: سیستم انتخاب کلاس تکمیل شد!")

# تست توابع
print("📚 کلاس‌های موجود:")
for class_id, class_info in CLASSES.items():
    print(f"  - {class_info['name']}: {class_info['price']}")

# تمرین: تابعی برای فیلتر کردن کلاس‌ها بر اساس قیمت بنویسید
# تمرین: تابعی برای جستجوی کلاس بر اساس نام بنویسید
# تمرین: تابعی برای نمایش کلاس‌های پیشنهادی بنویسید