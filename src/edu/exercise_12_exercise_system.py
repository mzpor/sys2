 """
تمرین 12: سیستم تمرین
سطح: متوسط
هدف: آشنایی با مدیریت تمرین‌ها
"""

# متغیرهای سیستم تمرین
recitation_exercises = {}
exercise_scores = {}

def handle_recitation_exercise(message):
    """
    مدیریت تمرین تلاوت
    
    پارامترها:
        message (dict): پیام دریافتی
    """
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    user_name = get_simple_name(message['from'])
    
    if not is_exercise_day():
        send_message(chat_id, "امروز روز تمرین نیست. تمرین‌ها در روزهای شنبه، دوشنبه و چهارشنبه برگزار می‌شود.")
        return
    
    if chat_id not in recitation_exercises:
        recitation_exercises[chat_id] = {
            'active': False,
            'participants': {},
            'start_time': None,
            'end_time': None
        }
    
    exercise_data = recitation_exercises[chat_id]
    
    if not exercise_data['active']:
        # شروع تمرین جدید
        exercise_data['active'] = True
        exercise_data['start_time'] = time.time()
        exercise_data['end_time'] = time.time() + (24 * 60 * 60)  # 24 ساعت
        exercise_data['participants'] = {}
        
        message_text = f"""
🏃‍♂️ <b>تمرین تلاوت شروع شد!</b>

👤 شروع کننده: {user_name}
⏰ مهلت: {get_exercise_deadline()}

📝 برای شرکت در تمرین، پیام خود را ارسال کنید.
        """
        
        keyboard = create_keyboard([
            [{'text': '📊 مشاهده نتایج', 'callback_data': 'view_exercise_results'}]
        ])
        
        send_message(chat_id, message_text, reply_markup=keyboard)
    else:
        # اضافه کردن شرکت‌کننده
        if user_id not in exercise_data['participants']:
            exercise_data['participants'][user_id] = {
                'name': user_name,
                'submission_time': time.time(),
                'message': message.get('text', '')
            }
            
            send_message(chat_id, f"✅ {user_name} در تمرین شرکت کرد!")
        else:
            send_message(chat_id, f"شما قبلاً در این تمرین شرکت کرده‌اید.")

def generate_exercise_report(chat_id, immediate=False, scored_user=None, scored_value=None):
    """
    تولید گزارش تمرین
    
    پارامترها:
        chat_id (int): شناسه گروه
        immediate (bool): آیا گزارش فوری ارسال شود
        scored_user (int): کاربر امتیاز داده شده
        scored_value (int): امتیاز داده شده
    """
    if chat_id not in recitation_exercises:
        return
    
    exercise_data = recitation_exercises[chat_id]
    
    if not exercise_data['active']:
        return
    
    participants = exercise_data['participants']
    total_participants = len(participants)
    
    if total_participants == 0:
        message_text = "هنوز کسی در تمرین شرکت نکرده است."
    else:
        message_text = f"""
📊 <b>گزارش تمرین تلاوت</b>

👥 تعداد شرکت‌کنندگان: {total_participants}
⏰ مهلت: {get_exercise_deadline()}

📝 شرکت‌کنندگان:
        """
        
        for user_id, participant in participants.items():
            message_text += f"\n• {participant['name']}"
    
    if immediate:
        send_message(chat_id, message_text)
    
    return message_text

def handle_admin_score(message):
    """
    مدیریت امتیازدهی توسط ادمین
    
    پارامترها:
        message (dict): پیام دریافتی
    """
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    
    if not is_admin(user_id, chat_id):
        return
    
    text = message.get('text', '')
    
    # فرمت: /score user_id score_value
    if text.startswith('/score '):
        parts = text.split()
        if len(parts) == 3:
            try:
                target_user_id = int(parts[1])
                score_value = int(parts[2])
                
                if score_value < 0 or score_value > 10:
                    send_message(chat_id, "امتیاز باید بین 0 تا 10 باشد.")
                    return
                
                if chat_id not in exercise_scores:
                    exercise_scores[chat_id] = {}
                
                exercise_scores[chat_id][target_user_id] = score_value
                
                send_message(chat_id, f"امتیاز {score_value} برای کاربر {target_user_id} ثبت شد.")
                
            except ValueError:
                send_message(chat_id, "فرمت صحیح: /score user_id score_value")

print("✅ تمرین 12: سیستم تمرین تکمیل شد!")

# تمرین: تابعی برای پایان دادن به تمرین بنویسید
# تمرین: تابعی برای محاسبه میانگین امتیازات بنویسید
# تمرین: تابعی برای نمایش رتبه‌بندی شرکت‌کنندگان بنویسید