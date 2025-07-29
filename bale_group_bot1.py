# گروک
import jdatetime  # برای کار با تاریخ شمسی
import requests  # برای ارتباط با API بله
import json      # برای کار با داده‌های JSON
import time      # برای کار با زمان
import re       # برای کار با عبارات منظم
import logging   # برای ثبت گزارش‌ها
import os       # برای بررسی وجود فایل
import sys      # برای مدیریت سیستم

# تنظیمات لاگ‌گذاری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot.log',
    filemode='a'
)

# توکن‌ها و آدرس‌های پایه
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
PAYMENT_TOKEN = "WALLET-LIiCzxGZnCd58Obr"
API_URL = f'https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates'
SEND_URL = f'https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage'
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
WEEKDAY_MAP = {
    0: 'شنبه',
    1: 'یک‌شنبه',
    2: 'دوشنبه',
    3: 'سه‌شنبه',
    4: 'چهارشنبه',
    5: 'پنج‌شنبه',
    6: 'جمعه'
}

# مسیر فایل‌های ذخیره‌سازی
DATA_FILE = "bot_data.json"

# داده‌های اولیه کلاس‌ها و لینک‌های پرداخت
CLASSES = {
    "quran_recitation": {
        "name": "رشت بری",
        "price": "1,000 تومان",
        "schedule": "شنبه‌ها و سه‌شنبه‌ها ساعت 18:00"
    },
    "tajvid": {
        "name": "جاجی زاده",
        "price": "1,000 تومان",
        "schedule": "یکشنبه‌ها و چهارشنبه‌ها ساعت 20:00"
    }
}
PAYMENT_LINKS = {
    "rasht": "ble.ir/join/Gah9cS9LzQ",
    "hajizade": "ble.ir/join/Gah9cS9LzQ"
}

# ساختار داده برای ذخیره اطلاعات
bot_data = {
    "admin": None,  # اطلاعات مدیر
    "coaches": {},  # اطلاعات مربی‌ها
    "assistant_coaches": {},  # اطلاعات کمک مربی‌ها
    "students": {},  # اطلاعات قرآن‌آموزان
    "classes": CLASSES,  # اطلاعات کلاس‌ها
    "payment_links": PAYMENT_LINKS  # لینک‌های پرداخت
}

# تابع برای بارگذاری داده‌ها از فایل
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return bot_data

# تابع برای ذخیره داده‌ها در فایل
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info("Data saved to file")

# تابع برای ارسال پیام
def send_message(chat_id, text, reply_markup=None):
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    response = requests.post(SEND_URL, json=payload)
    if response.status_code == 200:
        logging.info(f"Message sent to {chat_id}: {text}")
    else:
        logging.error(f"Failed to send message to {chat_id}: {response.text}")

# تابع برای دریافت تاریخ شمسی
def get_persian_date():
    date = jdatetime.datetime.now()
    weekday = WEEKDAY_MAP[date.weekday()]
    return f"{weekday} {date.day} {date.jmonth_name()}"

# تابع برای مدیریت پیوستن به گروه
def handle_new_group_join(chat_id):
    message = "👋 Hello! Welcome dear Quran students 🌟\nPlease make me an admin to use all features. Thank you!"
    send_message(chat_id, message)
    logging.info(f"Bot joined group {chat_id}")

# تابع برای بررسی به‌روزرسانی‌ها
def get_updates(offset=None):
    params = {'offset': offset} if offset else {}
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json().get('result', [])
    logging.error(f"Failed to get updates: {response.text}")
    return []

# تابع برای تولید کیبورد شیشه‌ای
def create_inline_keyboard(buttons):
    return {'inline_keyboard': [buttons]}

# تابع برای تولید کیبورد معمولی
def create_reply_keyboard(buttons):
    return {'keyboard': [buttons], 'resize_keyboard': True, 'one_time_keyboard': True}

# تابع اصلی مدیریت ربات
def main():
    global bot_data
    bot_data = load_data()  # بارگذاری داده‌ها
    offset = None

    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update['update_id'] + 1
                process_update(update)
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            time.sleep(5)

