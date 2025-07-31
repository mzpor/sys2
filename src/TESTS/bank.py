import requests
import time
import json
import uuid

# توکن‌های ربات و پرداخت
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
PAYMENT_TOKEN = "WALLET-LIiCzxGZnCd58Obr"  # برای دیباگ با توکن آزمایشی شروع کنید
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
GROUP_LINK = "ble.ir/mtelbot"

# قیمت کلاس‌ها (به ریال)
CLASS_PRICES = {
    "کلاس پایه": 10000,  # 1000 تومان = 10000 ریال
    "کلاس پیشرفته": 10000
}

user_states = {}

def get_updates(offset=None):
    """دریافت آپدیت‌ها از API بله"""
    res = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset, "timeout": 30})
    print(f"دریافت آپدیت‌ها: {res.status_code}, پاسخ: {res.text}")
    return res.json()

def send_message(chat_id, text, reply_markup=None):
    """ارسال پیام به کاربر"""
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    response = requests.post(f"{BASE_URL}/sendMessage", json=payload)
    print(f"ارسال پیام: {response.status_code}, پاسخ: {response.text}")
    return response.json()

def build_keyboard(buttons):
    """ساخت کیبورد برای گزینه‌ها"""
    return {
        "keyboard": [[{"text": btn}] for btn in buttons],
        "resize_keyboard": True
    }

def send_invoice(chat_id, amount, class_name):
    """ارسال پیام صورتحساب به کاربر"""
    payload = {
        "chat_id": chat_id,
        "title": f"پرداخت برای {class_name}",
        "description": f"پرداخت برای ثبت‌نام در {class_name} با مبلغ {amount // 10} تومان",
        "payload": str(uuid.uuid4()),
        "provider_token": PAYMENT_TOKEN,
        "currency": "IRR",
        "prices": [{"label": class_name, "amount": amount}],
        "need_phone_number": True  # درخواست شماره تلفن توسط سیستم پرداخت
    }
    try:
        response = requests.post(
            f"{BASE_URL}/sendInvoice",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"وضعیت HTTP (sendInvoice): {response.status_code}")
        print(f"پاسخ خام (sendInvoice): {response.text}")
        response_data = response.json()
        if response_data.get("ok"):
            print(f"صورتحساب با موفقیت برای چت {chat_id} ارسال شد")
            return True
        else:
            print(f"خطای API: {response_data}")
            return False
    except Exception as e:
        print(f"خطا در ارسال صورتحساب: {e}")
        return False

def answer_pre_checkout_query(pre_checkout_query_id, ok=True, error_message=None):
    """پاسخ به PreCheckoutQuery"""
    payload = {
        "pre_checkout_query_id": pre_checkout_query_id,
        "ok": ok
    }
    if error_message:
        payload["error_message"] = error_message
    response = requests.post(f"{BASE_URL}/answerPreCheckoutQuery", json=payload)
    print(f"پاسخ به PreCheckoutQuery: {response.status_code}, پاسخ: {response.text}")
    return response.json()

def main():
    offset = None
    print("ربات فعال شد...")

    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                message = update.get("message")
                pre_checkout_query = update.get("pre_checkout_query")

                print(f"آپدیت دریافت‌شده: {json.dumps(update, indent=2, ensure_ascii=False)}")

                if message:
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
                        send_message(chat_id, f"✅ شما کلاس '{text}' با قیمت {CLASS_PRICES[text] // 10} تومان را انتخاب کردید.", 
                                     reply_markup=build_keyboard(["💳 پرداخت"]))

                    elif state == "PAY" and text == "💳 پرداخت":
                        selected_class = user_states.get(f"class_{user_id}", "نامشخص")
                        amount = CLASS_PRICES[selected_class]
                        
                        if send_invoice(chat_id, amount, selected_class):
                            user_states[user_id] = "AWAITING_PAYMENT"
                            user_states[f"payment_class_{user_id}"] = selected_class
                        else:
                            send_message(chat_id, "❌ خطا در ارسال صورتحساب. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.")

                    elif state == "AWAITING_PAYMENT" and message.get("successful_payment"):
                        selected_class = user_states.get(f"payment_class_{user_id}", "نامشخص")
                        send_message(chat_id, f"💸 پرداخت برای '{selected_class}' با موفقیت انجام شد!")
                        send_message(chat_id, "🌟 محمد می‌گه: «قدم گذاشتن در مسیر رشد از همین‌جا شروع می‌شه!»")
                        send_message(chat_id, f"📎 لینک ورود به گروه: {GROUP_LINK}")
                        send_message(chat_id, "🎉 از اینکه همراه شدید، بی‌نهایت سپاسگزاریم!")
                        user_states[user_id] = "DONE"

                elif pre_checkout_query:
                    pre_checkout_query_id = pre_checkout_query["id"]
                    user_id = pre_checkout_query["from"]["id"]
                    print(f"دریافت PreCheckoutQuery: {json.dumps(pre_checkout_query, indent=2, ensure_ascii=False)}")
                    answer_pre_checkout_query(pre_checkout_query_id, ok=True)
                    user_states[user_id] = "PAYMENT_CONFIRMED"

        time.sleep(2)

if __name__ == "__main__":
    main()