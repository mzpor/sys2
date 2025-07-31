# -*- coding: utf-8 -*-
import requests
import json
import time
import re
import logging
import os
import sys
import jdatetime

# --- تنظیمات اولیه ---
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
API_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates"
SEND_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
DATA_FILE = "1.json"

# --- تنظیم logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- بارگذاری داده‌ها از فایل ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            return {"admin": {}, "classes": [], "coaches": []}
    else:
        return {"admin": {}, "classes": [], "coaches": []}

# --- ذخیره داده‌ها در فایل ---
def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info("Data saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save data: {e}")

# --- ارسال پیام به کاربر ---
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    try:
        response = requests.post(SEND_URL, json=payload)
        if response.status_code != 200:
            logging.error(f"Send failed: {response.status_code}, {response.text}")
    except Exception as e:
        logging.error(f"Send error: {e}")

# --- ساخت کیبورد معمولی ---
def get_main_keyboard():
    return {
        "keyboard": [
            [{"text": "شروع مجدد"}],
            [{"text": "پنل کاربری"}]
        ],
        "resize_keyboard": True
    }

# --- ساخت کیبورد اینلاین ---
def get_inline_keyboard(buttons):
    # buttons: لیستی از دکمه‌ها مانند [{"text": "تایید", "callback_data": "confirm"}]
    return {"inline_keyboard": [buttons]}

# --- پردازش داده‌های ادمین ---
def handle_admin_registration(chat_id, text, data, state):
    user_data = data["admin"]
    
    if state == "waiting_first_name":
        user_data["first_name"] = text.strip()
        data["admin"] = user_data
        save_data(data)
        send_message(chat_id, "نام خانوادگی خود را وارد کنید:", get_inline_keyboard([]))
        data["admin"]["state"] = "waiting_last_name"
        save_data(data)
    
    elif state == "waiting_last_name":
        user_data["last_name"] = text.strip()
        data["admin"] = user_data
        save_data(data)
        kb = get_inline_keyboard([{"text": "ارسال کد ملی", "callback_data": "enter_national_id"}])
        send_message(chat_id, f"نام شما: {user_data['first_name']} {user_data['last_name']}\nآیا صحیح است؟", kb)
        data["admin"]["state"] = "confirm_name"
        save_data(data)

# --- ارسال درخواست اجازه اپلیکیشن بله ---
def send_app_permission(chat_id):
    permission_link = "https://ble.ir/app_permissions_guide"  # لینک فرضی
    kb = get_inline_keyboard([{"text": "ارسال اجازه", "url": permission_link}])
    send_message(chat_id, "لطفاً اجازه دسترسی اپلیکیشن بله را ارسال کنید:", kb)

# --- پنل کاربری ---
def show_user_panel(chat_id, data):
    msg = "🔐 <b>پنل کاربری مدیر</b>\n\n"
    msg += "🔹 امکانات:\n"
    msg += "• افزودن/ویرایش کلاس‌ها\n"
    msg += "• مدیریت مربی‌ها\n"
    msg += "• تنظیم لینک گروه\n\n"
    msg += "📌 آخرین اعلان: اکنون می‌توانید ربات را به گروه اضافه کنید."

    kb = get_main_keyboard()
    send_message(chat_id, msg, kb)

# --- پردازش کال‌بک‌ها ---
def handle_callback_query(data, callback_query):
    chat_id = callback_query["message"]["chat"]["id"]
    data_str = callback_query["data"]

    if data_str == "enter_national_id":
        send_message(chat_id, "کد ملی خود را وارد کنید:")
        data["admin"]["state"] = "waiting_national_id"
        save_data(data)

    elif data_str == "confirm_register":
        data["admin"]["registered"] = True
        data["admin"]["state"] = "registered"
        save_data(data)
        send_app_permission(chat_id)
        send_message(chat_id, "✅ شما ثبت شدید، این پنل کاربری شماست.")
        show_user_panel(chat_id, data)

    elif data_str == "edit_classes":
        # منوی ویرایش کلاس‌ها
        classes_list = "\n".join([f"📘 {c['name']} - {c['price']} تومان" for c in data["classes"]]) or "هیچ کلاسی وجود ندارد."
        send_message(chat_id, f"📚 لیست کلاس‌ها:\n{classes_list}\n\nبرای افزودن کلاس جدید، نام و هزینه را به صورت زیر ارسال کنید:\nنام کلاس | هزینه")
        data["admin"]["state"] = "adding_class"
        save_data(data)

