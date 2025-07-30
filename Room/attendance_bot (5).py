import requests
import json

# تنظیمات بات
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

# کاربر مجاز
AUTHORIZED_USER_ID = 574330749  # آیدی مجاز
users = [f"کاربر{i+1}" for i in range(10)]  # لیست کاربران
statuses = ["حاضر", "تاخیر", "غایب", "موجه"]  # وضعیت‌ها
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
    return user_id == AUTHORIZED_USER_ID

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

        if text == "لیست حضور غیاب":
            send_message(chat_id, "سلام مربی عزیز 👋\nلطفاً وضعیت‌ها را ثبت کنید.")
            for user in users:
                send_message(chat_id, f"📋 {user}", {"keyboard": [[f"{i+1}. {status}" for i, status in enumerate(statuses)]]})
            print(f"دریافت دستور از user_id {user_id}: لیست حضور غیاب")

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