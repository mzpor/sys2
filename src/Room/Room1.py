# ... existing code ...
import os
import jdatetime
import requests
import json
import time
import re
import logging
from threading import Timer

# --- ذخیره و بارگذاری داده‌ها ---
DATA_FILE = 'bot_data.json'

def save_data():
    data = {
        'known_members': known_members,
        'recitation_exercises': recitation_exercises,
        'exercise_scores': exercise_scores,
        'attendance': attendance
    }
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"خطا در ذخیره داده‌ها: {e}")

def load_data():
    global known_members, recitation_exercises, exercise_scores, attendance
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            known_members = data.get('known_members', {})
            recitation_exercises = data.get('recitation_exercises', {})
            exercise_scores = data.get('exercise_scores', {})
            attendance = data.get('attendance', {})
    except FileNotFoundError:
        pass
    except Exception as e:
        logging.error(f"خطا در بارگذاری داده‌ها: {e}")
# --- پایان ذخیره و بارگذاری داده‌ها ---
# ... existing code ...
def add_known_member(user_info, chat_id):
    """افزودن عضو جدید به لیست"""
    user_id = user_info.get('id')
    if chat_id not in known_members:
        known_members[chat_id] = {}
    if user_id not in known_members[chat_id]:
        known_members[chat_id][user_id] = {
            'name': get_simple_name(user_info),
            'id': user_id,
            'added_time': time.time()
        }
        send_message(chat_id, get_simple_members_list(chat_id))
        save_data()  # ذخیره پس از تغییر
# ... existing code ...
def handle_recitation_exercise(message):
    # ... existing code ...
    if has_audio and is_exercise:
        if chat_id not in recitation_exercises:
            recitation_exercises[chat_id] = {}
        recitation_exercises[chat_id][user_id] = {
            'status': 'sent',
            'score': None,
            'date': get_jalali_date(),
            'message_id': message['message_id'],
            'user_name': user_name,
            'exercise_day': get_week_day()
        }
        send_message(chat_id, f"✅ تلاوت {user_name} دریافت شد!")
        schedule_report(chat_id)
        save_data()  # ذخیره پس از تغییر
        return True
    return False
# ... existing code ...
def handle_admin_score(message):
    # ... existing code ...
    if match and not recitation_exercises[chat_id][replied_user_id].get('score'):
        score = match.group(0)
        recitation_exercises[chat_id][replied_user_id]['score'] = score
        if chat_id not in exercise_scores:
            exercise_scores[chat_id] = {}
        if replied_user_id not in exercise_scores[chat_id]:
            exercise_scores[chat_id][replied_user_id] = []
        exercise_scores[chat_id][replied_user_id].append({
            'score': score,
            'date': get_jalali_date(),
            'week_day': recitation_exercises[chat_id][replied_user_id]['exercise_day']
        })
        user_name = recitation_exercises[chat_id][replied_user_id]['user_name']
        response = f"🎯 نمره جدید: {user_name} - {score}\n📅 {get_jalali_date()}"
        send_message(chat_id, response)
        save_data()  # ذخیره پس از تغییر
        return True
    return False
# ... existing code ...
def handle_attendance(message):
    # ... existing code ...
    if chat_id not in attendance:
        attendance[chat_id] = {}
    attendance[chat_id][replied_user_id] = {
        'date': get_jalali_date(),
        'present': text == 'حاضر'
    }
    user_name = get_simple_name(reply_message['from'])
    send_message(chat_id, f"📋 حضور و غیاب: {user_name} - {text}\n📅 {get_jalali_date()}")
    save_data()  # ذخیره پس از تغییر
# ... existing code ...


def main():
    """تابع اصلی ربات"""
    logging.info("ربات تلاوت شروع شد...")
    load_data()  # بارگذاری داده‌ها در شروع
    offset = None
    while True:
        # ... existing code ...