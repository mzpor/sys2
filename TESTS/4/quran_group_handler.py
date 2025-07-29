 # مدیریت گروه‌های قرآنی
# بخش مدیریت تمرین‌ها، نمره‌دهی و گزارش‌گیری

import jdatetime
import requests
import json
import time
import re
import logging
from quran_bot_main import *

def add_known_member(user_info, chat_id):
    """افزودن عضو جدید به لیست اعضای شناخته‌شده"""
    user_id = user_info.get('id')
    if not user_id:
        logging.error("شناسه کاربر نامعتبر است")
        return
    
    if chat_id not in known_members:
        known_members[chat_id] = {}
    if user_id not in known_members[chat_id]:
        known_members[chat_id][user_id] = {
            'name': get_simple_name(user_info),
            'id': user_id,
            'first_name': user_info.get('first_name', ''),
            'last_name': user_info.get('last_name', ''),
            'added_time': time.time()
        }
    
    if chat_id not in recitation_exercises:
        recitation_exercises[chat_id] = {}
    if user_id not in recitation_exercises[chat_id]:
        recitation_exercises[chat_id][user_id] = {
            'status': 'waiting',
            'score': None,
            'date': '',
            'message_id': None,
            'exercise_day': 'Saturday'
        }

def handle_recitation_exercise(message):
    """پردازش ارسال تمرین تلاوت"""
    chat_id = message['chat']['id']
    user_info = message['from']
    user_id = user_info.get('id')
    user_name = get_simple_name(user_info)
    
    has_voice = 'voice' in message
    has_audio = 'audio' in message
    
    text = message.get('caption', '').lower()
    exercise_pattern = r'\b(تلاوت|تمرین|ارسال تلاوت|قرآن|تلاوت قرآن)\b'
    is_exercise = bool(re.search(exercise_pattern, text, re.IGNORECASE))
    
    if is_admin(user_id, chat_id):
        logging.info(f"ادمین {user_name} ({user_id}) سعی کرد تمرین ارسال کند. نادیده گرفته شد.")
        return False

    if (has_voice or has_audio) and is_exercise:
        now = jdatetime.datetime.now()
        weekday = now.weekday()
        
        if weekday == 0:
            exercise_day = 'Saturday'
        elif weekday in [1, 2]:
            exercise_day = 'Monday'
        elif weekday in [3, 4]:
            exercise_day = 'Wednesday'
        else:
            send_message(chat_id, "⚠️ مهلت ارسال تلاوت به پایان رسیده است. لطفاً در روزهای تعیین شده تلاوت خود را ارسال کنید.")
            return False
        
        if chat_id not in recitation_exercises:
            recitation_exercises[chat_id] = {}
        
        recitation_exercises[chat_id][user_id] = {
            'status': 'sent',
            'score': None,
            'date': get_jalali_date(),
            'message_id': message['message_id'],
            'user_name': user_name,
            'exercise_day': exercise_day
        }
        
        report_message = generate_exercise_report(chat_id)
        send_message(chat_id, report_message)
        
        return True
    
    return False

def handle_admin_score(message):
    """پردازش نمره‌دهی توسط ادمین"""
    chat_id = message['chat']['id']
    user_info = message['from']
    user_id = user_info.get('id')
    
    if not is_admin(user_id, chat_id):
        return False
    
    if 'reply_to_message' not in message:
        return False
    
    reply_message = message['reply_to_message']
    replied_user_id = reply_message['from']['id']
    replied_message_id = reply_message['message_id']
    
    if chat_id not in recitation_exercises or replied_user_id not in recitation_exercises[chat_id]:
        return False
    
    exercise_data = recitation_exercises[chat_id][replied_user_id]
    if exercise_data.get('message_id') != replied_message_id:
        return False
    
    text = message.get('text', '').lower()
    score_pattern = r'\b(عالی|خوب|متوسط|ضعیف|بد)\b'
    match = re.search(score_pattern, text, re.IGNORECASE)
    score = match.group(0) if match else None
    
    if score and not exercise_data.get('score'):
        exercise_data['score'] = score
        
        if chat_id not in exercise_scores:
            exercise_scores[chat_id] = {}
        if replied_user_id not in exercise_scores[chat_id]:
            exercise_scores[chat_id][replied_user_id] = []
        
        exercise_scores[chat_id][replied_user_id].append({
            'score': score,
            'date': get_jalali_date(),
            'week_day': exercise_data.get('exercise_day', get_week_day())
        })
        
        user_name = exercise_data.get('user_name', 'کاربر')
        response = f"🎯 استاد به شما این نمره رو داد: **{score}**\n\n"
        response += f"👤 {user_name}\n"
        response += f"📅 {get_jalali_date()}\n{get_week_day()}\n\n"
        response += generate_exercise_report(chat_id, immediate=True, scored_user=user_name, scored_value=score)
        send_message(chat_id, response)
        
        return True
    
    return False

