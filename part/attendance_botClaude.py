import requests
import json
import time
from datetime import datetime
import jdatetime

# تنظیمات بات
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

# کاربران مجاز
AUTHORIZED_USER_IDS = [
 574330749, #محمد زارع ۲
 1114227010 , # محمد  ۱
 1775811194, #محرابی 
 #فدوی 
# 1790308237, #ایرانسل
# 2045777722 #رایتل
# رشت بری 
# مردانی
#مربیان 
 ]

users = [f"کاربر{i+1}" for i in range(10)]
attendance_data = {}
user_states = {}  # ذخیره وضعیت فعلی هر کاربر

# تابع تبدیل تاریخ به فارسی
def get_persian_date():
    now = jdatetime.datetime.now()
    weekdays = {
        0: "شنبه",
        1: "یکشنبه", 
        2: "دوشنبه",
        3: "سه‌شنبه",
        4: "چهارشنبه",
        5: "پنج‌شنبه",
        6: "جمعه"
    }
    months = {
        1: "فروردین",
        2: "اردیبهشت", 
        3: "خرداد",
        4: "تیر",
        5: "مرداد",
        6: "شهریور",
        7: "مهر",
        8: "آبان",
        9: "آذر", 
        10: "دی",
        11: "بهمن",
        12: "اسفند"
    }
    
    weekday = weekdays[now.weekday()]
    month = months[now.month]
    return f"{weekday} {now.day} {month}"

# تابع ارسال پیام
def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": reply_markup
    }
    response = requests.post(url, json=payload)
    return response.status_code == 200

# تابع ویرایش پیام
def edit_message(chat_id, message_id, text, reply_markup=None):
    url = f"{BASE_URL}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "reply_markup": reply_markup
    }
    response = requests.post(url, json=payload)
    return response.status_code == 200

# تابع پاسخ به callback
def answer_callback_query(callback_query_id, text=None):
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    requests.post(url, json=payload)

# بررسی مجوز کاربر
def is_user_authorized(user_id):
    return user_id in AUTHORIZED_USER_IDS

# دریافت آپدیت‌ها
def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"offset": offset, "timeout": 30} if offset else {"timeout": 30}
    try:
        response = requests.get(url, params=params, timeout=35)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"خطا در دریافت آپدیت‌ها: {e}")
    return None

# منوی اصلی
def get_main_menu():
    return {
        "inline_keyboard": [
            [{"text": "📊 مشاهده لیست حضور و غیاب", "callback_data": "view_attendance"}],
            [{"text": "✏️ ثبت حضور و غیاب سریع", "callback_data": "quick_attendance"}],
            [{"text": "🔄 پاک کردن همه داده‌ها", "callback_data": "clear_all"}],
            [{"text": "📈 آمار کلی", "callback_data": "statistics"}]
        ]
    }

# نمایش لیست حضور و غیاب با آیکون‌های رنگی
def get_attendance_list():
    current_time = f"{get_persian_date()} - {datetime.now().strftime('%H:%M')}"
    text = f"📊 **لیست حضور و غیاب**\n🕐 آخرین بروزرسانی: {current_time}\n\n"
    
    status_icons = {
        "حاضر": "✅",
        "حضور با تاخیر": "⏰", 
        "غایب": "❌",
        "غیبت(موجه)": "📄",
        "در انتظار": "⏳"
    }
    
    for i, user in enumerate(users, 1):
        status = attendance_data.get(user, "در انتظار")
        icon = status_icons.get(status, "⏳")
        text += f"{i:2d}. {icon} {user} - {status}\n"
    
    # آمار سریع
    present = sum(1 for status in attendance_data.values() if status == "حاضر")
    late = sum(1 for status in attendance_data.values() if status == "حضور با تاخیر")
    absent = sum(1 for status in attendance_data.values() if status == "غایب")
    justified = sum(1 for status in attendance_data.values() if status == "غیبت(موجه)")
    
    text += f"\n📈 **آمار:**\n"
    text += f"✅ حاضر: {present} | ⏰ تاخیر: {late}\n"
    text += f"❌ غایب: {absent} | 📄 موجه: {justified}"
    
    return text

