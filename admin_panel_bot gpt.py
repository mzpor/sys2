import json
import os
import logging
import requests
from time import sleep

# 🔧 تنظیمات اولیه
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
DATA_FILE = "1.json"

# 🎯 پیکربندی لاگ‌ها
logging.basicConfig(level=logging.INFO)

# 📦 بارگذاری یا ایجاد فایل اطلاعات
def load_data():
    """بارگذاری داده‌ها از فایل یا ایجاد فایل جدید"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # فایل وجود ندارد - ایجاد فایل جدید
            empty_data = {"admin": {}, "classes": []}
            save_data(empty_data)
            return empty_data
    except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
        # فایل خراب است - پاک کردن و ایجاد مجدد
        logging.error(f"خطا در بارگذاری فایل: {e}")
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        empty_data = {"admin": {}, "classes": []}
        save_data(empty_data)
        return empty_data

def save_data(data_to_save):
    """ذخیره داده‌ها در فایل"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        logging.info("داده‌ها با موفقیت ذخیره شدند")
    except Exception as e:
        logging.error(f"خطا در ذخیره فایل: {e}")

# بارگذاری داده‌ها
data = load_data()

# 📤 ارسال پیام

def send_message(chat_id, text, reply_markup=None):
    try:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = requests.post(f"{BASE_URL}/sendMessage", json=payload)
        if response.status_code != 200:
            logging.error(f"خطا در ارسال پیام: {response.text}")
    except Exception as e:
        logging.error(f"خطا در ارسال پیام: {e}")

# 📥 دریافت آپدیت‌ها

def get_updates(offset=None):
    try:
        url = f"{BASE_URL}/getUpdates"
        params = {"timeout": 100, "offset": offset}
        response = requests.get(url, params=params)
        return response.json().get("result", [])
    except Exception as e:
        logging.error(f"خطا در دریافت آپدیت‌ها: {e}")
        return []

# 📋 کیبوردها

def get_main_keyboard():
    return {"keyboard": [["شروع مجدد", "پنل کاربری"]], "resize_keyboard": True}

def get_inline_name_request():
    return {"inline_keyboard": [[{"text": "📝 وارد کردن نام و نام خانوادگی", "callback_data": "enter_name"}]]}

def get_inline_national_id():
    return {"inline_keyboard": [[{"text": "📍 وارد کردن کد ملی", "callback_data": "enter_nid"}]]}

def get_inline_confirm_admin():
    return {"inline_keyboard": [[{"text": "✅ تأیید اطلاعات", "callback_data": "confirm_admin"}]]}

def get_inline_add_class():
    return {"inline_keyboard": [[{"text": "➕ افزودن کلاس جدید", "callback_data": "add_class"}]]}

def get_inline_class_menu():
    return {"inline_keyboard": [
        [{"text": "📄 مشاهده کلاس‌ها", "callback_data": "view_classes"}],
        [{"text": "➕ افزودن کلاس", "callback_data": "add_class"}],
        [{"text": "✏️ ویرایش کلاس", "callback_data": "edit_class"}]
    ]}

# 🎯 وضعیت هر مدیر ذخیره می‌شود
admin_states = {}

# 🧠 پردازش پیام‌ها

