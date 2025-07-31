import requests
import json

# تنظیمات بات
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

# کاربران مجاز
AUTHORIZED_USER_IDS = [574330749, 1114227010]  # آیدی‌های مجاز
users = [f"کاربر{i+1}" for i in range(10)]  # لیست 10 کاربر
attendance_data = {}  # ذخیره وضعیت‌ها

# تابع ارسال پیام به کاربر
def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": reply_markup
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"پیام به chat_id {chat_id} ارسال شد")
    else:
        print(f"خطا در ارسال پیام: {response.status_code}, {response.text}")

# تابع بررسی دسترسی کاربر
def is_user_authorized(user_id):
    return user_id in AUTHORIZED_USER_IDS

# تابع دریافت آپدیت‌ها
def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"offset": offset} if offset else {}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"خطا در دریافت آپدیت‌ها: {response.status_code}, {response.text}")
        return None

# تابع ایجاد کیبورد شیشه‌ای برای حضور و غیاب
def create_attendance_keyboard():
    keyboard = {"inline_keyboard": []}
    for user in users:
        keyboard["inline_keyboard"].append([
            {"text": "✅ حاضر", "callback_data": f"status_{user}_حاضر"},
            {"text": "🚫 غایب", "callback_data": f"status_{user}_غایب"}
        ])
    return keyboard

# تابع پردازش آپدیت‌ها
def handle_update(update):
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")

        if not is_user_authorized(user_id):
            send_message(chat_id, "❌ شما اجازه دسترسی ندارید!")
            return

        if text == "/start":
            send_message(chat_id, "سلام مربی عزیز 👋\nپنل مدیریتی:", 
                        {"inline_keyboard": [[{"text": "📋 حضور و غیاب", "callback_data": "start_attendance"}]]})
            print(f"پنل مدیریتی برای user_id {user_id} ارسال شد")

    elif "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        user_id = callback["from"]["id"]
        callback_data = callback["data"]

        if not is_user_authorized(user_id):
            send_message(chat_id, "❌ شما اجازه دسترسی ندارید!")
            return

        if callback_data == "start_attendance":
            send_message(chat_id, "📋 لیست کاربران:\n" + "\n".join(users), create_attendance_keyboard())
            print(f"لیست حضور و غیاب برای user_id {user_id} ارسال شد")

        elif callback_data.startswith("status_"):
            _, user, status = callback_data.split("_")
            attendance_data[user] = status
            send_message(chat_id, f"✔ وضعیت {user} ثبت شد: {status}")
            print(f"وضعیت {user} به {status} برای user_id {user_id} ثبت شد")

# حلقه اصلی
def main():
    offset = 0
    print("بات شروع به کار کرد...")
    while True:
        updates = get_updates(offset)
        if updates and updates.get("ok") and updates.get("result"):
            for update in updates["result"]:
                offset = update["update_id"] + 1
                handle_update(update)
        else:
            print("هیچ آپدیتی دریافت نشد یا خطا رخ داد")

if __name__ == "__main__":
    main()