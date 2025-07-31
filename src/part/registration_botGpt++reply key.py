#  میخوام دکمه اول و درست کنم . 
import os
import sys
import json
import time
import re
import logging
import requests

# 📌 پیکربندی اولیه
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
DATA_FILE = "1.json"

# 👑 پیکربندی مدیران و مربیان
#ADMIN_ID = "574330749"  # محرابی مدیر اصلی
ADMIN_ID = "1114227010"
# شناسه‌های مدیران و مربیان (chat_id)
TEACHERS = {
    "574330749": "مدیر",  # همراه2
    "1790308237": "معاون",  # رایت
    "1114227010": "مربی1",  # همراه1
    # می‌توانید مربیان دیگر را اینجا اضافه کنید
    # "teacher_id": "نام مربی"
}

# شماره‌های تلفن مدیران (برای تشخیص از طریق شماره تلفن)
ADMIN_PHONES = {
    "989942878984": "مدیر",  # شماره مدیر
    "989123456789": "معاون",  # شماره معاون
    # می‌توانید شماره‌های دیگر را اینجا اضافه کنید
    # "phone_number": "نقش"
}

logging.basicConfig(level=logging.INFO)

# 🧠 بارگذاری یا ایجاد فایل داده‌ها
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_data = load_data()

# 🎯 ارسال پیام همراه با کیبورد
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=payload)

# 🎛️ ساخت کیبورد معمولی
def make_keyboard(buttons):
    return {"keyboard": [[{"text": b} for b in row] for row in buttons], "resize_keyboard": True}

# 🧊 ساخت کیبورد شیشه‌ای
def make_inline_keyboard(buttons):
    return {"inline_keyboard": buttons}

# ✅ بررسی اعتبار کد ملی
def is_valid_national_id(nid):
    return bool(re.fullmatch(r"\d{10}", nid))

# 👑 بررسی مدیر بودن کاربر
def is_admin(user_id, phone=None):
    # بررسی از طریق chat_id
    if user_id in TEACHERS:
        return True, TEACHERS[user_id]
    
    # بررسی از طریق شماره تلفن
    if phone and phone in ADMIN_PHONES:
        return True, ADMIN_PHONES[phone]
    
    return False, None