def handle_message(message):
    chat_id = message["chat"]["id"]
    user_id = str(chat_id)
    text = message.get("text", "")
        # --- مدیریت ثبت‌نام مدیر ---
    if admin_states.get(user_id) == "awaiting_admin_name":
        data["admin"]["full_name"] = text
        data["admin"]["user_id"] = user_id  
        save_data(data)
        admin_states[user_id] = "awaiting_admin_nid"
        send_message(chat_id, "📍 لطفاً کد ملی خود را وارد کنید:")
        return

    if admin_states.get(user_id) == "awaiting_admin_nid":
        data["admin"]["national_id"] = text
        data["admin"]["user_id"] = user_id  # ثبت user_id مدیر
        save_data(data)
        admin_states[user_id] = "main_menu"
        send_message(chat_id, "✅ اطلاعات شما ثبت شد.", reply_markup=get_inline_confirm_admin())
        return
    # اگر مدیر قبلاً ثبت شده باشد
    if data["admin"].get("user_id") == user_id:
        state = admin_states.get(user_id, "main_menu")

        if text == "شروع مجدد":
            admin_states[user_id] = "main_menu"
            send_message(chat_id, "🔄 بازگشت به منوی اصلی.", reply_markup=get_main_keyboard())
        elif text == "پنل کاربری":
            send_message(chat_id, "👤 پنل مدیریت:", reply_markup=get_inline_class_menu())
        elif state == "awaiting_class_name":
            admin_states[user_id] = "awaiting_class_section"
            data["temp_class"] = {"name": text}
            send_message(chat_id, "✍️ لطفاً بخش کلاس را وارد کنید:")
        elif state == "awaiting_class_section":
            admin_states[user_id] = "awaiting_class_price"
            data["temp_class"]["section"] = text
            send_message(chat_id, "💰 لطفاً هزینه کلاس را وارد کنید:")
        elif state == "awaiting_class_price":
            admin_states[user_id] = "awaiting_class_link"
            data["temp_class"]["price"] = text
            send_message(chat_id, "🔗 لطفاً لینک گروه کلاس را وارد کنید:")
        elif state == "awaiting_class_link":
            class_obj = data["temp_class"]
            class_obj["link"] = text
            data["classes"].append(class_obj)
            save_data(data)
            admin_states[user_id] = "main_menu"
            send_message(chat_id, "✅ کلاس با موفقیت اضافه شد.", reply_markup=get_inline_class_menu())
        else:
            send_message(chat_id, "❓ لطفاً یکی از گزینه‌ها را انتخاب کنید.", reply_markup=get_main_keyboard())

    else:
        # اگر مدیر ثبت نشده باشد
        if "full_name" not in data["admin"]:
            send_message(chat_id, "🌟 به پنل مدیریت خوش آمدید!", reply_markup=get_inline_name_request())
        else:
            send_message(chat_id, "⛔ شما اجازه دسترسی ندارید.")

# 🎯 پردازش کال‌بک

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    user_id = str(chat_id)
    data_id = callback["id"]
    data_call = callback["data"]

    if data_call == "enter_name":
        admin_states[user_id] = "awaiting_admin_name"
        send_message(chat_id, "👤 لطفاً نام و نام خانوادگی خود را وارد کنید:")
    elif data_call == "enter_nid":
        admin_states[user_id] = "awaiting_admin_nid"
        send_message(chat_id, "📍 لطفاً کد ملی خود را وارد کنید:")
    elif data_call == "confirm_admin":
        data["admin"]["user_id"] = user_id
        save_data(data)
        send_message(chat_id, "✅ ثبت‌نام شما با موفقیت انجام شد.", reply_markup=get_main_keyboard())
    elif data_call == "add_class":
        admin_states[user_id] = "awaiting_class_name"
        send_message(chat_id, "📝 لطفاً نام کلاس را وارد کنید:")
    elif data_call == "view_classes":
        if not data["classes"]:
            send_message(chat_id, "❗ هیچ کلاسی ثبت نشده است.")
        else:
            text = "📚 لیست کلاس‌ها:\n"
            for idx, c in enumerate(data["classes"], 1):
                text += f"{idx}. {c['name']} | بخش: {c['section']} | 💰 {c['price']} | لینک: {c['link']}\n"
            send_message(chat_id, text)

# 🚀 تابع اصلی

def main():
    offset = None
    print("⏳ ربات در حال اجراست...")
    logging.info("ربات شروع شد")
    
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                if "message" in update:
                    handle_message(update["message"])
                elif "callback_query" in update:
                    handle_callback(update["callback_query"])
            sleep(1)
        except Exception as e:
            logging.error(f"خطا در حلقه اصلی: {e}")
            sleep(5)

if __name__ == "__main__":
    main()
