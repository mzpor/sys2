import requests
import json
import time
import random
import os

BOT_TOKEN = "811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
LOG_USER_ID =    # ایدی کاربر برای دریافت لاگ‌ها
ADMIN_USER_ID = 1114227010  # ایدی کاربر ادمین (موبایل یا سازنده)

def get_updates(offset=None):
    response = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset})
    return response.json()

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    response = requests.post(f"{BASE_URL}/sendMessage", json=payload)
    return response.json()

def send_log(message):
    send_message(LOG_USER_ID, message)

def main():
    offset = None
    last_message_ids = {}
    room_users = {}  # برای ذخیره کاربران هر روم

    print("ربات لاگ‌دهنده روم بله راه‌اندازی شد...")

    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1

                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    chat_type = message["chat"].get("type")
                    user = message.get("from", {})
                    user_id = user.get("id")
                    user_name = user.get("first_name", "ناشناس")

                    # لاگ ورود به روم
                    if chat_type == "supergroup" and user_id not in room_users.get(chat_id, []):
                        room_title = message["chat"].get("title", "بدون نام")
                        log_message = f"الان در روم {room_title} هستم. کاربر {user_name} وارد شد."
                        send_log(log_message)
                        if chat_id not in room_users:
                            room_users[chat_id] = []
                        room_users[chat_id].append(user_id)

                    # لاگ ادمین شدن
                    if "new_chat_members" in message and any(m.get("id") == user_id and m.get("is_admin") for m in message["new_chat_members"]):
                        room_title = message["chat"].get("title", "بدون نام")
                        log_message = f"الان در روم {room_title} ادمین شدم. کاربر {user_name} ادمین شد."
                        send_log(log_message)

                    # لاگ پیام متنی
                    if "text" in message:
                        text = message["text"]
                        room_title = message["chat"].get("title", "بدون نام")
                        log_message = f"در روم {room_title}، کاربر {user_name} پیام متنی ارسال کرد: {text}"
                        send_log(log_message)

                    # لاگ پیام صوتی
                    if "voice" in message:
                        room_title = message["chat"].get("title", "بدون نام")
                        log_message = f"در روم {room_title}، کاربر {user_name} پیام صوتی ارسال کرد."
                        send_log(log_message)

                    # لاگ پیام عکس
                    if "photo" in message:
                        room_title = message["chat"].get("title", "بدون نام")
                        log_message = f"در روم {room_title}، کاربر {user_name} عکس ارسال کرد."
                        send_log(log_message)

                    # لاگ ریپلای
                    if "reply_to_message_id" in message:
                        room_title = message["chat"].get("title", "بدون نام")
                        reply_to = message["reply_to_message_id"]
                        log_message = f"در روم {room_title}، کاربر {user_name} به پیام {reply_to} ریپلای کرد."
                        send_log(log_message)

                    # دستور تغییر لینک روم
                    if "text" in message and message["text"].startswith("/set_link") and user_id == ADMIN_USER_ID:
                        room_title = message["chat"].get("title", "بدون نام")
                        new_link = message["text"].replace("/set_link", "").strip()
                        if new_link:
                            log_message = f"لینک روم {room_title} توسط ادمین به {new_link} تغییر کرد."
                            send_log(log_message)
                            send_message(LOG_USER_ID, f"لینک جدید روم: {new_link}")
                        else:
                            send_message(chat_id, "لطفاً لینک جدید رو وارد کن!")

                    # دستور لیست اعضا
                    if "text" in message and message["text"] == "/list_members" and user_id == ADMIN_USER_ID:
                        room_title = message["chat"].get("title", "بدون نام")
                        # شبیه‌سازی لیست اعضا (چون API بله لیست کامل رو مستقیم نمی‌ده)
                        admins = [u for u in room_users.get(chat_id, []) if u == user_id]  # فقط ادمین فعلی
                        users = [u for u in room_users.get(chat_id, []) if u != user_id]
                        admin_names = [name for uid, name in [(uid, load_user_data(uid)["first_name"] if load_user_data(uid) else "ناشناس") for uid in admins] if uid]
                        user_names = [name for uid, name in [(uid, load_user_data(uid)["first_name"] if load_user_data(uid) else "ناشناس") for uid in users] if uid]
                        log_message = f"لیست ادمین‌ها در روم {room_title}: {', '.join(admin_names)}\nلیست کاربرها: {', '.join(user_names)}"
                        send_log(log_message)
                        send_message(chat_id, log_message)

def load_user_data(chat_id):
    if os.path.exists("1.txt"):
        with open("1.txt", "r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    user_id_str, user_data = line.strip().split(" | ", 1)
                    if int(user_id_str) == chat_id:
                        return json.loads(user_data)
    return {"first_name": "ناشناس"}

if __name__ == "__main__":
    main()