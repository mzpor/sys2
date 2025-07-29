#گروک  ضعسف ساخت . 
#ایراد ها گرفته شد
#شروع خوب نیست دکمه های معمولی دیر میاد. 

import jdatetime
import requests
import json
import time
import re
import logging
import os
import sys

# تنظیم لاگینگ برای گزارش‌های انگلیسی
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# تنظیمات ربات
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
API_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates"
SEND_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

# فایل ذخیره‌سازی داده‌ها
DATA_FILE = "1.json"
users_data = {}

# بارگذاری داده‌ها از فایل JSON
def load_data():
    """بارگذاری داده‌ها از فایل JSON"""
    global users_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        logging.info("Data loaded from JSON file")
    else:
        users_data = {}
        logging.info("No data file found, starting with empty data")

# ذخیره داده‌ها در فایل JSON
def save_data():
    """ذخیره داده‌ها در فایل JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)
    logging.info("Data saved to JSON file")

# ارسال پیام
def send_message(chat_id, text, reply_markup=None):
    """ارسال پیام به کاربر با استفاده از API بله"""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup
    }
    response = requests.post(SEND_URL, json=payload)
    logging.info(f"Message sent to {chat_id}: {text}")
    return response.json()

# کیبورد معمولی اصلی
def main_keyboard():
    """کیبورد معمولی برای گزینه‌های ثابت"""
    return {
        "keyboard": [
            [{"text": "شروع مجدد"}, {"text": "معرفی آموزشگاه"}, {"text": "خروج"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

# کیبورد معمولی برای مراحل
def step_keyboard():
    """کیبورد معمولی برای مراحل ثبت‌نام"""
    return {
        "keyboard": [
            [{"text": "شروع مجدد"}, {"text": "خروج"}, {"text": "برگشت به قبل"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

# اعتبارسنجی کد ملی
def validate_national_id(national_id):
    """اعتبارسنجی کد ملی ۱۰ رقمی"""
    if not national_id:
        return False, "کد ملی خالی است"
    if re.match(r'^\d{10}$', national_id):
        return True, national_id
    return False, "کد ملی نامعتبر است. باید ۱۰ رقم باشد."

# اعتبارسنجی شماره تلفن
def validate_phone_number(phone_number):
    """اعتبارسنجی شماره تلفن با فرمت بله"""
    if not phone_number:
        return False, "شماره تلفن خالی است"
    else: #re.match(r'^\98\d{10}$', phone_number) and len(phone_number) == 12:
        return True, phone_number
    return False, "شماره تلفن نامعتبر است. باید با 98 شروع شود و 12 کاراکتر باشد."

# پردازش پیام‌ها
def process_message(message):
    """پردازش پیام‌های دریافتی از کاربر"""
    chat_id = message['chat']['id']
    user_id = str(message['from']['id'])
    text = message.get('text', '')
    contact = message.get('contact', None)

    # بارگذاری داده‌ها
    load_data()

    # اگر کاربر جدید است
    if user_id not in users_data:
        users_data[user_id] = {"step": "start"}
        save_data()

    # مرحله شروع
    if text == "/start":
        users_data[user_id]["step"] = "start"
        save_data()
        message_text = "🌟 خوش آمدید! به ربات ثبت‌نام آموزشگاه خوش آمدید!"
        reply_markup = {
            "keyboard": main_keyboard()["keyboard"],
            "inline_keyboard": [[{"text": "📝 شروع ثبت‌نام", "callback_data": "start_registration"}]]
        }
        send_message(chat_id, message_text, reply_markup)
        logging.info(f"User {user_id} started the bot")
        return

    # پردازش مراحل ثبت‌نام
    if users_data[user_id]["step"] == "waiting_name" and text not in ["شروع مجدد", "خروج", "برگشت به قبل"]:
        full_name = text.strip()
        first_name = full_name.split()[0] if full_name.split() else ""
        users_data[user_id] = {
            "full_name": full_name,
            "first_name": first_name,
            "step": "waiting_national_id"
        }
        save_data()
        message_text = (f"{first_name} عزیز،\n"
                        f"نام شما: {full_name}\n"
                        f"کد ملی: هنوز مانده\n"
                        f"تلفن: هنوز مانده")
        reply_markup = {
            "keyboard": step_keyboard()["keyboard"],
            "inline_keyboard": [
                [{"text": "✏️ تصحیح نام", "callback_data": "edit_name"},
                 {"text": "📍 وارد کردن کد ملی", "callback_data": "enter_national_id"}]
            ]
        }
        send_message(chat_id, message_text, reply_markup)
        logging.info(f"User {user_id} entered name: {full_name}")
        return

    # پردازش کد ملی
    if users_data[user_id]["step"] == "waiting_national_id_input" and text not in ["شروع مجدد", "خروج", "برگشت به قبل"]:
        is_valid, result = validate_national_id(text)
        if is_valid:
            users_data[user_id]["national_id"] = result
            users_data[user_id]["step"] = "waiting_phone"
            save_data()
            message_text = (f"{users_data[user_id]['first_name']} عزیز،\n"
                            f"نام شما: {users_data[user_id]['full_name']}\n"
                            f"کد ملی: {result}\n"
                            f"تلفن: هنوز مانده")
            reply_markup = {
                "keyboard": step_keyboard()["keyboard"],
                "inline_keyboard": [
                    [{"text": "✏️ تصحیح کد ملی", "callback_data": "edit_national_id"},
                     {"text": "📱 ارسال تلفن", "callback_data": "send_phone"}]
                ]
            }
            send_message(chat_id, message_text, reply_markup)
            logging.info(f"User {user_id} entered national ID: {result}")
        else:
            send_message(chat_id, result)
            logging.error(f"Invalid national ID for user {user_id}: {text}")
        return

    # پردازش شماره تلفن
    if contact and users_data[user_id]["step"] == "waiting_phone":
        mobile = contact.get('phone_number', '')
        is_valid, result = validate_phone_number(mobile)
        if is_valid:
            users_data[user_id]["phone"] = result
            users_data[user_id]["step"] = "final_confirmation"
            save_data()
            message_text = (f"📋 {users_data[user_id]['first_name']} عزیز، حساب کاربری شما:\n"
                            f"نام: {users_data[user_id]['full_name']}\n"
                            f"کد ملی: {users_data[user_id]['national_id']}\n"
                            f"تلفن: {result[1:]} \n"
                            f"آیا اطلاعات درست است؟")
            reply_markup = {
                "keyboard": step_keyboard()["keyboard"],
                "inline_keyboard": [
                    [{"text": "✅ تأیید نهایی", "callback_data": "final_confirm"},
                     {"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}]
                ]
            }
            send_message(chat_id, message_text, reply_markup)
            logging.info(f"User {user_id} entered phone: {result}")
        else:
            send_message(chat_id, result, reply_markup={"inline_keyboard": [[{"text": "📱 ارسال تلفن", "callback_data": "send_phone"}]]})
            logging.error(f"Invalid phone number for user {user_id}: {mobile}")
        return

    # مدیریت دستورات کیبورد معمولی
    if text == "شروع مجدد":
        users_data[user_id] = {"step": "start"}
        save_data()
        process_message({"chat": {"id": chat_id}, "from": {"id": user_id}, "text": "/start"})
        return
    if text == "خروج":
        send_message(chat_id, "🙏 با تشکر از شما، از ربات خارج شدید.", reply_markup={"remove_keyboard": True})
        logging.info(f"User {user_id} exited")
        return
    if text == "برگشت به قبل" and users_data[user_id]["step"] != "start":
        if users_data[user_id]["step"] == "waiting_national_id":
            users_data[user_id]["step"] = "waiting_name"
            save_data()
            send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی).", reply_markup=step_keyboard())
        elif users_data[user_id]["step"] == "waiting_phone":
            users_data[user_id]["step"] = "waiting_national_id"
            save_data()
            send_message(chat_id, f"{users_data[user_id]['first_name']} عزیز، لطفاً کد ملی ۱۰ رقمی خود را وارد کنید.", reply_markup=step_keyboard())
        logging.info(f"User {user_id} went back to previous step")
        return

# پردازش callbackها
def process_callback_query(callback_query):
    """پردازش callbackهای کیبورد شیشه‌ای"""
    chat_id = callback_query['message']['chat']['id']
    user_id = str(callback_query['from']['id'])
    data = callback_query['data']

    load_data()

    if user_id not in users_data:
        users_data[user_id] = {"step": "start"}
        save_data()

    if data == "start_registration":
        users_data[user_id]["step"] = "waiting_name"
        save_data()
        send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی).", reply_markup=step_keyboard())
        logging.info(f"User {user_id} started registration")
        return

    if data == "edit_name":
        users_data[user_id]["step"] = "waiting_name"
        save_data()
        send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی).", reply_markup=step_keyboard())
        logging.info(f"User {user_id} requested to edit name")
        return

    if data == "enter_national_id":
        users_data[user_id]["step"] = "waiting_national_id_input"
        save_data()
        send_message(chat_id, f"{users_data[user_id]['first_name']} عزیز، لطفاً کد ملی ۱۰ رقمی خود را وارد کنید.", reply_markup=step_keyboard())
        logging.info(f"User {user_id} requested to enter national ID")
        return

    if data == "edit_national_id":
        users_data[user_id]["step"] = "waiting_national_id_input"
        save_data()
        send_message(chat_id, f"{users_data[user_id]['first_name']} عزیز، لطفاً کد ملی ۱۰ رقمی خود را وارد کنید.", reply_markup=step_keyboard())
        logging.info(f"User {user_id} requested to edit national ID")
        return

    if data == "send_phone":
        users_data[user_id]["step"] = "waiting_phone"
        save_data()
        message_text = f"{users_data[user_id]['first_name']} عزیز، لطفاً برای ارسال شماره تلفن خود روی دکمه زیر بزنید."
        reply_markup = {
            "keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        send_message(chat_id, message_text, reply_markup)
        logging.info(f"User {user_id} requested to send phone")
        return

    if data == "final_confirm":
        users_data[user_id]["step"] = "completed"
        save_data()
        send_message(chat_id, f"🎉 {users_data[user_id]['first_name']} عزیز، ثبت‌نام شما با موفقیت تکمیل شد! موفق باشید!", reply_markup=main_keyboard())
        logging.info(f"User {user_id} completed registration")
        return

    if data == "edit_info":
        users_data[user_id] = {"step": "waiting_name"}
        save_data()
        send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی).", reply_markup=step_keyboard())
        logging.info(f"User {user_id} requested to edit all info")
        return

# حلقه اصلی ربات
def main():
    """حلقه اصلی برای دریافت به‌روزرسانی‌ها"""
    offset = 0
    while True:
        try:
            response = requests.get(f"{API_URL}?offset={offset}&timeout=30").json()
            if not response.get("ok"):
                logging.error(f"API error: {response}")
                time.sleep(5)
                continue

            for update in response.get("result", []):
                offset = update["update_id"] + 1
                if "message" in update:
                    process_message(update["message"])
                elif "callback_query" in update:
                    process_callback_query(update["callback_query"])
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    logging.info("Bot started")
    main()