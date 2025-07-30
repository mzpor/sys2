import requests
import time
import json

TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
API_URL = f"https://tapi.bale.ai/bot{TOKEN}/getUpdates"
SEND_URL = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"
URL = f"https://tapi.bale.ai/bot{TOKEN}/"

user_states = {}

# تابع ارسال پیام
def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if keyboard:
        data["reply_markup"] = json.dumps({
            "keyboard": keyboard,
            "resize_keyboard": True
        })
    response = requests.post(URL + "sendMessage", data=data)
    return response

# ساخت دکمه‌ها
def build_buttons(count):
    rows = []
    row = []
    for i in range(1, count + 1):
        row.append(f"گزینه {i}")
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return rows

def build_control_buttons():
    return [["+", "-"]]

# دریافت آخرین آپدیت‌ها
def get_updates(offset=None):
    data = {"timeout": 100}
    if offset:
        data["offset"] = offset
    response = requests.get(URL + "getUpdates", data=data)
    result = response.json()["result"]
    return result

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message")
            if not message:
                continue

            text = message.get("text")
            chat_id = message["chat"]["id"]
            user_id = str(chat_id)

            # حالت اولیه
            if text == "/start":
                send_message(chat_id, "🎓 خوش آمدید! یکی از گزینه‌ها رو انتخاب کنید:", 
                    keyboard=[["۱", "۲", "۳"]])
                user_states[user_id] = {"mode": "normal", "count": 0}

            elif text in ["۱", "۲", "۳"]:
                count = int(text)
                keyboard = build_buttons(count) + build_control_buttons()
                send_message(chat_id, f"{count} دکمه معمولی فعال شد:", keyboard=keyboard)
                user_states[user_id]["mode"] = "dynamic"
                user_states[user_id]["count"] = count

            elif text == "+":
                state = user_states.get(user_id, {})
                if state.get("mode") == "dynamic":
                    if state["count"] < 8:
                        state["count"] += 1
                        keyboard = build_buttons(state["count"]) + build_control_buttons()
                        send_message(chat_id, f"تعداد دکمه‌ها: {state['count']}", keyboard=keyboard)
                    else:
                        send_message(chat_id, "🚫 بیشتر از ۸ دکمه مجاز نیست!")

            elif text == "-":
                state = user_states.get(user_id, {})
                if state.get("mode") == "dynamic":
                    if state["count"] > 2:
                        state["count"] -= 1
                        keyboard = build_buttons(state["count"]) + build_control_buttons()
                        send_message(chat_id, f"تعداد دکمه‌ها: {state['count']}", keyboard=keyboard)
                    else:
                        send_message(chat_id, "🚫 کمتر از ۲ دکمه مجاز نیست!")

        time.sleep(1)

if __name__ == "__main__":
    main()


