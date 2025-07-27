import os
import jdatetime
import requests
import json
import time
import re
import logging
from threading import Timer

# تنظیمات لاگ‌گیری
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# توکن ربات از متغیر محیطی
BOT_TOKEN = os.environ.get('BOT_TOKEN', '811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1')  # یار مربی (برای تست)
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

# تنظیمات گروه‌ها (برای شرط‌گذاری روزهای تمرین)
GROUP_CONFIGS = {
    "-100123456789": {"exercise_days": [0, 4]},  # گروه خاص: فقط شنبه و چهارشنبه
    # گروه‌های دیگر به‌طور پیش‌فرض: شنبه، دوشنبه، چهارشنبه
}

# پیام‌های انگیزشی
motivational_quotes = [
    "🌟 تمرین تلاوت، گامی به سوی نور!",
    "🚀 با هر تلاوت، به خدا نزدیک‌تر شو!",
    "💪 تمرین مداوم، کلید موفقیت است!"
]
quote_index = 0

# داده‌ها
known_members = {}  # {chat_id: {user_id: {name, id, first_name, last_name, added_time}}}
recitation_exercises = {}  # {chat_id: {user_id: {status, score, date, message_id, exercise_day}}}
exercise_scores = {}  # {chat_id: {user_id: [scores]}}

def create_keyboard(buttons, is_inline=True):
    """ایجاد کیبورد برای دکمه‌ها"""
    if is_inline:
        return {"inline_keyboard": [[{"text": btn["text"], "callback_data": btn["callback_data"]} for btn in row] for row in buttons]}
    return {"keyboard": [[{"text": btn["text"]} for btn in row] for row in buttons], "resize_keyboard": True, "one_time_keyboard": False}