def generate_exercise_report(chat_id, immediate=False, scored_user=None, scored_value=None):
    """تولید گزارش وضعیت تمرین‌ها"""
    global quote_index
    
    if chat_id not in known_members:
        return "هیچ عضوی ثبت نشده!"
    
    report = f"📋 گزارش تمرین تلاوت قرآن\n\n"
    report += f"📅 {get_week_day()} {get_jalali_date()}"
    
    if immediate and scored_user:
        report += f"🆕 نمره جدید: {scored_user} - {scored_value}\n\n"
    
    if is_exercise_day():
        report += f"🟢 امروز روز تمرین است ({get_week_day()})\n\n"
    else:
        report += f"🔴 امروز روز تمرین نیست ({get_week_day()})\n\n"
    
    sent_exercises = []
    waiting_exercises = []
    scored_exercises = []
    
    current_exercise_day = (
        'Saturday' if jdatetime.datetime.now().weekday() == 5 else
        'Monday' if jdatetime.datetime.now().weekday() in [6, 0] else
        'Wednesday' if jdatetime.datetime.now().weekday() == 1 else
        'Thursday'
    )
    
    administrators = get_chat_administrators(chat_id)
    admin_ids = {admin_info.get('user', {}).get('id') for admin_info in administrators}

    for user_id, user_data in known_members[chat_id].items():
        if user_id in admin_ids:
            continue
        user_name = user_data['name']
        
        if chat_id in recitation_exercises and user_id in recitation_exercises[chat_id]:
            exercise = recitation_exercises[chat_id][user_id]
            
            if exercise['status'] == 'sent' and exercise.get('exercise_day') == current_exercise_day:
                if exercise['score']:
                    scored_exercises.append(f"✅ {user_name} - نمره: {exercise['score']}")
                else:
                    sent_exercises.append(f"⏳ {user_name} - در انتظار بررسی")
            else:
                waiting_exercises.append(f"❌ {user_name} - در انتظار تمرین")
        else:
            waiting_exercises.append(f"❌ {user_name} - در انتظار تمرین")
    
    if scored_exercises:
        report += "🎯 نمره گرفته‌ها:\n"
        for item in scored_exercises:
            report += f"{item}\n"
        report += "\n"
    
    if sent_exercises:
        report += "⏳ تمرین‌های در انتظار نمره:\n"
        for item in sent_exercises:
            report += f"{item}\n"
        report += "\n"
    
    if waiting_exercises:
        report += "❌ در انتظار تمرین:\n"
        for item in waiting_exercises:
            report += f"{item}\n"
        report += "\n"
    
    total = len(known_members[chat_id])
    sent_count = len(sent_exercises) + len(scored_exercises)
    participation_percentage = (sent_count / total * 100) if total > 0 else 0
    
    report += f"📊 آمار کلی:\n"
    report += f"👥 کل اعضا: {total}\n"
    report += f"📤 تمرین فرستاده: {sent_count}\n"
    report += f"📥 در انتظار: {len(waiting_exercises)}\n"
    report += f"📈 درصد مشارکت: {participation_percentage:.1f}%\n\n"
    
    report += f"💡 پیام انگیزشی:\n{MOTIVATIONAL_QUOTES[quote_index]}\n\n"
    quote_index = (quote_index + 1) % len(MOTIVATIONAL_QUOTES)
    
    report += f"⏰ مهلت ارسال تمرین:\n"
    report += f"تا پایان امروز\n"
    report += "🏃‍♂️ عجله کنید، فرصت را از دست ندهید!"
    
    return report

