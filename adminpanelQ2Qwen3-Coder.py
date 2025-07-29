import requests
import json
import os
import logging
import jdatetime
import time
import re

# تنظیمات اولیه
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
API_URL = f"{BASE_URL}/getUpdates"
SEND_URL = f"{BASE_URL}/sendMessage"
DATA_FILE = "1.json"

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# تابع ذخیره داده‌ها
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info("Data saved.")

# تابع بارگذاری داده‌ها
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info("Data loaded.")
        return data
    else:
        logging.info("No data file found. Creating new one.")
        return {"admins": {}, "classes": {}, "trainers": {}}

# ارسال پیام
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    response = requests.post(SEND_URL, json=payload)
    logging.info(f"Message sent to {chat_id}: {text}")

# نمایش پنل اولیه
def show_main_menu(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "شروع مجدد", "callback_data": "restart"}],
            [{"text": "پنل کاربری", "callback_data": "panel"}]
        ]
    }
    send_message(chat_id, "لطفاً گزینه‌ای را انتخاب کنید:", reply_markup=keyboard)

# ثبت‌نام مدیر
def start_registration(chat_id, data):
    data["admins"][str(chat_id)] = {"step": "get_name", "info": {}}
    save_data(data)
    send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید:")

# پردازش ورودی‌ها
def handle_message(chat_id, text, data):
    admin = data["admins"].get(str(chat_id))
    if not admin:
        show_main_menu(chat_id)
        return

    step = admin.get("step")
    info = admin["info"]

    if step == "get_name":
        info["name"] = text
        admin["step"] = "get_national_id"
        save_data(data)
        send_message(chat_id, "لطفاً کد ملی خود را وارد کنید:")

    elif step == "get_national_id":
        if not re.match(r"^\d{10}$", text):
            send_message(chat_id, "کد ملی نامعتبر است. لطفاً مجدداً وارد کنید:")
            return
        info["national_id"] = text
        admin["step"] = "confirm"
        save_data(data)
        send_message(chat_id, f"نام: {info['name']}\nکد ملی: {info['national_id']}\nآیا تأیید می‌کنید؟",
                     reply_markup={
                         "inline_keyboard": [
                             [{"text": "بله", "callback_data": "confirm_yes"}],
                             [{"text": "خیر", "callback_data": "confirm_no"}]
                         ]
                     })

    elif step == "confirmed":
        send_message(chat_id, "شما ثبت شدید، این پنل کاربری شماست.")
        show_admin_panel(chat_id)

# تأیید اطلاعات
def confirm_info(chat_id, data, confirmed):
    admin = data["admins"].get(str(chat_id))
    if not admin:
        return

    if confirmed:
        admin["step"] = "confirmed"
        save_data(data)
        send_message(chat_id, "شما ثبت شدید، این پنل کاربری شماست.")
        send_message(chat_id, "اکنون می‌توانید ربات را به گروه اضافه کنید.")
        show_admin_panel(chat_id)
    else:
        start_registration(chat_id, data)

# نمایش پنل مدیریتی
def show_admin_panel(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "مدیریت کلاس‌ها", "callback_data": "manage_classes"}],
            [{"text": "مدیریت مربی‌ها", "callback_data": "manage_trainers"}],
            [{"text": "ثبت لینک گروه", "callback_data": "set_group_link"}]
        ]
    }
    send_message(chat_id, "به پنل مدیریتی خوش آمدید:", reply_markup=keyboard)

# مدیریت کال‌بک‌ها
def handle_callback(chat_id, callback_data, data):
    if callback_data == "restart":
        start_registration(chat_id, data)
    elif callback_data == "panel":
        show_admin_panel(chat_id)
    elif callback_data == "confirm_yes":
        confirm_info(chat_id, data, True)
    elif callback_data == "confirm_no":
        confirm_info(chat_id, data, False)

# تابع اصلی گوش دادن به پیام‌ها
def main():
    data = load_data()
    last_update_id = 0

    while True:
        try:
            response = requests.get(API_URL)
            updates = response.json().get("result", [])
            for update in updates:
                update_id = update["update_id"]
                if update_id <= last_update_id:
                    continue

                last_update_id = update_id

                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["from"]["id"]
                    text = msg.get("text", "")
                    handle_message(chat_id, text, data)

                elif "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["from"]["id"]
                    callback_data = cb["data"]
                    handle_callback(chat_id, callback_data, data)

        except Exception as e:
            logging.error(f"Error: {e}")

        time.sleep(2)

if __name__ == "__main__":
    main()

    ##   باید فایل رو پاک میکردم تا کار کنه 
    #خیلی گیج میزنه شرط ها خراب ..  فایل باشه . شروع بشه همش پیام میده.. 
    