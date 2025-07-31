import os
import json
import time
import re
import logging
import requests

# 📌 پیکربندی اولیه
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
DATA_FILE = "1.json"

logging.basicConfig(level=logging.INFO)

# 🧠 بارگذاری یا ایجاد فایل داده‌ها
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 🎯 ارسال پیام همراه با کیبورد
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=payload)

# 🎛️ ساخت کیبورد معمولی
def make_keyboard(buttons):
    return {"keyboard": [[{"text": b} for b in row] for row in buttons], "resize_keyboard": True}

# 🧊 ساخت کیبورد شیشه‌ای
def make_inline_keyboard(buttons):
    return {"inline_keyboard": buttons}

# ✅ بررسی اعتبار کد ملی
def is_valid_national_id(nid):
    return bool(re.fullmatch(r"\d{10}", nid))

# 🧠 مدیریت وضعیت کاربر در حافظه
user_states = {}  # برای ذخیره وضعیت موقت کاربران در حافظه (رم)

# 🔁 مدیریت هر آپدیت
def handle_update(update):
    global user_states
    user_data = load_data()  # بارگذاری اطلاعات از فایل JSON

    if "message" in update:
        message = update["message"]
        text = message.get("text", "")
        chat_id = message["chat"]["id"]
        user_id = str(chat_id)
        contact = message.get("contact")

        # مرحله: شروع یا شروع مجدد
        if text == "/start" or text == "شروع مجدد":
            user_states[user_id] = {}  # پاک کردن وضعیت موقت در حافظه
            if user_id in user_data and "full_name" in user_data[user_id]:
                first_name = user_data[user_id]["first_name"]
                full_name = user_data[user_id]["full_name"]
                national_id = user_data[user_id].get("national_id", "هنوز مانده")
                phone = user_data[user_id].get("phone", "هنوز مانده")
                
                send_message(
                    chat_id,
                    f"_🌟 {first_name} عزیز، خوش آمدی!\n"
                    f"حساب کاربری شما آماده است 👇_\n"
                    f"*نام*: {full_name}\n"
                    f"*کد ملی*: {national_id}\n"
                    f"*تلفن*: {phone}",
                    reply_markup=make_inline_keyboard([
                        [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}],
                        [{"text": "📚 انتخاب کلاس", "callback_data": "choose_class"}]
                    ])
                )
            else:
                send_message(
                    chat_id,
                    "_🌟 خوش آمدید! به ربات ثبت‌نام آموزشگاه خوش آمدید!_\n"
                    "برای شروع ثبت‌نام روی دکمه زیر بزنید:",
                    reply_markup=make_inline_keyboard([
                        [{"text": "📝 شروع ثبت‌نام", "callback_data": "start_registration"}]
                    ])
                )
        
        # مدیریت مراحل ثبت‌نام
        elif user_id in user_states:
            state = user_states[user_id]
            
            # مرحله: نام
            if "full_name" not in state:
                state["full_name"] = text
                state["first_name"] = text.split()[0]
                send_message(
                    chat_id,
                    f"_{state['first_name']} عزیز،\nنام شما: {text}\nکد ملی: هنوز مانده\nتلفن: هنوز مانده_\n\nلطفاً کد ملی ۱۰ رقمی خود را وارد کنید.",
                    reply_markup=make_keyboard([["شروع مجدد", "خروج", "برگشت به قبل"]])
                )
                send_message(
                    chat_id,
                    "می‌خواهید نام را ویرایش کنید؟",
                    reply_markup=make_inline_keyboard([[{"text": "✏️ تصحیح نام", "callback_data": "edit_name"}]])
                )
            
            # مرحله: کد ملی
            elif "national_id" not in state:
                if is_valid_national_id(text):
                    state["national_id"] = text
                    send_message(
                        chat_id,
                        f"_{state['first_name']} عزیز،\nنام شما: {state['full_name']}\nکد ملی: {text}\nتلفن: هنوز مانده_\n\n📱 لطفاً شماره تلفن خود را با دکمه زیر ارسال کنید.",
                        reply_markup=make_keyboard([["شروع مجدد", "خروج", "برگشت به قبل"]])
                    )
                    send_message(
                        chat_id,
                        "👇👇👇",
                        reply_markup={
                            "keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]],
                            "resize_keyboard": True
                        }
                    )
                else:
                    send_message(chat_id, "_❌ کد ملی نامعتبر است. لطفاً ۱۰ رقم وارد کنید._")
            
            # مرحله: شماره تلفن
            elif "phone" not in state and contact:
                state["phone"] = contact["phone_number"]
                send_message(
                    chat_id,
                    f"_📋 {state['first_name']} عزیز، حساب کاربری شما:\nنام: {state['full_name']}\nکد ملی: {state['national_id']}\nتلفن: {state['phone']}_",
                    reply_markup=make_inline_keyboard([
                        [{"text": "✅ تأیید نهایی", "callback_data": "final_confirm"}],
                        [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}]
                    ])
                )

    elif "callback_query" in update:
        query = update["callback_query"]
        data = query["data"]
        chat_id = query["message"]["chat"]["id"]
        user_id = str(chat_id)

        if data == "start_registration":
            user_states[user_id] = {}
            send_message(chat_id, "_لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی)._")
        
        elif data == "edit_name":
            user_states[user_id].pop("full_name", None)
            send_message(chat_id, "_نام جدید را وارد کنید._")
        
        elif data == "edit_info":
            user_states[user_id] = {}
            send_message(chat_id, "_بیایید دوباره شروع کنیم. لطفاً نام و نام خانوادگی خود را وارد کنید._")
        
        elif data == "final_confirm":
            user_data[user_id] = user_states[user_id]  # ذخیره اطلاعات در فایل JSON فقط هنگام تأیید نهایی
            save_data(user_data)
            send_message(
                chat_id,
                f"🎉 {user_states[user_id]['first_name']} عزیز، ثبت‌نام شما با موفقیت تکمیل شد! موفق باشید!",
                reply_markup=make_inline_keyboard([
                    [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}],
                    [{"text": "📚 انتخاب کلاس", "callback_data": "choose_class"}]
                ])
            )
            user_states[user_id] = {}  # پاک کردن وضعیت موقت پس از ذخیره

# ♻️ حلقه اصلی
def main():
    last_update_id = 0
    while True:
        try:
            resp = requests.get(f"{BASE_URL}/getUpdates", params={"offset": last_update_id + 1})
            updates = resp.json().get("result", [])
            for update in updates:
                last_update_id = update["update_id"]
                handle_update(update)
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()