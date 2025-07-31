"""
**سناریو ربات:**
1. کاربر دستور /start رو می‌فرسته.
2. ربات لیستی از گزینه‌ها (مثل کلاس‌ها) با دکمه‌های معمولی نشون می‌ده.
3. کاربر یه گزینه (مثل "کلاس پایه") انتخاب می‌کنه.
4. ربات یه پیام تأیید با دکمه شیشه‌ای (مثل "💳 پرداخت") می‌فرسته.
5. کاربر روی دکمه پرداخت کلیک می‌کنه و ربات یه صورتحساب (با متد sendInvoice) می‌فرسته.
6. بعد از پرداخت موفق، ربات پیام‌های تأیید و لینک گروه رو می‌فرسته.

**جزئیات دکمه‌ها:**
- دکمه‌های معمولی: ["کلاس پایه", "کلاس پیشرفته"] (برای انتخاب کلاس)
- دکمه‌های شیشه‌ای: ["💳 پرداخت"] (برای شروع پرداخت)

**رفتار بعد از پرداخت:**
- پیام‌ها:
  1. "💸 پرداخت برای '{class_name}' با موفقیت انجام شد!"
  2. "🌟 محمد می‌گه: «قدم گذاشتن در مسیر رشد از همین‌جا شروع می‌شه!»"
  3. "📎 لینک ورود به گروه: {group_link}"
  4. "🎉 از اینکه همراه شدید، بی‌نهایت سپاسگزاریم!"
- منتشرشده در: چت خصوصی با کاربر

**جزئیات فنی:**
- توکن ربات: {BOT_TOKEN}
- توکن پرداخت: {PAYMENT_TOKEN} (تست یا تولید)
- لینک گروه: {GROUP_LINK}
- ارز: IRR
- قیمت‌ها: {لیست قیمت‌ها به ریال}
- نیاز به شماره تلفن در صورتحساب: {True/False}

**درخواست:**
- کد پایتون بنویس که این سناریو رو پیاده کنه.
- اگه خطایی تو کد فعلی (اختیاری: کد رو اینجا بذار) بود، اصلاحش کن.
- خروجی‌های دیباگ (مثل sendInvoice و SuccessfulPayment) رو تو نظر بگیر.
"""

"""
**سناریو ربات:**
1. کاربر /start رو می‌فرسته.
2. ربات دو دکمه معمولی ["کلاس پایه", "کلاس پیشرفته"] نشون می‌ده.
3. کاربر یه کلاس انتخاب می‌کنه.
4. ربات پیام تأیید با دکمه شیشه‌ای "💳 پرداخت" می‌فرسته.
5. کاربر روی دکمه پرداخت کلیک می‌کنه و صورتحساب با متد sendInvoice ارسال می‌شه.
6. بعد از پرداخت موفق، ربات 4 پیام تو چت خصوصی کاربر می‌فرسته.

**جزئیات دکمه‌ها:**
- دکمه‌های معمولی: ["کلاس پایه", "کلاس پیشرفته"]
- دکمه شیشه‌ای: ["💳 پرداخت"]

**رفتار بعد از پرداخت:**
- پیام‌ها:
  1. "💸 پرداخت برای '{class_name}' با موفقیت انجام شد!"
  2. "🌟 محمد می‌گه: «قدم گذاشتن در مسیر رشد از همین‌جا شروع می‌شه!»"
  3. "📎 لینک ورود به گروه: ble.ir/join/Gah9cS9LzQ"
  4. "🎉 از اینکه همراه شدید، بی‌نهایت سپاسگزاریم!"
- منتشرشده در: چت خصوصی کاربر

**جزئیات فنی:**
- توکن ربات: 1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3
- توکن پرداخت: WALLET-LIiCzxGZnCd58Obr (تولید)
- لینک گروه: ble.ir/join/Gah9cS9LzQ
- ارز: IRR
- قیمت‌ها: {"کلاس پایه": 10000, "کلاس پیشرفته": 10000} (ریال)
- نیاز به شماره تلفن در صورتحساب: True

**درخواست:**
- کد پایتون فعلی (زیر) رو اصلاح کن تا دکمه شیشه‌ای "💳 پرداخت" درست کار کنه و پیام‌های بعد از پرداخت تو چت خصوصی منتشر بشن.
- خطاها رو بر اساس خروجی‌های قبلی (اگه داری) تصحیح کن.
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

def build_reply_keyboard(buttons):
    """ساخت کیبورد معمولی برای گزینه‌ها"""
    return {
        "keyboard": [[{"text": btn}] for btn in buttons],
        "resize_keyboard": True
    }

def build_inline_keyboard(buttons):
    """ساخت کیبورد شیشه‌ای برای دکمه پرداخت"""
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

                if successful_payment:
                    chat_id = message["chat"]["id"]
                    user_id = message["from"]["id"]
                    state = user_states.get(user_id, "START")
                    if state == "AWAITING_PAYMENT":
                        selected_class = user_states.get(f"class_{user_id}", "نامشخص")
                        send_message(chat_id, f"💸 پرداخت برای '{selected_class}' با موفقیت انجام شد!")
                        send_message(chat_id, "🌟 محمد می‌گه: «قدم گذاشتن در مسیر رشد از همین‌جا شروع می‌شه!»")
                        send_message(chat_id, f"📎 لینک ورود به گروه: {GROUP_LINK}")
                        send_message(chat_id, "🎉 از اینکه همراه شدید، بی‌نهایت سپاسگزاریم!")
                        user_states[user_id] = "DONE"

                elif callback_query:
                    chat_id = callback_query["message"]["chat"]["id"]
                    user_id = callback_query["from"]["id"]
                    callback_data = callback_query["data"]
                    state = user_states.get(user_id, "START")
                    if state == "PAY" and callback_data == "pay":
                        selected_class = user_states.get(f"class_{user_id}", "نامشخص")
                        amount = CLASS_PRICES[selected_class]
                        if send_invoice(chat_id, amount, selected_class):
                            user_states[user_id] = "AWAITING_PAYMENT"
                            user_states[f"payment_class_{user_id}"] = selected_class
                        else:
                            send_message(chat_id, "❌ خطا در ارسال صورتحساب. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.")

                elif message:
                    chat_id = message["chat"]["id"]
                    user_id = message["from"]["id"]
                    text = message.get("text", "")
                    state = user_states.get(user_id, "START")

                    if text == "/start":
                        user_states[user_id] = "CHOOSE_CLASS"
                        send_message(chat_id, "🎓 لطفاً یکی از کلاس‌ها را انتخاب کنید:", 
                                     reply_markup=build_reply_keyboard(list(CLASS_PRICES.keys())))

                    elif state == "CHOOSE_CLASS" and text in CLASS_PRICES:
                        user_states[user_id] = "PAY"
                        user_states[f"class_{user_id}"] = text
                        send_message(chat_id, f"✅ شما کلاس '{text}' با قیمت {CLASS_PRICES[text] // 10} تومان را انتخاب کردید.", 
                                     reply_markup=build_inline_keyboard([{"text": "💳 پرداخت", "callback_data": "pay"}]))

                elif pre_checkout_query:
                    pre_checkout_query_id = pre_checkout_query["id"]
                    user_id = pre_checkout_query["from"]["id"]
                    print(f"دریافت PreCheckoutQuery: {json.dumps(pre_checkout_query, indent=2, ensure_ascii=False)}")
                    answer_pre_checkout_query(pre_checkout_query_id, ok=True)
                    user_states[user_id] = "PAYMENT_CONFIRMED"

        time.sleep(2)

if __name__ == "__main__":
    main()