# --- اصل برنامه ---
def main():
    logging.info("Bot started.")
    data = load_data()
    offset = 0

    while True:
        try:
            response = requests.get(f"{API_URL}?offset={offset}&timeout=30")
            if response.status_code != 200:
                time.sleep(5)
                continue

            updates = response.json().get("result", [])
            
            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message")
                callback_query = update.get("callback_query")

                if callback_query:
                    handle_callback_query(data, callback_query)
                    continue

                if not message or "text" not in message:
                    continue

                chat_id = message["chat"]["id"]
                text = message["text"]
                first_name = message["from"].get("first_name", "")
                user_state = data["admin"].get("state", "start")

                # --- اگر ادمین قبلاً ثبت شده باشد، مستقیماً پنل نمایش داده شود ---
                if data["admin"].get("registered") and chat_id == data["admin"].get("chat_id"):
                    if text == "پنل کاربری":
                        show_user_panel(chat_id, data)
                    elif text == "شروع مجدد":
                        data["admin"] = {"chat_id": chat_id, "state": "waiting_first_name"}
                        save_data(data)
                        send_message(chat_id, "نام خود را وارد کنید:")
                    continue

                # --- اولین ورود یا شروع مجدد ---
                if text == "/start" or text == "شروع مجدد":
                    data["admin"] = {
                        "chat_id": chat_id,
                        "state": "waiting_first_name"
                    }
                    save_data(data)
                    send_message(chat_id, f"سلام {first_name}! لطفاً نام خود را وارد کنید:")
                    continue

                # --- ثبت نام ادمین ---
                if chat_id == data["admin"].get("chat_id"):
                    if user_state == "waiting_first_name":
                        handle_admin_registration(chat_id, text, data, "waiting_first_name")
                    elif user_state == "waiting_last_name":
                        handle_admin_registration(chat_id, text, data, "waiting_last_name")
                    elif user_state == "waiting_national_id":
                        national_id = text.strip()
                        if not re.match(r"^\d{10}$", national_id):
                            send_message(chat_id, "کد ملی نامعتبر است. لطفاً ۱۰ رقم وارد کنید:")
                        else:
                            data["admin"]["national_id"] = national_id
                            kb = get_inline_keyboard([
                                {"text": "✅ تایید", "callback_data": "confirm_register"},
                                {"text": "❌ بازگشت", "callback_data": "enter_national_id"}
                            ])
                            send_message(chat_id, 
                                f"اطلاعات شما:\n"
                                f"نام: {data['admin']['first_name']} {data['admin']['last_name']}\n"
                                f"کد ملی: {national_id}\n\n"
                                f"آیا این اطلاعات صحیح است؟", kb)
                            data["admin"]["state"] = "confirm_registration"
                            save_data(data)
                    elif user_state == "adding_class" and "|" in text:
                        try:
                            name, price = text.split("|", 1)
                            price = int(price.strip())
                            data["classes"].append({"name": name.strip(), "price": price})
                            save_data(data)
                            send_message(chat_id, f"✅ کلاس '{name.strip()}' با هزینه {price} تومان اضافه شد.")
                            show_user_panel(chat_id, data)
                        except:
                            send_message(chat_id, "فرمت نادرست! نام | هزینه")
                    else:
                        send_message(chat_id, "لطفاً دستور معتبر وارد کنید.")

        except Exception as e:
            logging.error(f"Loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()