def generate_score_report(chat_id):
    """تولید گزارش کلی نمرات"""
    global quote_index
    
    if chat_id not in exercise_scores or not any(exercise_scores[chat_id].values()):
        send_message(chat_id, "هنوز هیچ نمره‌ای ثبت نشده!")
        return
    
    report = f"🏆 گزارش کلی نمرات تلاوت قرآن\n\n"
    report += f"📅 {get_week_day()} {get_jalali_date()}\n\n"
    
    excellent_users = []
    good_users = []
    average_users = []
    weak_users = []
    no_exercise = []
    
    administrators = get_chat_administrators(chat_id)
    admin_ids = {admin_info.get('user', {}).get('id') for admin_info in administrators}

    for user_id, user_data in known_members[chat_id].items():
        if user_id in admin_ids:
            continue
        user_name = user_data['name']
        
        if user_id in exercise_scores[chat_id] and exercise_scores[chat_id][user_id]:
            last_score = exercise_scores[chat_id][user_id][-1]['score']
            
            if last_score == 'عالی':
                excellent_users.append(user_name)
            elif last_score == 'خوب':
                good_users.append(user_name)
            elif last_score == 'متوسط':
                average_users.append(user_name)
            elif last_score in ['ضعیف', 'بد']:
                weak_users.append(user_name)
        else:
            no_exercise.append(user_name)
    
    if excellent_users:
        report += "🌟 عالی:\n"
        for i, name in enumerate(sorted(excellent_users), 1):
            report += f"{i}. {name}\n"
        report += "\n"
    
    if good_users:
        report += "👍 خوب:\n"
        for i, name in enumerate(sorted(good_users), 1):
            report += f"{i}. {name}\n"
        report += "\n"
    
    if average_users:
        report += "📊 متوسط:\n"
        for i, name in enumerate(sorted(average_users), 1):
            report += f"{i}. {name}\n"
        report += "\n"
    
    if weak_users:
        report += "👎 نیاز به تلاش:\n"
        for i, name in enumerate(sorted(weak_users), 1):
            report += f"{i}. {name}\n"
        report += "\n"
    
    if no_exercise:
        report += "❌ بدون تمرین:\n"
        for i, name in enumerate(sorted(no_exercise), 1):
            report += f"{i}. {name}\n"
        report += "\n"
    
    total = len(known_members[chat_id])
    report += f"📊 آمار:\n"
    report += f"🌟 عالی: {len(excellent_users)}\n"
    report += f"👍 خوب: {len(good_users)}\n"
    report += f"📊 متوسط: {len(average_users)}\n"
    report += f"👎 نیاز به تلاش: {len(weak_users)}\n"
    report += f"❌ بدون تمرین: {len(no_exercise)}\n"
    report += f"👥 کل: {total}\n\n"
    
    report += f"💡 پیام انگیزشی:\n{MOTIVATIONAL_QUOTES[quote_index]}\n\n"
    quote_index = (quote_index + 1) % len(MOTIVATIONAL_QUOTES)
    
    report += f"⏰ مهلت ارسال تمرین:\n"
    report += f"تا پایان امروز\n"
    report += "🏃‍♂️ عجله کنید، فرصت را از دست ندهید!"
    
    send_message(chat_id, report)

def get_simple_members_list(chat_id):
    """تهیه لیست ساده از اعضای گروه"""
    administrators = get_chat_administrators(chat_id)
    admin_ids = {admin_info.get('user', {}).get('id') for admin_info in administrators}
    admin_names = sorted([get_simple_name(admin_info.get('user', {})) for admin_info in administrators])
    
    regular_members = sorted([user_info['name'] for user_id, user_info in known_members.get(chat_id, {}).items() 
                            if user_id not in admin_ids])
    
    report = f"📋 لیست اعضای گروه قرآنی\n\n"
    report += f"📅 {get_week_day()} {get_jalali_date()}"
    
    report += "👑 ادمین‌های گروه:\n"
    if admin_names:
        for admin_name in admin_names:
            report += f"- {admin_name}\n"
    report += "\n"
    
    report += "👥 قرآن‌آموزان:\n"
    if regular_members:
        for i, member_name in enumerate(regular_members, 1):
            report += f"{i}. {member_name}\n"
    report += "\n"
    
    total_known = len(regular_members)
    total_admins = len(admin_names)
    
    report += f"📊 آمار:\n"
    report += f"👑 تعداد ادمین‌ها: {total_admins} نفر\n"
    report += f"👥 تعداد قرآن‌آموزان: {total_known} نفر\n"
    report += f"🔍 کل اعضای عضو شده: {total_known + total_admins} نفر\n\n"
    
    if total_known < 10:
        report += "💡 نکته: برای ارسال تمرین و ارزیابی، لطفا /عضو بزنید\n\n"
        report += "⚠️ محدودیت: API بله، امکان دریافت همه اعضا را نمی‌دهد."
    
    return report

def welcome_new_member(chat_id, user_info):
    """خوش‌آمدگویی به عضو جدید"""
    user_id = user_info.get('id')
    
    if not is_admin(user_id, chat_id):
        user_name = get_simple_name(user_info)
        welcome_msg = f"🎉 سلام {user_name}!\n\n"
        welcome_msg += "به گروه قرآنی خوش آمدید! 🌟\n\n"
        welcome_msg += "برای ثبت در لیست گروه و ارسال تمرین، لطفاً /عضو بزنید 👍\n\n"
        welcome_msg += f"📅 امروز: {get_week_day()} {get_jalali_date()}\n"
        welcome_msg += "⏰ روزهای تمرین: شنبه، دوشنبه، چهارشنبه"
        send_message(chat_id, welcome_msg)

def process_new_chat_member(message):
    """پردازش عضو جدید گروه"""
    if 'new_chat_members' in message:
        chat_id = message['chat']['id']
        for new_member in message['new_chat_members']:
            add_known_member(new_member, chat_id)
            welcome_new_member(chat_id, new_member)