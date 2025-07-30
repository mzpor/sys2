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
        print(f"Message sent to chat_id {chat_id}")
    else:
        print(f"Error sending message: {response.status_code}, {response.text}")

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
        print(f"Error getting updates: {response.status_code}, {response.text}")
        return None

# تابع ایجاد کیبورد شیشه‌ای برای هر کاربر
def create_user_keyboard(user):
    keyboard = {
        "inline_keyboard": [[
            {"text": "حاضر", "callback_data": f"status_{user}_حاضر"},
            {"text": "تاخیر", "callback_data": f"status_{user}_تاخیر"},
            {"text": "غایب", "callback_data": f"status_{user}_غایب"},
            {"text": "موجه", "callback_data": f"status_{user}_موجه"}
        ]]
    }
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
            print(f"Management panel sent to user_id {user_id}")

    elif "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        user_id = callback["from"]["id"]
        callback_data = callback["data"]

        if not is_user_authorized(user_id):
            send_message(chat_id, "❌ شما اجازه دسترسی ندارید!")
            return

        if callback_data == "start_attendance":
            user_list = "\n".join([f"{i+1}. {user} (در انتظار)" for i, user in enumerate(users)])
            send_message(chat_id, f"📋 لیست کاربران:\n{user_list}", create_user_keyboard(users[0]))
            for user in users[1:]:
                send_message(chat_id, f"{users.index(user)+1}. {user} (در انتظار)", create_user_keyboard(user))
            print(f"Attendance list sent to user_id {user_id}")

        elif callback_data.startswith("status_"):
            _, user, status = callback_data.split("_")
            attendance_data[user] = status
            send_message(chat_id, f"✔ وضعیت {user} ثبت شد: {status}")
            print(f"Status updated for {user} to {status} by user_id {user_id}")

# حلقه اصلی
def main():
    offset = 0
    print("Bot started...")
    while True:
        updates = get_updates(offset)
        if updates and updates.get("ok") and updates.get("result"):
            for update in updates["result"]:
                offset = update["update_id"] + 1
                handle_update(update)
     #   else:
          #  print("No updates received or error occurred")

if __name__ == "__main__":
    main()