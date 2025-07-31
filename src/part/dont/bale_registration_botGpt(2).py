import os
import sys
import json
import time
import re
import logging
import requests

BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
DATA_FILE = "1.json"

# بارگذاری داده‌ها از فایل
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)
else:
    user_data = {}

# ذخیره‌سازی داده‌ها
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

# ارسال پیام متنی
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=payload)

# ساخت کیبورد معمولی
def make_keyboard(buttons):
    return {
        "keyboard": [[{"text": b} for b in row] for row in buttons],
        "resize_keyboard": True
    }

# ساخت کیبورد شیشه‌ای
def make_inline_keyboard(buttons):
    return {
        "inline_keyboard": buttons
    }

# بررسی اعتبار کد ملی
def is_valid_national_id(nid):
    return bool(re.fullmatch(r"\d{10}", nid))

# بررسی وضعیت هر کاربر
user_state = {}

def handle_update(update):
    message = update.get("message", {})
    callback = update.get("callback_query", {})
    contact = message.get("contact")
    chat_id = message.get("chat", {}).get("id") or callback.get("message", {}).get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id") or callback.get("from", {}).get("id")
    text = message.get("text") or callback.get("data")

    if callback:
        data = callback["data"]
        if data == "start_registration":
            user_state[user_id] = {}
            send_message(chat_id, "_لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی)._")
        elif data == "edit_info":
            user_state[user_id] = {}
            send_message(chat_id, "_لطفاً اطلاعات خود را از نو وارد کنید. ابتدا نام و نام خانوادگی را وارد نمایید._")
        return

    # مرحله ۱: شروع
    if text in ["/start", "شروع مجدد"]:
        if user_id in user_data and "full_name" in user_data[user_id]:
            u = user_data[user_id]
            send_message(chat_id,
                f"_🌟 {u['first_name']} عزیز، خوش آمدی!\nحساب کاربری شما آماده است 👇_\n"
                f"*نام*: {u['full_name']}\n*کد ملی*: {u.get('national_id', 'هنوز مانده')}\n*تلفن*: {u.get('phone', 'هنوز مانده')}",
                reply_markup=make_inline_keyboard([
                    [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}],
                    [{"text": "📚 انتخاب کلاس", "callback_data": "choose_class"}]
                ])
            )
        else:
            send_message(chat_id, "_🌟 خوش آمدید! به ربات ثبت‌نام آموزشگاه خوش آمدید!_",
                reply_markup=make_keyboard([["شروع مجدد", "معرفی آموزشگاه", "خروج"]])
            )
            send_message(chat_id, "برای شروع ثبت‌نام روی دکمه زیر بزنید:",
                reply_markup=make_inline_keyboard(
                    [[{"text": "📝 شروع ثبت‌نام", "callback_data": "start_registration"}]]
                )
            )
        return

    # مراحل ثبت‌نام
    state = user_state.get(user_id, {})

    # مرحله ۲: نام
    if "full_name" not in state:
        state["full_name"] = text
        state["first_name"] = text.split()[0]
        user_state[user_id] = state
        send_message(chat_id,
            f"_{state['first_name']} عزیز،\nنام شما: {state['full_name']}\nکد ملی: هنوز مانده\nتلفن: هنوز مانده_\n\nلطفاً کد ملی ۱۰ رقمی خود را وارد کنی",
            reply_markup=make_keyboard([["شروع مجدد", "خروج", "برگشت به قبل"]])
        )
        send_message(chat_id,
            "می‌خواهید نام را ویرایش کنید؟",
            reply_markup=make_inline_keyboard([[{"text": "✏️ تصحیح نام", "callback_data": "edit_name"}]]))
        return

    # مرحله ۳: کد ملی
    if "national_id" not in state:
        if is_valid_national_id(text):
            state["national_id"] = text
            user_state[user_id] = state
            send_message(chat_id,
                f"_{state['first_name']} عزیز،\nنام شما: {state['full_name']}\nکد ملی: {text}\nتلفن: هنوز مانده_\n\n📱 لطفاً شماره تلفن خود را با دکمه زیر ارسال کنید.",
                reply_markup=make_keyboard([["شروع مجدد", "خروج", "برگشت به قبل"]])
            )
            send_message(chat_id, "👇👇👇",
                reply_markup={
                    "keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]],
                    "resize_keyboard": True
                })
        else:
            send_message(chat_id, "_❌ کد ملی نامعتبر است. لطفاً ۱۰ رقم وارد کنید._")
        return

    # مرحله ۴: شماره تلفن
    if "phone" not in state and contact:
        state["phone"] = contact["phone_number"]
        user_data[user_id] = state
        save_data()
        send_message(chat_id,
            f"_📋 {state['first_name']} عزیز، حساب کاربری شما:\nنام: {state['full_name']}\nکد ملی: {state['national_id']}\nتلفن: {state['phone']}_",
            reply_markup=make_inline_keyboard([
                [{"text": "✅ تأیید نهایی", "callback_data": "final_confirm"}],
                [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}]
            ])
        )
        return

# اجرای حلقه اصلی (برای نمونه)

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
   # print("⏳ در حال اجرا... (شبیه‌سازی)")
     main()
    # در حالت واقعی باید با وب‌هوک یا long-polling اجرا شود