# کیبورد ثبت سریع حضور و غیاب
def get_quick_attendance_keyboard():
    keyboard = []
    # دکمه‌های تک‌تک برای کاربران (هر کاربر در یک ردیف)
    for i, user in enumerate(users):
        status = attendance_data.get(user, "⏳")
        status_icon = {"حاضر": "✅", "حضور با تاخیر": "⏰", "غایب": "❌", "غیبت(موجه)": "📄"}.get(status, "⏳")
        keyboard.append([{"text": f"{status_icon} {user}", "callback_data": f"select_user_{i}"}])
    
    # دکمه‌های کنترل
    keyboard.extend([
        [{"text": "✅ همه حاضر", "callback_data": "all_present"}, 
         {"text": "❌ همه غایب", "callback_data": "all_absent"}],
        [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]
    ])
    
    return {"inline_keyboard": keyboard}

# کیبورد انتخاب وضعیت برای هر کاربر
def get_status_keyboard(user_index):
    user = users[user_index]
    return {
        "inline_keyboard": [
            [
                {"text": "✅ حاضر", "callback_data": f"set_status_{user_index}_حاضر"},
                {"text": "⏰ حضور با تاخیر", "callback_data": f"set_status_{user_index}_حضور با تاخیر"}
            ],
            [
                {"text": "❌ غایب", "callback_data": f"set_status_{user_index}_غایب"},
                {"text": "📄 غیبت(موجه)", "callback_data": f"set_status_{user_index}_غیبت(موجه)"}
            ],
            [
                {"text": "🔙 برگشت", "callback_data": "quick_attendance"}
            ]
        ]
    }

