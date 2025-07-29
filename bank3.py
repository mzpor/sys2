"""
سناریوی جدید (بر اساس پیشنهاد)
بر اساس پیشنهادت، سناریوی جدید ربات این‌جوریه:

شروع:
کاربر دستور /start رو می‌فرسته.
ربات یه کیبورد معمولی (ReplyKeyboard) با سه دکمه نشون می‌ده:
شروع: برای شروع فرآیند انتخاب کلاس.
خروج: برای خروج و حذف کیبورد.
کلاس: برای رفتن به انتخاب کلاس.
انتخاب کلاس:
وقتی کاربر روی «کلاس» کلیک می‌کنه، ربات یه پیام با دو دکمه شیشه‌ای (InlineKeyboard) نشون می‌ده:
کلاس هزار تومانی (مثلاً کلاس پایه، 10000 ریال)
کلاس دو هزار تومانی (مثلاً کلاس پیشرفته، 20000 ریال)
همزمان، یه کیبورد معمولی با دکمه «برگشت به قبل» نمایش داده می‌شه.
پرداخت:
کاربر روی یکی از دکمه‌های شیشه‌ای (مثلاً «کلاس هزار تومانی») کلیک می‌کنه.
ربات پیام صورتحساب رو با متد sendInvoice می‌فرسته.
بعد از پرداخت موفق:
ربات این پیام‌ها رو تو چت خصوصی کاربر منتشر می‌کنه:
💸 پرداخت برای '{class_name}' با موفقیت انجام شد!
🌟 محمد می‌گه: «قدم گذاشتن در مسیر رشد از همین‌جا شروع می‌شه!»
📎 لینک ورود به گروه: ble.ir/join/Gah9cS9LzQ
🎉 از اینکه همراه شدید، بی‌نهایت سپاسگزاریم!
کیبورد معمولی (شامل دکمه‌های «شروع»، «خروج»، «کلاس») دوباره نمایش داده می‌شه تا منظم بمونه.
دکمه‌های معمولی و شیشه‌ای:
دکمه‌های معمولی (ReplyKeyboard):
در صفحه شروع: ["شروع", "خروج", "کلاس"]
بعد از انتخاب کلاس: ["برگشت به قبل"]
بعد از پرداخت موفق: ["شروع", "خروج", "کلاس"]
دکمه‌های شیشه‌ای (InlineKeyboard):
برای انتخاب کلاس: ["کلاس هزار تومانی", "کلاس دو هزار تومانی"]

ورژن 2
خطا بله 
دکمه بازگشت به قبل کار نکرد. 

"""

import requests
import time
import json
import uuid

# توکن‌های ربات و پرداخت
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
PAYMENT_TOKEN = "WALLET-LIiCzxGZnCd58Obr"  # توکن تولید (برای تست: WALLET-TEST-1111111111111111)
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
GROUP_LINK = "ble.ir/join/Gah9cS9LzQ"

# قیمت کلاس‌ها (به ریال)
CLASS_PRICES = {
    "کلاس هزار تومانی": 10000,  # 1000 تومان
    "کلاس دو هزار تومانی": 20000  # 2000 تومان
}

user_states = {}

def get_updates(offset=None):
    """دریافت آپدیت‌ها از API بله"""
    res = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset, "timeout": 30})
    print(f"دریافت آپدیت‌ها: {res.status_code}, پاسخ: {res.text}")
    return res.json()

def send_message(chat_id, text, reply_markup=None, secondary_reply_markup=None):
    """ارسال پیام به کاربر با پشتیبانی از کیبورد معمولی و شیشه‌ای"""
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup and secondary_reply_markup:
        # ترکیب کیبورد شیشه‌ای و معمولی
        payload["reply_markup"] = reply_markup
        payload["reply_markup"].update(secondary_reply_markup)
    elif reply_markup:
        payload["reply_markup"] = reply_markup
    elif secondary_reply_markup:
        payload["reply_markup"] = secondary_reply_markup
    response = requests.post(f"{BASE_URL}/sendMessage", json=payload)
    print(f"ارسال پیام: {response.status_code}, پاسخ: {response.text}")
    return response.json()

def build_reply_keyboard(buttons):
    """ساخت کیبورد معمولی"""
    return {
        "keyboard": [[{"text": btn}] for btn in buttons],
        "resize_keyboard": True
    }

