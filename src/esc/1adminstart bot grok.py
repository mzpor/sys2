# --- کتابخانه‌ها ---
import jdatetime  # برای کار با تاریخ شمسی
import requests  # برای ارتباط با API بله
import json      # برای کار با داده‌های JSON
import time      # برای کار با زمان
import re       # برای کار با عبارات منظم
import logging  # برای ثبت گزارش‌ها
import os       # برای بررسی وجود فایل
import sys      # برای مدیریت سیستم

# --- تنظیمات اولیه ---
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
API_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates"
SEND_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
DATA_FILE = "1.json"

# --- تنظیمات لاگ ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot.log'
)

# --- کیبوردهای اصلی ---
def control_keyboard():
    """ایجاد کیبورد معمولی پیش‌فرض"""
    return {
        "keyboard": [
            [{"text": "🔁 شروع جدید"}, {"text": "🚫 خروج"}],
            [{"text": "🧹 پاک‌سازی اطلاعات"}]
        ],
        "resize_keyboard": True
    }

def admin_panel_keyboard():
    """ایجاد کیبورد پنل مدیریتی"""
    return {
        "keyboard": [
            [{"text": "🔁 شروع جدید"}, {"text": "📊 پنل کاربری"}],
            [{"text": "🧹 پاک‌سازی اطلاعات"}, {"text": "🚫 خروج"}]
        ],
        "resize_keyboard": True
    }

# --- ذخیره و بازیابی داده‌ها ---
def load_data():
    """بارگذاری داده‌ها از فایل JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}, "classes": {}, "trainers": {}, "assistants": {}}

def save_data(data):
    """ذخیره داده‌ها در فایل JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info("Data saved to JSON file")

# --- ارسال پیام ---
def send_message(chat_id, text, reply_markup=None):
    """ارسال پیام به کاربر یا گروه"""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    response = requests.post(SEND_URL, json=payload)
    logging.info(f"Message sent to {chat_id}: {text}")
    return response.json()

# --- بررسی مدیر ---
def is_first_user(data, user_id):
    """بررسی اینکه آیا کاربر اولین کاربر (مدیر) است"""
    return len(data["users"]) == 0

# --- اعتبارسنجی کد ملی ---
def validate_national_id(national_id):
    """اعتبارسنجی کد ملی ۱۰ رقمی"""
    return re.match(r'^\d{10}$', national_id) is not None

# --- تولید کد تصادفی برای مربی/کمک مربی ---
def generate_random_code():
    """تولید کد تصادفی ۶ رقمی"""
    import random
    code = str(random.randint(100000, 999999))
    logging.info(f"Random code generated: {code}")
    return code