# پردازش callback ها
def handle_callback_query(callback):
    chat_id = callback["message"]["chat"]["id"]
    message_id = callback["message"]["message_id"]
    user_id = callback["from"]["id"]
    data = callback["data"]
    callback_query_id = callback["id"]
    
    if not is_user_authorized(user_id):
        answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
        return
    
    # منوی اصلی
    if data == "main_menu":
        edit_message(chat_id, message_id, 
                    "🏠 **منوی اصلی**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", 
                    get_main_menu())
        answer_callback_query(callback_query_id)
    
    # مشاهده لیست
    elif data == "view_attendance":
        text = get_attendance_list()
        keyboard = {"inline_keyboard": [[{"text": "🔄 بروزرسانی", "callback_data": "view_attendance"}],
                                       [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]]}
        edit_message(chat_id, message_id, text, keyboard)
        answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
    
    # ثبت سریع
    elif data == "quick_attendance":
        edit_message(chat_id, message_id, 
                    "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:", 
                    get_quick_attendance_keyboard())
        answer_callback_query(callback_query_id)
    
    # انتخاب کاربر
    elif data.startswith("select_user_"):
        user_index = int(data.split("_")[-1])
        user = users[user_index]
        current_status = attendance_data.get(user, "در انتظار")
        edit_message(chat_id, message_id, 
                    f"👤 **{user}**\nوضعیت فعلی: {current_status}\n\nوضعیت جدید را انتخاب کنید:", 
                    get_status_keyboard(user_index))
        answer_callback_query(callback_query_id, f"انتخاب {user}")
    
    # تنظیم وضعیت
    elif data.startswith("set_status_"):
        parts = data.split("_")
        user_index = int(parts[2])
        status = parts[3]
        user = users[user_index]
        attendance_data[user] = status
        
        # مستقیماً برگشت به لیست ستونی کاربرها
        edit_message(chat_id, message_id, 
                    "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:", 
                    get_quick_attendance_keyboard())
        answer_callback_query(callback_query_id, f"✅ {user} - {status}")
    
    # همه حاضر
    elif data == "all_present":
        for user in users:
            attendance_data[user] = "حاضر"
        edit_message(chat_id, message_id, 
                    "✅ **همه کاربران حاضر علامت گذاری شدند**", 
                    {"inline_keyboard": [
                        [{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}],
                        [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
                    ]})
        answer_callback_query(callback_query_id, "✅ همه حاضر شدند")
    
    # همه غایب
    elif data == "all_absent":
        for user in users:
            attendance_data[user] = "غایب"
        edit_message(chat_id, message_id, 
                    "❌ **همه کاربران غایب علامت گذاری شدند**", 
                    {"inline_keyboard": [
                        [{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}],
                        [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
                    ]})
        answer_callback_query(callback_query_id, "❌ همه غایب شدند")
    
    # پاک کردن همه
    elif data == "clear_all":
        attendance_data.clear()
        edit_message(chat_id, message_id, 
                    "🗑️ **همه داده‌ها پاک شدند**", 
                    {"inline_keyboard": [
                        [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
                    ]})
        answer_callback_query(callback_query_id, "🗑️ داده‌ها پاک شدند")
    
    # آمار
    elif data == "statistics":
        total = len(users)
        present = sum(1 for status in attendance_data.values() if status == "حاضر")
        late = sum(1 for status in attendance_data.values() if status == "حضور با تاخیر")
        absent = sum(1 for status in attendance_data.values() if status == "غایب")
        justified = sum(1 for status in attendance_data.values() if status == "غیبت(موجه)")
        pending = total - len(attendance_data)
        
        stats_text = f"""📈 **آمار کلی حضور و غیاب**

👥 کل کاربران: {total}
✅ حاضر: {present} ({present/total*100:.1f}%)
⏰ حضور با تاخیر: {late} ({late/total*100:.1f}%)

❌ غایب: {absent} ({absent/total*100:.1f}%)
📄 غیبت(موجه): {justified} ({justified/total*100:.1f}%)
⏳ در انتظار: {pending} ({pending/total*100:.1f}%)

🕐 زمان آخرین بروزرسانی: {get_persian_date()} - {datetime.now().strftime("%H:%M")}"""
        
        edit_message(chat_id, message_id, stats_text, 
                    {"inline_keyboard": [
                        [{"text": "🔄 بروزرسانی آمار", "callback_data": "statistics"}],
                        [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]
                    ]})
        answer_callback_query(callback_query_id, "📊 آمار بروزرسانی شد")

# پردازش پیام‌های متنی
def handle_message(message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")
    
    if not is_user_authorized(user_id):
        print(f"🤖 id❌ {chat_id}.")
        send_message(chat_id, "❌ شما اجازه دسترسی به این بات را ندارید!")
        
        return
    
    if text == "/start":
        print(f"🤖 start id✅ {chat_id}.")
        welcome_text = f"""🎯 **بات حضور و غیاب**

سلام مربی عزیز! 👋
به بات حضور و غیاب خوش آمدید.

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد کاربران: {len(users)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
        
        # کیبورد معمولی
        keyboard = {
            "keyboard": [
                [{"text": "شروع"}, {"text": "خروج"}, {"text": "منوی اصلی"}]
            ],
            "resize_keyboard": True
        }
        
        send_message(chat_id, welcome_text, keyboard)
    
    elif text == "منوی اصلی":
        welcome_text = f"""🏠 **منوی اصلی**

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد کاربران: {len(users)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
        
        send_message(chat_id, welcome_text, get_main_menu())
    
    elif text == "شروع":
        print(f"🤖 شروع id✅ {chat_id}.")
        welcome_text = f"""🎯 **بات حضور و غیاب**

سلام مربی عزیز! 👋
به بات حضور و غیاب خوش آمدید.

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد کاربران: {len(users)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
        
        # کیبورد معمولی
        keyboard = {
            "keyboard": [
                [{"text": "شروع"}, {"text": "خروج"}, {"text": "منوی اصلی"}]
            ],
            "resize_keyboard": True
        }
        
        send_message(chat_id, welcome_text, keyboard)
    
    elif text == "خروج":
        send_message(chat_id, "👋 با تشکر از استفاده شما از بات حضور و غیاب. موفق باشید! 🌟")

# پردازش آپدیت‌ها
def handle_update(update):
    try:
        if "message" in update:
            handle_message(update["message"])
        elif "callback_query" in update:
            handle_callback_query(update["callback_query"])
    except Exception as e:
        print(f"خطا در پردازش آپدیت: {e}")

# حلقه اصلی بات
def main():
    offset = 0
    print("🤖 بات حضور و غیاب شروع شد...")
    print(f"🕐 زمان شروع: {get_persian_date()} - {datetime.now().strftime('%H:%M:%S')}")
    
    while True:
        try:
            updates = get_updates(offset)
            if updates and updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    handle_update(update)
            else:
                time.sleep(1)  # صبر کوتاه در صورت عدم دریافت آپدیت
        except KeyboardInterrupt:
            print("\n⛔ بات متوقف شد.")
            break
        except Exception as e:
            print(f"خطای غیرمنتظره: {e}")
            time.sleep(5)  # صبر 5 ثانیه در صورت خطا

if __name__ == "__main__":
    main()