def build_inline_keyboard(buttons):
    """ساخت کیبورد شیشه‌ای"""
    return {
        "inline_keyboard": [[{"text": btn["text"], "callback_data": btn["callback_data"]}] for btn in buttons]
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
        "need_phone_number": True
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
                callback_query = update.get("callback_query")
                successful_payment = message.get("successful_payment") if message else None

                print(f"آپدیت دریافت‌شده: {json.dumps(update, indent=2, ensure_ascii=False)}")

                if successful_payment and message:
                    chat_id = message["chat"]["id"]
                    user_id = message["from"]["id"]
                    selected_class = user_states.get(f"payment_class_{user_id}")
                    if selected_class:
                        send_message(chat_id, f"💸 پرداخت برای '{selected_class}' با موفقیت انجام شد!", 
                                     reply_markup=build_reply_keyboard(["شروع", "خروج", "کلاس"]))
                        send_message(chat_id, "🌟 محمد می‌گه: «قدم گذاشتن در مسیر رشد از همین‌جا شروع می‌شه!»", 
                                     reply_markup=build_reply_keyboard(["شروع", "خروج", "کلاس"]))
                        send_message(chat_id, f"📎 لینک ورود به گروه: {GROUP_LINK}", 
                                     reply_markup=build_reply_keyboard(["شروع", "خروج", "کلاس"]))
                        send_message(chat_id, "🎉 از اینکه همراه شدید، بی‌نهایت سپاسگزاریم!", 
                                     reply_markup=build_reply_keyboard(["شروع", "خروج", "کلاس"]))
                        user_states[user_id] = "DONE"

                elif callback_query:
                    chat_id = callback_query["message"]["chat"]["id"]
                    user_id = callback_query["from"]["id"]
                    callback_data = callback_query["data"]
                    state = user_states.get(user_id, "START")
                    if state == "CHOOSE_CLASS" and callback_data in CLASS_PRICES:
                        user_states[user_id] = "PAY"
                        user_states[f"payment_class_{user_id}"] = callback_data
                        if send_invoice(chat_id, CLASS_PRICES[callback_data], callback_data):
                            user_states[user_id] = "AWAITING_PAYMENT"
                        else:
                            send_message(chat_id, "❌ خطا در ارسال صورتحساب. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.", 
                                         reply_markup=build_reply_keyboard(["برگشت به قبل"]))

                elif message:
                    chat_id = message["chat"]["id"]
                    user_id = message["from"]["id"]
                    text = message.get("text", "")
                    state = user_states.get(user_id, "START")

                    if text == "/start" or text == "شروع":
                        user_states[user_id] = "START"
                        send_message(chat_id, "🎓 به ربات خوش اومدی! لطفاً یکی از گزینه‌ها رو انتخاب کن:", 
                                     reply_markup=build_reply_keyboard(["شروع", "خروج", "کلاس"]))

                    elif text == "خروج":
                        user_states[user_id] = "START"
                        send_message(chat_id, "👋 خداحافظ! هر وقت خواستی برگرد.", 
                                     reply_markup={"remove_keyboard": True})

                    elif text == "کلاس" or text == "برگشت به قبل":
                        user_states[user_id] = "CHOOSE_CLASS"
                        send_message(chat_id, "🎓 لطفاً یکی از کلاس‌ها رو انتخاب کن:", 
                                     reply_markup=build_inline_keyboard([
                                         {"text": "کلاس هزار تومانی", "callback_data": "کلاس هزار تومانی"},
                                         {"text": "کلاس دو هزار تومانی", "callback_data": "کلاس دو هزار تومانی"}
                                     ]), 
                                     secondary_reply_markup=build_reply_keyboard(["برگشت به قبل"]))

                elif pre_checkout_query:
                    pre_checkout_query_id = pre_checkout_query["id"]
                    user_id = pre_checkout_query["from"]["id"]
                    print(f"دریافت PreCheckoutQuery: {json.dumps(pre_checkout_query, indent=2, ensure_ascii=False)}")
                    answer_pre_checkout_query(pre_checkout_query_id, ok=True)
                    user_states[user_id] = "PAYMENT_CONFIRMED"

        time.sleep(2)

if __name__ == "__main__":
    main()