# 🔁 مدیریت هر آپدیت
def handle_update(update):
    if "message" in update:
        message = update["message"]
        text = message.get("text", "")
        chat_id = message["chat"]["id"]
        user_id = str(chat_id)
        contact = message.get("contact")

        # 👑 بررسی مدیر بودن
        is_admin_user, admin_role = is_admin(user_id)
        if is_admin_user:
            if text == "/start" or text == "شروع مجدد":
                send_message(chat_id, 
                    f"_👑 {admin_role} عزیز، به پنل مدیریتی خوش آمدید!_",
                    reply_markup=make_keyboard([["📊 آمار کاربران", "👥 مدیریت کاربران"], ["📚 مدیریت کلاس‌ها", "⚙️ تنظیمات"], ["🔙 بازگشت به حالت عادی"]])
                )
                return
            elif text == "📊 آمار کاربران":
                total_users = len([u for u in user_data.keys() if u != "admin" and u != "classes" and u != "temp_class"])
                completed_users = len([u for u in user_data.keys() if u != "admin" and u != "classes" and u != "temp_class" and "phone" in user_data[u]])
                send_message(chat_id, f"_📊 آمار کاربران:_\n*کل کاربران:* {total_users}\n*تکمیل شده:* {completed_users}\n*ناقص:* {total_users - completed_users}")
            elif text == "👥 مدیریت کاربران":
                send_message(chat_id, "_👥 پنل مدیریت کاربران_", 
                    reply_markup=make_inline_keyboard([
                        [{"text": "📋 لیست کاربران", "callback_data": "list_users"}],
                        [{"text": "🔍 جستجوی کاربر", "callback_data": "search_user"}]
                    ])
                )
            elif text == "📚 مدیریت کلاس‌ها":
                send_message(chat_id, "_📚 پنل مدیریت کلاس‌ها_",
                    reply_markup=make_inline_keyboard([
                        [{"text": "➕ افزودن کلاس", "callback_data": "add_class"}],
                        [{"text": "📋 لیست کلاس‌ها", "callback_data": "list_classes"}]
                    ])
                )
            elif text == "🔙 بازگشت به حالت عادی":
                send_message(chat_id, "_🌟 خوش آمدید! به ربات ثبت‌نام آموزشگاه خوش آمدید!_",
                    reply_markup=make_keyboard([["شروع مجدد", "معرفی آموزشگاه", "خروج"]])
                )
                return

        # مرحله: شروع
        if text == "/start" or text == "شروع مجدد":
            # همیشه دکمه‌های معمولی را نمایش بده
            send_message(chat_id, "_🌟 خوش آمدید! به ربات ثبت‌نام آموزشگاه خوش آمدید!_",
                reply_markup=make_keyboard([["شروع مجدد", "معرفی آموزشگاه", "خروج"]])
            )
            
            # بررسی وضعیت کاربر
            if user_id in user_data and "full_name" in user_data[user_id]:
                first_name = user_data[user_id]["first_name"]
                full_name = user_data[user_id]["full_name"]
                national_id = user_data[user_id].get("national_id", "هنوز مانده")
                phone = user_data[user_id].get("phone", "هنوز مانده")
                
                send_message(chat_id,
                    f"_🌟 {first_name} عزیز، خوش آمدی!\n"
                    f"حساب کاربری شما آماده است 👇_\n"
                    f"*نام*: {full_name}\n"
                    f"*کد ملی*: {national_id}\n"
                    f"*تلفن*: {phone}",
                    reply_markup=make_inline_keyboard([
                        [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}],
                        [{"text": "📚 انتخاب کلاس", "callback_data": "choose_class"}]
                    ])
                )
            else:
                user_data[user_id] = {}  # فقط اگر ثبت‌نام نکرده، جدید بساز
                send_message(chat_id, "برای شروع ثبت‌نام روی دکمه زیر بزنید:",
                    reply_markup=make_inline_keyboard([[{"text": "📝 شروع ثبت‌نام", "callback_data": "start_registration"}]])
                )

        # 🎯 مدیریت دکمه‌های معمولی
        elif text == "معرفی آموزشگاه":
            send_message(chat_id, 
                "_🏫 *معرفی آموزشگاه*\n\n"
                "آموزشگاه ما با بیش از ۱۰ سال سابقه در زمینه آموزش قرآن کریم، "
                "خدمات متنوعی ارائه می‌دهد:\n\n"
                "📚 *کلاس‌های موجود:*\n"
                "• تجوید قرآن کریم\n"
                "• صوت و لحن\n"
                "• حفظ قرآن کریم\n"
                "• تفسیر قرآن\n\n"
                "💎 *مزایای ثبت‌نام:*\n"
                "• اساتید مجرب\n"
                "• کلاس‌های آنلاین و حضوری\n"
                "• گواهی پایان دوره\n"
                "• قیمت مناسب_\n\n"
                "برای ثبت‌نام روی دکمه زیر کلیک کنید:",
                reply_markup=make_inline_keyboard([[{"text": "📝 ثبت‌نام", "callback_data": "start_registration"}]])
            )
        
        elif text == "خروج":
            send_message(chat_id, "_👋 با تشکر از استفاده شما از ربات ما. موفق باشید! 🌟_")
        
        elif text == "برگشت به قبل":
            if user_id in user_data:
                # برگشت به مرحله قبل
                if "phone" in user_data[user_id]:
                    user_data[user_id].pop("phone", None)
                    save_data(user_data)
                    send_message(chat_id, "_لطفاً شماره تلفن خود را دوباره ارسال کنید._",
                        reply_markup={"keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]], "resize_keyboard": True}
                    )
                elif "national_id" in user_data[user_id]:
                    user_data[user_id].pop("national_id", None)
                    save_data(user_data)
                    send_message(chat_id, "_لطفاً کد ملی خود را دوباره وارد کنید._")
                elif "full_name" in user_data[user_id]:
                    user_data[user_id].pop("full_name", None)
                    save_data(user_data)
                    send_message(chat_id, "_لطفاً نام خود را دوباره وارد کنید._")
           
        elif user_id in user_data:
            state = user_data[user_id]
            
            # مرحله: نام
            if "full_name" not in state:
                user_data[user_id]["full_name"] = text
                user_data[user_id]["first_name"] = text.split()[0]
                save_data(user_data)
                send_message(chat_id, f"_{state['first_name']} عزیز،\nنام شما: {text}\nکد ملی: هنوز مانده\nتلفن: هنوز مانده_\n\nلطفاً کد ملی ۱۰ رقمی خود را وارد کنید.",
                    reply_markup=make_keyboard([["شروع مجدد", "خروج", "برگشت به قبل"]]))
                send_message(chat_id, "می‌خواهید نام را ویرایش کنید؟",
                    reply_markup=make_inline_keyboard([[{"text": "✏️ تصحیح نام", "callback_data": "edit_name"}]]))
            
            # مرحله: کد ملی
            elif "national_id" not in state:
                if is_valid_national_id(text):
                    user_data[user_id]["national_id"] = text
                    save_data(user_data)
                    send_message(
                        chat_id,
                        f"_{state['first_name']} عزیز،\nنام شما: {state['full_name']}\nکد ملی: {text}\nتلفن: هنوز مانده_\n\n📱 لطفاً شماره تلفن خود را با دکمه زیر ارسال کنید.",
                        reply_markup=make_keyboard([["شروع مجدد", "خروج", "برگشت به قبل"]])
                    )
                    send_message(
                        chat_id,
                        "👇👇👇",
                        reply_markup={
                            "keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]],
                            "resize_keyboard": True
                        }
                    )
                else:
                    send_message(chat_id, "_❌ کد ملی نامعتبر است. لطفاً ۱۰ رقم وارد کنید._")
            # مرحله: شماره تلفن
            elif "phone" not in state and contact:
                phone_number = contact["phone_number"]
                user_data[user_id]["phone"] = phone_number
                save_data(user_data)
                
                # بررسی مدیر بودن از طریق شماره تلفن
                is_admin_user, admin_role = is_admin(user_id, phone_number)
                if is_admin_user:
                    # اگر مدیر است، پیام ویژه نمایش بده
                    send_message(
                        chat_id,
                        f"_👑 {admin_role} عزیز،\n"
                        f"نام: {state['full_name']}\n"
                        f"کد ملی: {state['national_id']}\n"
                        f"تلفن: {phone_number}\n\n"
                        f"شما به عنوان {admin_role} شناسایی شدید! 🌟_",
                        reply_markup=make_inline_keyboard([
                            [{"text": "✅ تأیید نهایی", "callback_data": "final_confirm"}],
                            [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}],
                            [{"text": "👑 ورود به پنل مدیریتی", "callback_data": "admin_panel"}]
                        ])
                    )
                else:
                    # کاربر عادی
                    send_message(
                        chat_id,
                        f"_📋 {state['first_name']} عزیز، حساب کاربری شما:\nنام: {state['full_name']}\nکد ملی: {state['national_id']}\nتلفن: {phone_number}_",
                        reply_markup=make_inline_keyboard([
                            [{"text": "✅ تأیید نهایی", "callback_data": "final_confirm"}],
                            [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}]
                        ])
                    )

    elif "callback_query" in update:
        query = update["callback_query"]
        data = query["data"]
        chat_id = query["message"]["chat"]["id"]
        user_id = str(chat_id)

        if data == "start_registration":
            user_data[user_id] = {}
            save_data(user_data)
            send_message(chat_id, "_لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی)._")
        elif data == "edit_name":
            user_data[user_id].pop("full_name", None)
            save_data(user_data)
            send_message(chat_id, "_نام جدید را وارد کنید._")
        elif data == "edit_national_id":
            user_data[user_id].pop("national_id", None)
            save_data(user_data)
            send_message(chat_id, "_کد ملی جدید را وارد کنید._")
        elif data == "edit_info":
            user_data[user_id] = {}
            save_data(user_data)
            send_message(chat_id, "_بیایید دوباره شروع کنیم. لطفاً نام و نام خانوادگی خود را وارد کنید._")
        elif data == "final_confirm":
            send_message(chat_id, f"🎉 {user_data[user_id]['first_name']} عزیز، ثبت‌نام شما با موفقیت تکمیل شد! موفق باشید!")
        elif data == "choose_class":
            # نمایش کلاس‌های موجود
            classes = user_data.get("classes", [])
            if classes:
                class_text = "_📚 کلاس‌های موجود:_\n\n"
                for i, cls in enumerate(classes, 1):
                    class_text += f"*{i}. {cls['name']}*\n"
                    class_text += f"بخش: {cls['section']}\n"
                    class_text += f"قیمت: {cls['price']} تومان\n\n"
                send_message(chat_id, class_text)
            else:
                send_message(chat_id, "_📚 در حال حاضر کلاسی موجود نیست. لطفاً بعداً مراجعه کنید._")
        elif data == "admin_panel":
            # ورود به پنل مدیریتی
            is_admin_user, admin_role = is_admin(user_id)
            if is_admin_user:
                send_message(chat_id, 
                    f"_👑 {admin_role} عزیز، به پنل مدیریتی خوش آمدید!_",
                    reply_markup=make_keyboard([["📊 آمار کاربران", "👥 مدیریت کاربران"], ["📚 مدیریت کلاس‌ها", "⚙️ تنظیمات"], ["🔙 بازگشت به حالت عادی"]])
                )
            else:
                send_message(chat_id, "_❌ شما دسترسی مدیریتی ندارید._")

# ♻️ حلقه اصلی
def main():
    print("Bot is running...")
    last_update_id = 0
    while True:
        try:
            resp = requests.get(f"{BASE_URL}/getUpdates", params={"offset": last_update_id + 1})
            updates = resp.json().get("result", [])
            for update in updates:
                last_update_id = update["update_id"]
                handle_update(update)
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
