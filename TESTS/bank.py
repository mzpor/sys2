import requests
import time

BOT_TOKEN = "811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1"
#BOT_TOKEN = "توکن واقعی بات رو اینجا بذار"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
GROUP_LINK = "https://bale.ai/join/MadreseTalavatGroup"

CLASS_PRICES = {
    "کلاس پایه": "200,000 تومان",
    "کلاس پیشرفته": "400,000 تومان"
}

user_states = {}

def get_updates(offset=None):
    res = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset})
    return res.json()

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=payload)

def build_keyboard(buttons):
    return {
        "keyboard": [[{"text": btn}] for btn in buttons],
        "resize_keyboard": True
    }

def main():
    offset = None
    print("ربات فعال شد...")

    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                message = update.get("message")
                if not message: continue

                chat_id = message["chat"]["id"]
                user_id = message["from"]["id"]
                text = message.get("text", "")

                state = user_states.get(user_id, "START")

                if text == "/start":
                    user_states[user_id] = "CHOOSE_CLASS"
                    send_message(chat_id, "🎓 لطفاً یکی از کلاس‌ها را انتخاب کنید:", 
                                 reply_markup=build_keyboard(list(CLASS_PRICES.keys())))

                elif state == "CHOOSE_CLASS" and text in CLASS_PRICES:
                    user_states[user_id] = "PAY"
                    user_states[f"class_{user_id}"] = text
                    send_message(chat_id, f"✅ شما کلاس '{text}' با قیمت {CLASS_PRICES[text]} را انتخاب کردید.", 
                                 reply_markup=build_keyboard(["💳 پرداخت"]))

                elif state == "PAY" and text == "💳 پرداخت":
                    # پرداخت آزمایشی فرضی
                    selected_class = user_states.get(f"class_{user_id}", "نامشخص")
                    send_message(chat_id, f"💸 پرداخت آزمایشی برای '{selected_class}' با موفقیت انجام شد!")
                    send_message(chat_id, "🌟 محمد می‌گه: «قدم گذاشتن در مسیر رشد از همین‌جا شروع می‌شه!»")
                    send_message(chat_id, f"📎 لینک ورود به گروه: {GROUP_LINK}")
                    send_message(chat_id, "🎉 از اینکه همراه شدید، بی‌نهایت سپاسگزاریم!")

                    user_states[user_id] = "DONE"

        time.sleep(2)

if __name__ == "__main__":
    main()