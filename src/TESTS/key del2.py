import requests
import json
import time
import random

BOT_TOKEN = "811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

quotes = [
    "تمرین تلاوت زندگی‌ات را تغییر می‌دهد! 🌟",
    "با هر تمرین، یک قدم به رشد نزدیک‌تر می‌شوی! 🚀",
    "پیگیری و تمرین، کلید موفقیت توست! 💪",
    "تمرین با دقت، کیفیت تلاوتت را بالا می‌برد! 🔥",
    "شاگرد پرتلاش! منتظر تلاوت‌های زیبای تو هستیم! 🎯"
]

def get_updates(offset=None):
    response = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset})
    return response.json()

def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    response = requests.post(f"{BASE_URL}/sendMessage", json=payload)
    return response.json()  # برای دریافت message_id

def delete_message(chat_id, message_id):
    payload = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    requests.post(f"{BASE_URL}/deleteMessage", json=payload)

def create_reply_keyboard():
    keyboard = {
        "keyboard": [
            [{"text": "محمد"}, {"text": "علی"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    return keyboard

def create_inline_keyboard():
    keyboard = {
        "inline_keyboard": [
            [{"text": "مهدی", "callback_data": "mahdi"}],
            [{"text": "سعید", "callback_data": "saeed"}]
        ]
    }
    return keyboard

def generate_response(name):
    quote = random.choice(quotes)
    return f"{name} می‌گه: «{quote}»"

def answer_callback_query(callback_query_id, text=None):
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    requests.post(f"{BASE_URL}/answerCallbackQuery", json=payload)

def main():
    offset = None
    last_message_ids = {}  # دیکشنری برای ذخیره message_id هر چت

    print("ربات با دکمه‌های معمولی و شیشه‌ای راه‌اندازی شد...")

    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1

                # پیام متنی
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    user_message_id = message["message_id"]

                    # حذف پیام قبلی قبل از پردازش
                    if chat_id in last_message_ids:
                        delete_message(chat_id, last_message_ids[chat_id])

                    if text == "/start" or text.lower() == "restart":
                        sent_message = send_message(chat_id, "دکمه‌های معمولی رو امتحان کن:", reply_markup=create_reply_keyboard())
                        send_message(chat_id, "دکمه‌های شیشه‌ای رو امتحان کن:", reply_markup=create_inline_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif text == "محمد":
                        sent_message = send_message(chat_id, generate_response("محمد"), reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif text == "علی":
                        sent_message = send_message(chat_id, generate_response("علی"), reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]

                # کلیک روی دکمه‌های شیشه‌ای
                elif "callback_query" in update:
                    query = update["callback_query"]
                    chat_id = query["message"]["chat"]["id"]
                    data = query["data"]
                    query_id = query["id"]
                    message_id = query["message"]["message_id"]

                    # حذف پیام قبلی قبل از پردازش
                    if chat_id in last_message_ids:
                        delete_message(chat_id, last_message_ids[chat_id])

                    if data == "mahdi":
                        sent_message = send_message(chat_id, generate_response("مهدی"), reply_markup=create_inline_keyboard())
                    elif data == "saeed":
                        sent_message = send_message(chat_id, generate_response("سعید"), reply_markup=create_inline_keyboard())
                    else:
                        sent_message = send_message(chat_id, "گزینه‌ای شناسایی نشد!", reply_markup=create_inline_keyboard())

                    answer_callback_query(query_id)
                    last_message_ids[chat_id] = sent_message["result"]["message_id"]

        time.sleep(2)

if __name__ == "__main__":
    main()