# --- اصلی ---
def main():
    """تابع اصلی ربات"""
    data = load_data()
    offset = None
    user_states = {}  # ذخیره وضعیت موقت کاربران

    while True:
        try:
            # دریافت آپدیت‌ها
            params = {"offset": offset} if offset else {}
            response = requests.get(API_URL, params=params).json()
            if not response.get("ok"):
                logging.error("Failed to get updates")
                time.sleep(5)
                continue

            for update in response.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message", {})
                callback_query = update.get("callback_query", {})
                chat_id = message.get("chat", {}).get("id")
                user_id = str(message.get("from", {}).get("id", callback_query.get("from", {}).get("id")))
                text = message.get("text", "")
                contact = message.get("contact", {})
                callback_data = callback_query.get("data", "")

                if not chat_id or not user_id:
                    continue

                # بررسی وجود کاربر در داده‌ها
                if user_id not in data["users"]:
                    data["users"][user_id] = {}
                    if is_first_user(data, user_id):
                        data["users"][user_id]["role"] = "admin"
                        logging.info(f"User {user_id} registered as admin")

                user_data = data["users"][user_id]
                state = user_states.get(user_id, "start")

                # --- شروع ---
                if text == "/start" or text == "🔁 شروع جدید":
                    user_states[user_id] = "start"
                    if user_data.get("role") == "admin":
                        send_message(
                            chat_id,
                            f"_🌟 {user_data.get('first_name', 'کاربر')} عزیز، به ربات مدیریت گروه خوش آمدید!_\n"
                            f"شما مدیر هستید.\n"
                            f"لطفاً به پنل کاربری بروید یا ثبت‌نام را ادامه دهید.",
                            reply_markup=admin_panel_keyboard()
                        )
                    else:
                        send_message(
                            chat_id,
                            "_🌟 خوش آمدید! به ربات مدیریت گروه خوش آمدید!_\n"
                            "لطفاً نقش خود را انتخاب کنید.",
                            reply_markup={
                                "inline_keyboard": [
                                    [
                                        {"text": "👨‍🏫 مربی", "callback_data": "select_trainer"},
                                        {"text": "🤝 کمک مربی", "callback_data": "select_assistant"},
                                        {"text": "📚 قرآن‌آموز", "callback_data": "select_student"}
                                    ]
                                ]
                            }
                        )
                    continue

                # --- خروج ---
                if text == "🚫 خروج":
                    send_message(chat_id, "_👋 خدانگهدار!_", reply_markup={})
                    user_states.pop(user_id, None)
                    continue

                # --- پاک‌سازی اطلاعات ---
                if text == "🧹 پاک‌سازی اطلاعات":
                    user_states.pop(user_id, None)
                    send_message(chat_id, "_🧹 اطلاعات موقت پاک شد._", reply_markup=control_keyboard())
                    continue

                # --- پنل کاربری مدیر ---
                if text == "📊 پنل کاربری" and user_data.get("role") == "admin":
                    classes_list = "\n".join(
                        [f"{name}: {info['cost']} تومان - {info['link']}" for name, info in data["classes"].items()]
                    ) or "هیچ کلاسی ثبت نشده."
                    trainers_list = "\n".join(
                        [f"{info['full_name']}: {info['phone']}" for uid, info in data["trainers"].items()]
                    ) or "هیچ مربی‌ای ثبت نشده."
                    assistants_list = "\n".join(
                        [f"{info['full_name']}: {info['phone']}" for uid, info in data["assistants"].items()]
                    ) or "هیچ کمک مربی‌ای ثبت نشده."
                    send_message(
                        chat_id,
                        f"_📊 پنل مدیریتی_\n\n"
                        f"*لیست کلاس‌ها:*\n{classes_list}\n\n"
                        f"*لیست مربی‌ها:*\n{trainers_list}\n\n"
                        f"*لیست کمک مربی‌ها:*\n{assistants_list}\n\n"
                        f"برای مدیریت کلاس‌ها یا تأیید مربی‌ها، گزینه‌ها را انتخاب کنید.",
                        reply_markup={
                            "inline_keyboard": [
                                [{"text": "➕ افزودن کلاس", "callback_data": "add_class"}],
                                [{"text": "✏️ ویرایش کلاس", "callback_data": "edit_class"}],
                                [{"text": "📬 تأیید مربی‌ها", "callback_data": "confirm_trainer"}]
                            ]
                        }
                    )
                    continue

                # --- انتخاب نقش ---
                if callback_data in ["select_trainer", "select_assistant"]:
                    role = "trainer" if callback_data == "select_trainer" else "assistant"
                    user_states[user_id] = f"await_code_{role}"
                    code = generate_random_code()
                    user_data["temp_code"] = code
                    admin_id = next(uid for uid, info in data["users"].items() if info.get("role") == "admin")
                    send_message(
                        admin_id,
                        f"_📬 درخواست جدید_\n"
                        f"کاربر {user_id} درخواست {role} داده است.\n"
                        f"کد تأیید: `{code}`",
                        reply_markup=control_keyboard()
                    )
                    send_message(
                        chat_id,
                        "_لطفاً کد تأیید ارسال‌شده توسط مدیر را وارد کنید._",
                        reply_markup=control_keyboard()
                    )
                    continue

                # --- تأیید کد توسط مربی/کمک مربی ---
                if state.startswith("await_code_") and text.isdigit():
                    role = state.split("_")[-1]
                    if text == user_data.get("temp_code"):
                        user_data["role"] = role
                        user_states[user_id] = f"get_name_{role}"
                        send_message(
                            chat_id,
                            "_✅ کد تأیید شد._\n"
                            "لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی).",
                            reply_markup=control_keyboard()
                        )
                    else:
                        send_message(
                            chat_id,
                            "_❌ کد نامعتبر است. دوباره وارد کنید._",
                            reply_markup=control_keyboard()
                        )
                    continue

                # --- دریافت نام و نام خانوادگی ---
                if state.startswith("get_name_"):
                    role = state.split("_")[-1]
                    if re.match(r'^[\u0600-\u06FF\s]+$', text):
                        user_data["full_name"] = text
                        user_data["first_name"] = text.split()[0]
                        user_states[user_id] = f"get_national_id_{role}"
                        send_message(
                            chat_id,
                            f"_{user_data['first_name']} عزیز،_\n"
                            f"نام شما: {text}\n"
                            f"کد ملی: هنوز مانده\n"
                            f"تلفن: هنوز مانده\n\n"
                            f"لطفاً کد ملی ۱۰ رقمی خود را وارد کنید.",
                            reply_markup={
                                "keyboard": [
                                    [{"text": "🔁 شروع جدید"}, {"text": "🚫 خروج"}, {"text": "⬅️ برگشت به قبل"}]
                                ],
                                "resize_keyboard": True
                            },
                            {
                                "inline_keyboard": [[{"text": "✏️ تصحیح نام", "callback_data": f"edit_name_{role}"}]]
                            }
                        )
                    else:
                        send_message(
                            chat_id,
                            "_❌ نام نامعتبر است. لطفاً فقط حروف فارسی وارد کنید._",
                            reply_markup=control_keyboard()
                        )
                    continue

                # --- دریافت کد ملی ---
                if state.startswith("get_national_id_"):
                    role = state.split("_")[-1]
                    if validate_national_id(text):
                        user_data["national_id"] = text
                        user_states[user_id] = f"get_phone_{role}"
                        send_message(
                            chat_id,
                            f"_{user_data['first_name']} عزیز،_\n"
                            f"نام شما: {user_data['full_name']}\n"
                            f"کد ملی: {text}\n"
                            f"تلفن: هنوز مانده\n\n"
                            f"لطفاً برای ارسال شماره تلفن خود روی دکمه زیر بزنید.",
                            reply_markup={
                                "keyboard": [
                                    [{"text": "🔁 شروع جدید"}, {"text": "🚫 خروج"}, {"text": "⬅️ برگشت به قبل"}]
                                ],
                                "resize_keyboard": True
                            },
                            {
                                "inline_keyboard": [
                                    [{"text": "✏️ تصحیح کد ملی", "callback_data": f"edit_national_id_{role}"}],
                                    [{"text": "📱 ارسال شماره تلفن", "request_contact": True}]
                                ]
                            }
                        )
                    else:
                        send_message(
                            chat_id,
                            "_❌ کد ملی نامعتبر است. لطفاً ۱۰ رقم وارد کنید._",
                            reply_markup=control_keyboard()
                        )
                    continue

                # --- دریافت شماره تلفن ---
                if state.startswith("get_phone_") and contact:
                    role = state.split("_")[-1]
                    phone = contact.get("phone_number", "").replace("+", "")
                    if re.match(r'^989\d{9}$', phone):
                        user_data["phone"] = phone
                        user_states[user_id] = f"confirm_{role}"
                        send_message(
                            chat_id,
                            f"_📋 {user_data['first_name']} عزیز، حساب کاربری شما:_\n"
                            f"نام: {user_data['full_name']}\n"
                            f"کد ملی: {user_data['national_id']}\n"
                            f"تلفن: {phone}\n\n"
                            f"آیا اطلاعات درست است؟",
                            reply_markup={
                                "keyboard": [
                                    [{"text": "🔁 شروع جدید"}, {"text": "🚫 خروج"}, {"text": "⬅️ برگشت به قبل"}]
                                ],
                                "resize_keyboard": True
                            },
                            {
                                "inline_keyboard": [
                                    [{"text": "✅ تأیید نهایی", "callback_data": f"final_confirm_{role}"}],
                                    [{"text": "✏️ تصحیح اطلاعات", "callback_data": f"edit_info_{role}"}]
                                ]
                            }
                        )
                    else:
                        send_message(
                            chat_id,
                            "_❌ شماره تلفن نامعتبر است._",
                            reply_markup=control_keyboard()
                        )
                    continue

                # --- تأیید نهایی ---
                if callback_data.startswith("final_confirm_"):
                    role = callback_data.split("_")[-1]
                    data[role + "s"][user_id] = {
                        "full_name": user_data["full_name"],
                        "national_id": user_data["national_id"],
                        "phone": user_data["phone"]
                    }
                    save_data(data)
                    admin_id = next(uid for uid, info in data["users"].items() if info.get("role") == "admin")
                    send_message(
                        admin_id,
                        f"_📬 {user_data['first_name']} به عنوان {role} ثبت شد:_\n"
                        f"نام: {user_data['full_name']}\n"
                        f"کد ملی: {user_data['national_id']}\n"
                        f"تلفن: {user_data['phone']}"
                    )
                    send_message(
                        chat_id,
                        f"_🎉 {user_data['first_name']} عزیز، ثبت‌نام شما به عنوان {role} با موفقیت تکمیل شد!_\n"
                        f"لطفاً منتظر تأیید مدیر و لینک گروه باشید.",
                        reply_markup=control_keyboard()
                    )
                    user_states.pop(user_id, None)
                    continue

                # --- تصحیح اطلاعات ---
                if callback_data.startswith("edit_info_"):
                    role = callback_data.split("_")[-1]
                    user_states[user_id] = f"get_name_{role}"
                    send_message(
                        chat_id,
                        "_لطفاً نام و نام خانوادگی خود را دوباره وارد کنید._",
                        reply_markup=control_keyboard()
                    )
                    continue

                # --- افزودن کلاس توسط مدیر ---
                if callback_data == "add_class" and user_data.get("role") == "admin":
                    user_states[user_id] = "add_class_name"
                    send_message(
                        chat_id,
                        "_لطفاً نام کلاس را وارد کنید._",
                        reply_markup=control_keyboard()
                    )
                    continue

                if state == "add_class_name":
                    data["classes"][text] = {"cost": "", "link": ""}
                    user_states[user_id] = "add_class_cost"
                    send_message(
                        chat_id,
                        f"_نام کلاس: {text}_\n"
                        f"لطفاً هزینه کلاس را وارد کنید (به تومان).",
                        reply_markup=control_keyboard()
                    )
                    continue

                if state == "add_class_cost" and text.isdigit():
                    data["classes"][list(data["classes"].keys())[-1]]["cost"] = text
                    user_states[user_id] = "add_class_link"
                    send_message(
                        chat_id,
                        f"_هزینه کلاس: {text} تومان_\n"
                        f"لطفاً لینک گروه کلاس را وارد کنید (مثال: ble.ir/join/xxx).",
                        reply_markup=control_keyboard()
                    )
                    continue

                if state == "add_class_link" and re.match(r'^ble\.ir/join/[a-zA-Z0-9]+$', text):
                    data["classes"][list(data["classes"].keys())[-1]]["link"] = text
                    save_data(data)
                    send_message(
                        chat_id,
                        f"_✅ کلاس با موفقیت ثبت شد:_\n"
                        f"نام: {list(data['classes'].keys())[-1]}\n"
                        f"هزینه: {data['classes'][list(data['classes'].keys())[-1]]['cost']} تومان\n"
                        f"لینک: {text}",
                        reply_markup=admin_panel_keyboard()
                    )
                    user_states.pop(user_id, None)
                    continue

                # --- ویرایش کلاس ---
                if callback_data == "edit_class" and user_data.get("role") == "admin":
                    if not data["classes"]:
                        send_message(chat_id, "_هیچ کلاسی ثبت نشده است._", reply_markup=admin_panel_keyboard())
                    else:
                        buttons = [[{"text": name, "callback_data": f"edit_class_{name}"}] for name in data["classes"]]
                        send_message(
                            chat_id,
                            "_لطفاً کلاس موردنظر برای ویرایش را انتخاب کنید._",
                            reply_markup={"inline_keyboard": buttons}
                        )
                    continue

                # --- مدیریت آپدیت‌های بیشتر در آینده ---
                logging.info(f"Unhandled update: {update}")

        except Exception as e:
            logging.error(f"Error: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    logging.info("Bot started")
    main()