#ورژن 3
import requests
import json
import time
import random
import os

BOT_TOKEN = "811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
DATA_FILE = "1.txt"

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
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    response = requests.post(f"{BASE_URL}/sendMessage", json=payload)
    return response.json()

def create_inline_keyboard(buttons):
    keyboard = {"inline_keyboard": buttons}
    return keyboard

def create_reply_keyboard():
    keyboard = {
        "keyboard": [
            [{"text": "معرفی مدرسه"}, {"text": "نظرسنجی"}],
            [{"text": "درباره ربات"}, {"text": "سوالات متداول"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    return keyboard

def save_user_data(chat_id, data):
    users = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    chat_id_str, user_data = line.strip().split(" | ", 1)
                    users[chat_id_str] = json.loads(user_data)
    users[str(chat_id)] = data
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        for chat_id_str, user_data in users.items():
            file.write(f"{chat_id_str} | {json.dumps(user_data, ensure_ascii=False)}\n")  # ensure_ascii=False برای فارسی
    print(f"داده‌ها ذخیره شدند: {data}")

def load_user_data(chat_id):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    chat_id_str, user_data = line.strip().split(" | ", 1)
                    if int(chat_id_str) == chat_id:
                        return json.loads(user_data)
    return None

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
    last_message_ids = {}

    print("ربات مدرسه قرآنی تلاوت راه‌اندازی شد...")

    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1

                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    user_data = load_user_data(chat_id)

                    if text == "/start" or text.lower() == "restart":
                        if not user_data:
                            welcome_msg = "🌟 سلام! به مدرسه قرآنی تلاوت خوش آمدید! 📖\nآماده‌اید با قرآن همراه بشید؟ بیایید شروع کنیم!\nمتن زیبا و انتخابی ورود به مدرسه قرانی برای قرآن‌آموزان"
                            inline_buttons = [
                                [{"text": "ثبت نام", "callback_data": "register"}],
                                [{"text": "مشاهده لیست کلاس ها", "callback_data": "view_classes"}]
                            ]
                            sent_message = send_message(chat_id, welcome_msg, reply_markup=create_inline_keyboard(inline_buttons))
                            send_message(chat_id, "منوی اصلی:", reply_markup=create_reply_keyboard())
                        else:
                            inline_buttons = [
                                [{"text": "تایید حساب کاربری", "callback_data": "verify_account"}],
                                [{"text": "مشاهده لیست کلاس ها", "callback_data": "view_classes"}]
                            ]
                            sent_message = send_message(chat_id, f"خوش آمدید {user_data.get('first_name', '')}!", reply_markup=create_inline_keyboard(inline_buttons))
                            send_message(chat_id, "منوی اصلی:", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif text == "معرفی مدرسه":
                        intro_msg = "📚 **معرفی مدرسه تلاوت قرآن**\n- معرفی کامل مدرسه تلاوت قرآن\n- خدمات ارائه شده: آموزش تلاوت، حفظ قرآن\n- اهداف آموزشی: تربیت قرآن‌آموزان ماهر\n"
                        inline_buttons = [
                            [{"text": "ثبت نام", "callback_data": "register"}],
                            [{"text": "بازگشت به منو", "callback_data": "back_to_menu"}]
                        ]
                        sent_message = send_message(chat_id, intro_msg, reply_markup=create_inline_keyboard(inline_buttons))
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif text == "نظرسنجی":
                        if user_data and "survey" not in user_data:
                            sent_message = send_message(chat_id, "لطفاً نظرتون رو انتخاب کنید:\n- خوب\n- بد\n- نیاز به بهبود", reply_markup=create_reply_keyboard())
                        else:
                            sent_message = send_message(chat_id, f"نظر قبلی شما: {user_data.get('survey', 'ندارد')}", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif text == "درباره ربات":
                        sent_message = send_message(chat_id, "این ربات برای کمک به قرآن‌آموزان طراحی شده است.", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif text == "سوالات متداول":
                        sent_message = send_message(chat_id, "سوالات متداول در سایت موجود است.", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif user_data and user_data.get("step") == "full_name":
                        user_data["full_name"] = text
                        user_data["first_name"] = text.split()[0] if text.split() else text
                        user_data["chat_id"] = chat_id  # اضافه کردن ایدی
                        user_data["step"] = "phone"
                        save_user_data(chat_id, user_data)
                        inline_buttons = [
                            [{"text": "ارسال تلفن (بله)", "callback_data": "send_phone"}, {"text": "تصحیح نام", "callback_data": "edit_name"}]
                        ]
                        reply_buttons = {"keyboard": [[{"text": "ارسال تلفن موبایل"}]], "resize_keyboard": True, "one_time_keyboard": False}
                        sent_message = send_message(chat_id, f"نام و نام خانوادگی: {text}\nلطفاً تلفن خود را وارد کنید:", reply_markup=reply_buttons)
                        send_message(chat_id, "", reply_markup=create_inline_keyboard(inline_buttons))
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif user_data and user_data.get("step") == "phone":
                        user_data["phone"] = text
                        user_data["step"] = "national_id"
                        save_user_data(chat_id, user_data)
                        inline_buttons = [
                            [{"text": "تصحیح نام", "callback_data": "edit_name"}]
                        ]
                        sent_message = send_message(chat_id, f"نام: {user_data['first_name']}\nموبایل: {text}\nلطفاً کد ملی خود را وارد کنید:", reply_markup=create_reply_keyboard())
                        send_message(chat_id, "", reply_markup=create_inline_keyboard(inline_buttons))
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif user_data and user_data.get("step") == "national_id":
                        user_data["national_id"] = text
                        user_data["step"] = "complete"
                        save_user_data(chat_id, user_data)
                        inline_buttons = [
                            [{"text": "تصحیح کد ملی", "callback_data": "edit_national_id"}],
                            [{"text": "انتخاب کلاس", "callback_data": "select_class"}]
                        ]
                        sent_message = send_message(chat_id, f"حساب کاربری:\nنام: {user_data['first_name']}\nموبایل: {user_data['phone']}\nکد ملی: {text}", reply_markup=create_reply_keyboard())
                        send_message(chat_id, "", reply_markup=create_inline_keyboard(inline_buttons))
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif text in ["خوب", "بد", "نیاز به بهبود"] and user_data:
                        user_data["survey"] = text
                        save_user_data(chat_id, user_data)
                        sent_message = send_message(chat_id, f"نظر شما ثبت شد: {text}", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]

                elif "callback_query" in update:
                    query = update["callback_query"]
                    chat_id = query["message"]["chat"]["id"]
                    data = query["data"]
                    query_id = query["id"]
                    user_data = load_user_data(chat_id)

                    if data == "register" and not user_data:
                        user_data = {"step": "full_name", "chat_id": chat_id}
                        save_user_data(chat_id, user_data)
                        sent_message = send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید:", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif data == "view_classes" and user_data and user_data.get("step") == "complete":
                        classes = [
                            "کلاس تلاوت پایه: https://example.com/pay1",
                            "کلاس حفظ قرآن: https://example.com/pay2",
                            "کلاس تجوید: https://example.com/pay3"
                        ]
                        class_msg = "\n".join(classes)
                        sent_message = send_message(chat_id, f"لیست کلاس‌ها:\n{class_msg}", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif data == "verify_account" and user_data and user_data.get("step") == "complete":
                        sent_message = send_message(chat_id, f"حساب شما تأیید شد:\nنام: {user_data['first_name']}\nموبایل: {user_data['phone']}\nکد ملی: {user_data['national_id']}", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif data == "edit_name" and user_data and user_data.get("step") in ["full_name", "phone", "national_id"]:
                        user_data["step"] = "full_name"
                        save_user_data(chat_id, user_data)
                        sent_message = send_message(chat_id, "لطفاً نام و نام خانوادگی جدید را وارد کنید:", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif data == "send_phone" and user_data and user_data.get("step") == "phone":
                        sent_message = send_message(chat_id, "لطفاً شماره تلفن خود را از طریق اپلیکیشن بله ارسال کنید یا دستی وارد کنید:", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif data == "edit_national_id" and user_data and user_data.get("step") == "complete":
                        user_data["step"] = "national_id"
                        save_user_data(chat_id, user_data)
                        sent_message = send_message(chat_id, "لطفاً کد ملی جدید را وارد کنید:", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif data == "select_class" and user_data and user_data.get("step") == "complete":
                        classes = [
                            "کلاس تلاوت پایه: https://example.com/pay1",
                            "کلاس حفظ قرآن: https://example.com/pay2",
                            "کلاس تجوید: https://example.com/pay3"
                        ]
                        class_msg = "\n".join(classes)
                        sent_message = send_message(chat_id, f"لیست کلاس‌ها:\n{class_msg}", reply_markup=create_reply_keyboard())
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]
                    elif data == "back_to_menu":
                        inline_buttons = [
                            [{"text": "ثبت نام", "callback_data": "register"}],
                            [{"text": "مشاهده لیست کلاس ها", "callback_data": "view_classes"}]
                        ] if not user_data else [
                            [{"text": "تایید حساب کاربری", "callback_data": "verify_account"}],
                            [{"text": "مشاهده لیست کلاس ها", "callback_data": "view_classes"}]
                        ]
                        sent_message = send_message(chat_id, "منوی اصلی:", reply_markup=create_reply_keyboard())
                        send_message(chat_id, "", reply_markup=create_inline_keyboard(inline_buttons))
                        last_message_ids[chat_id] = sent_message["result"]["message_id"]

                    answer_callback_query(query_id)

        time.sleep(2)

if __name__ == "__main__":
    main()