# تابع پردازش به‌روزرسانی‌ها
def process_update(update):
    if 'message' in update:
        message = update['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        text = message.get('text', '')

        # بررسی پیوستن به گروه
        if 'new_chat_member' in message and message['new_chat_member']['id'] == bot_id():
            handle_new_group_join(chat_id)
            return

        # بررسی وضعیت ادمین
        if is_bot_admin(chat_id):
            handle_admin_features(chat_id, user_id, text)
        else:
            send_message(chat_id, "Please make me an admin to use all features.")

        # مدیریت چت خصوصی
        if message['chat']['type'] == 'private':
            handle_private_chat(chat_id, user_id, text)

# تابع بررسی ادمین بودن ربات
def is_bot_admin(chat_id):
    url = f"{BASE_URL}/getChatAdministrators"
    response = requests.get(url, params={'chat_id': chat_id})
    if response.status_code == 200:
        admins = response.json().get('result', [])
        return any(admin['user']['id'] == bot_id() for admin in admins)
    return False

# تابع دریافت آیدی ربات
def bot_id():
    response = requests.get(f"{BASE_URL}/getMe")
    if response.status_code == 200:
        return response.json()['result']['id']
    return None

# تابع مدیریت چت خصوصی
def handle_private_chat(chat_id, user_id, text):
    global bot_data

    # بررسی مدیر جدید
    if not bot_data['admin']:
        bot_data['admin'] = {'id': user_id, 'state': 'awaiting_name'}
        save_data(bot_data)
        send_message(chat_id, "Please enter your first name and last name:")
        return

    # مدیریت حالت‌های مدیر
    if bot_data['admin'] and bot_data['admin']['id'] == user_id:
        if bot_data['admin'].get('state') == 'awaiting_name':
            if re.match(r'^[\u0600-\u06FF\s]+$', text):  # بررسی حروف فارسی
                bot_data['admin']['name'] = text
                bot_data['admin']['state'] = 'confirm_name'
                save_data(bot_data)
                buttons = create_inline_keyboard([{'text': 'Confirm', 'callback_data': 'confirm_admin_name'}])
                send_message(chat_id, f"Is this your name: {text}?", buttons)
            else:
                send_message(chat_id, "Please enter a valid name in Persian.")
        return

    # انتخاب نقش کاربر
    if text == '/start':
        buttons = create_reply_keyboard(['Coach', 'Assistant Coach', 'Quran Student'])
        send_message(chat_id, "Please select your role:", buttons)

    # مدیریت نقش‌ها
    elif text in ['Coach', 'Assistant Coach']:
        handle_coach_registration(chat_id, user_id, text)
    elif text == 'Quran Student':
        handle_student_registration(chat_id, user_id)

# تابع مدیریت ثبت‌نام مربی
def handle_coach_registration(chat_id, user_id, role):
    import random
    code = random.randint(1000, 9999)
    bot_data['coaches'][str(user_id)] = {'role': role, 'state': 'awaiting_code', 'code': code}
    save_data(bot_data)
    send_message(bot_data['admin']['id'], f"New {role} registration request. Confirmation code: {code}")
    send_message(chat_id, f"Please enter the confirmation code sent to the admin:")

# تابع مدیریت ثبت‌نام قرآن‌آموز
def handle_student_registration(chat_id, user_id):
    bot_data['students'][str(user_id)] = {'state': 'check_channel'}
    save_data(bot_data)
    buttons = create_inline_keyboard([{'text': 'Join Channel', 'url': 'https://ble.ir/join/school_channel'}])
    send_message(chat_id, "Welcome! Please join our channel first:", buttons)

# تابع مدیریت ویژگی‌های ادمین
def handle_admin_features(chat_id, user_id, text):
    if text == '/عضو':
        update_student_list(chat_id)
    elif text == 'شروع مجدد':
        bot_data = load_data()
        send_message(chat_id, "Bot restarted.")
    elif text == 'پنل کاربری':
        show_admin_panel(chat_id, user_id)

# تابع نمایش پنل مدیریتی
def show_admin_panel(chat_id, user_id):
    student_list = "\n".join([f"{s['name']} - {s['phone']}" for s in bot_data['students'].values() if 'name' in s])
    class_list = "\n".join([f"{k}: {v['name']} - {v['price']}" for k, v in bot_data['classes'].items()])
    message = f"Admin Panel:\n\nStudents:\n{student_list}\n\nClasses:\n{class_list}"
    send_message(chat_id, message)

# تابع به‌روزرسانی لیست قرآن‌آموزان
def update_student_list(chat_id):
    student_list = "\n".join([f"{s['name']} - {s['phone']}" for s in bot_data['students'].values() if 'name' in s])
    message = f"Quran Students:\n{student_list}\n\nTo join the class, click /عضو"
    send_message(chat_id, message)
    for coach_id in bot_data['coaches']:
        send_message(coach_id, f"Updated student list:\n{student_list}")

# اجرای ربات
if __name__ == "__main__":
    logging.info("Bot started")
    main()