def get_updates(offset=None):
    """دریافت پیام‌های جدید از API"""
    params = {'offset': offset} if offset else {}
    try:
        response = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=10)
        return response.json() if response.ok else None
    except requests.RequestException as e:
        logging.error(f"خطای شبکه: {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    """ارسال پیام به گروه"""
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        response = requests.post(f"{BASE_URL}/sendMessage", json=data, timeout=10)
        if not response.ok:
            logging.error(f"خطا در ارسال پیام: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"خطای شبکه: {e}")

def get_chat_administrators(chat_id):
    """دریافت لیست ادمین‌ها"""
    try:
        response = requests.get(f"{BASE_URL}/getChatAdministrators", params={"chat_id": chat_id}, timeout=10)
        return response.json().get('result', []) if response.ok else []
    except requests.RequestException as e:
        logging.error(f"خطای شبکه: {e}")
        return []

def get_simple_name(user):
    """دریافت نام ساده کاربر"""
    first_name = user.get('first_name', '')
    last_name = user.get('last_name', '')
    full_name = f"{first_name} {last_name}".strip()
    return full_name if full_name else user.get('username', 'بدون نام')

def get_jalali_date():
    """دریافت تاریخ جلالی"""
    now = jdatetime.datetime.now()
    months = {1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد', 4: 'تیر', 5: 'مرداد', 6: 'شهریور',
              7: 'مهر', 8: 'آبان', 9: 'آذر', 10: 'دی', 11: 'بهمن', 12: 'اسفند'}
    return f"{now.day} {months.get(now.month, '')}"

def get_week_day():
    """دریافت نام روز هفته"""
    weekdays = {0: 'شنبه', 1: 'یک‌شنبه', 2: 'دوشنبه', 3: 'سه‌شنبه', 4: 'چهارشنبه', 5: 'پنج‌شنبه', 6: 'جمعه'}
    return weekdays.get(jdatetime.datetime.now().weekday(), 'نامشخص')

def is_exercise_day(chat_id):
    """بررسی روز تمرین برای گروه"""
    weekday = jdatetime.datetime.now().weekday()
    group_config = GROUP_CONFIGS.get(str(chat_id), {"exercise_days": [0, 2, 4]})  # پیش‌فرض: شنبه، دوشنبه، چهارشنبه
    return weekday in group_config["exercise_days"]

def is_scoring_day():
    """بررسی روز نمره‌دهی"""
    weekday = jdatetime.datetime.now().weekday()
    return weekday in [1, 3, 5]  # یکشنبه، سه‌شنبه، پنج‌شنبه

def schedule_report(chat_id):
    """زمان‌بندی گزارش خودکار در پایان مهلت"""
    now = jdatetime.datetime.now()
    if is_exercise_day(chat_id):
        deadline = now.replace(hour=23, minute=59, second=59)
        seconds_until_deadline = (deadline - now).total_seconds()
        if seconds_until_deadline > 0:
            Timer(seconds_until_deadline, lambda: send_message(chat_id, generate_exercise_report(chat_id, immediate=True))).start()

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
        # نمایش لیست اعضا پس از عضویت
        send_message(chat_id, get_simple_members_list(chat_id))

def handle_recitation_exercise(message):
    """پردازش تمرین تلاوت"""
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    user_name = get_simple_name(message['from'])

    if is_admin(user_id, chat_id):
        return False

    if not is_exercise_day(chat_id):
        send_message(chat_id, "⚠️ امروز روز تمرین نیست! روزهای تمرین: شنبه، دوشنبه، چهارشنبه")
        return False

    has_audio = 'voice' in message or 'audio' in message
    text = message.get('caption', '').lower()
    is_exercise = bool(re.search(r'\b(تلاوت|تمرین|ارسال تلاوت)\b', text, re.IGNORECASE))

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
        send_message(chat_id, f"✅ تمرین {user_name} دریافت شد!")
        schedule_report(chat_id)
        return True
    return False

def handle_admin_score(message):
    """پردازش نمره‌دهی ادمین"""
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    if not is_admin(user_id, chat_id):
        return False
    if 'reply_to_message' not in message:
        return False

    reply_message = message['reply_to_message']
    replied_user_id = reply_message['from']['id']
    replied_message_id = reply_message['message_id']
    if chat_id not in recitation_exercises or replied_user_id not in recitation_exercises[chat_id]:
        return False
    if recitation_exercises[chat_id][replied_user_id]['message_id'] != replied_message_id:
        return False

    text = message.get('text', '').lower()
    score_pattern = r'\b(عالی|خوب|بد)\b'
    match = re.search(score_pattern, text, re.IGNORECASE)
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
        return True
    return False

def generate_exercise_report(chat_id, immediate=False):
    """تولید گزارش تمرین‌ها"""
    global quote_index
    report = f"📋 گزارش تمرین تلاوت\n📅 {get_week_day()} {get_jalali_date()}\n\n"
    if is_exercise_day(chat_id):
        report += "🟢 امروز روز تمرین است\n"
    elif is_scoring_day():
        report += "🔵 امروز روز نمره‌دهی است\n"
    else:
        report += "🔴 امروز روز استراحت است\n"

    admin_ids = {admin['user']['id'] for admin in get_chat_administrators(chat_id)}
    sent_exercises = []
    waiting_exercises = []

    for user_id, user_data in known_members.get(chat_id, {}).items():
        if user_id in admin_ids:
            continue
        user_name = user_data['name']
        if chat_id in recitation_exercises and user_id in recitation_exercises[chat_id]:
            exercise = recitation_exercises[chat_id][user_id]
            if exercise['status'] == 'sent' and exercise['exercise_day'] == get_week_day():
                sent_exercises.append(f"✅ {user_name}")
            else:
                waiting_exercises.append(f"❌ {user_name}")
        else:
            waiting_exercises.append(f"❌ {user_name}")

    if sent_exercises:
        report += "📤 تمرین‌های ارسال‌شده:\n" + "\n".join(sent_exercises) + "\n\n"
    if waiting_exercises:
        report += "⏳ در انتظار تمرین:\n" + "\n".join(waiting_exercises) + "\n\n"

    total = len(known_members.get(chat_id, {})) - len(admin_ids)
    sent_count = len(sent_exercises)
    participation = (sent_count / total * 100) if total > 0 else 0
    report += f"📊 آمار:\n👥 کل اعضا: {total}\n📤 تمرین فرستاده: {sent_count}\n📈 درصد مشارکت: {participation:.1f}%\n"
    if immediate:
        report += f"\n💡 پیام انگیزشی:\n{motivational_quotes[quote_index]}"
        quote_index = (quote_index + 1) % len(motivational_quotes)
    return report

def get_simple_members_list(chat_id):
    """تهیه لیست اعضا به‌صورت زیبا"""
    admin_ids = {admin['user']['id'] for admin in get_chat_administrators(chat_id)}
    admin_names = sorted([get_simple_name(admin['user']) for admin in get_chat_administrators(chat_id)])
    regular_members = sorted([user_info['name'] for user_id, user_info in known_members.get(chat_id, {}).items() if user_id not in admin_ids])

    report = f"📋 لیست اعضا\n📅 {get_week_day()} {get_jalali_date()}\n\n"
    report += "👑 ادمین‌ها:\n" + "\n".join([f"• {name}" for name in admin_names]) + "\n\n"
    report += "👥 قرآن‌آموزان:\n" + "\n".join([f"{i}. {name}" for i, name in enumerate(regular_members, 1)]) + "\n\n"
    report += f"📊 آمار:\n👑 ادمین‌ها: {len(admin_names)}\n👥 قرآن‌آموزان: {len(regular_members)}"
    return report

def is_admin(user_id, chat_id):
    """بررسی ادمین بودن کاربر"""
    return user_id in {admin['user']['id'] for admin in get_chat_administrators(chat_id)}

def process_new_chat_member(message):
    """پردازش عضو جدید"""
    chat_id = message['chat']['id']
    for new_member in message.get('new_chat_members', []):
        user_id = new_member.get('id')
        if not is_admin(user_id, chat_id):
            add_known_member(new_member, chat_id)
            welcome_msg = f"🎉 {get_simple_name(new_member)}، به گروه خوش آمدید!\nلطفاً برای ثبت در لیست، /عضو بزنید."
            send_message(chat_id, welcome_msg)

def process_message(message):
    """پردازش پیام‌ها"""
    chat_id = message['chat']['id']
    chat_type = message['chat']['type']
    user_info = message['from']
    user_id = user_info.get('id')

    if chat_type not in ['group', 'supergroup']:
        send_message(chat_id, "این ربات فقط در گروه‌ها کار می‌کند!")
        return

    add_known_member(user_info, chat_id)
    schedule_report(chat_id)

    if 'text' in message:
        text = message['text'].strip().lower()
        is_admin_user = is_admin(user_id, chat_id)

        if text == '/شروع' and is_admin_user:
            msg = "🤖 ربات تلاوت\n\n"
            msg += "دستورات:\n👥 /عضو - ثبت در گروه\n📋 /لیست - لیست اعضا\n🎯 /گزارش - گزارش تمرین‌ها\n🏆 /نمرات - گزارش نمرات\n\n"
            msg += "📅 روزهای تمرین: شنبه، دوشنبه، چهارشنبه (تا ۲۳:۵۹)\n🔍 روزهای نمره‌دهی: یکشنبه، سه‌شنبه، پنج‌شنبه\n"
            msg += f"📅 امروز: {get_week_day()} {get_jalali_date()}"
            send_message(chat_id, msg)
        elif text == '/عضو' and not is_admin_user:
            send_message(chat_id, f"🎉 {get_simple_name(user_info)}، ثبت شدید!\n" + get_simple_members_list(chat_id))
        elif text == '/لیست':
            send_message(chat_id, get_simple_members_list(chat_id))
        elif is_admin_user and text == '/گزارش':
            send_message(chat_id, generate_exercise_report(chat_id))
        elif is_admin_user and text == '/نمرات':
            report = f"🏆 گزارش نمرات\n📅 {get_week_day()} {get_jalali_date()}\n\n"
            admin_ids = {admin['user']['id'] for admin in get_chat_administrators(chat_id)}
            excellent, good, bad, no_exercise = [], [], [], []
            for user_id, user_data in known_members.get(chat_id, {}).items():
                if user_id in admin_ids:
                    continue
                user_name = user_data['name']
                if user_id in exercise_scores.get(chat_id, {}) and exercise_scores[chat_id][user_id]:
                    last_score = exercise_scores[chat_id][user_id][-1]['score']
                    if last_score == 'عالی':
                        excellent.append(user_name)
                    elif last_score == 'خوب':
                        good.append(user_name)
                    elif last_score == 'بد':
                        bad.append(user_name)
                else:
                    no_exercise.append(user_name)
            if excellent:
                report += "🌟 عالی:\n" + "\n".join([f"{i}. {name}" for i, name in enumerate(sorted(excellent), 1)]) + "\n\n"
            if good:
                report += "👍 خوب:\n" + "\n".join([f"{i}. {name}" for i, name in enumerate(sorted(good), 1)]) + "\n\n"
            if bad:
                report += "👎 بد:\n" + "\n".join([f"{i}. {name}" for i, name in enumerate(sorted(bad), 1)]) + "\n\n"
            if no_exercise:
                report += "❌ بدون تمرین:\n" + "\n".join([f"{i}. {name}" for i, name in enumerate(sorted(no_exercise), 1)])
            send_message(chat_id, report)

def main():
    """تابع اصلی ربات"""
    logging.info("ربات تلاوت شروع شد...")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            if updates and updates.get('ok'):
                for update in updates.get('result', []):
                    if 'message' in update:
                        process_message(update['message'])
                        process_new_chat_member(update['message'])
                        handle_recitation_exercise(update['message'])
                        handle_admin_score(update['message'])
                    offset = update['update_id'] + 1
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"خطا: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()