import requests
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# تنظیمات بات
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# لیست کاربران مجاز (شماره موبایل و آیدی تلگرام)
AUTHORIZED_USERS = [
    {"phone": "989102175431", "user_id": 1114227010},  # مثال: شماره و آیدی مربی 1
    {"phone": "989942878984", "user_id": 574330749},  # مثال: شماره و آیدی مربی 2
]

# تنظیمات کاربران و وضعیت‌ها
users = [f"کاربر{i+1}" for i in range(10)]
statuses = ["حاضر", "تاخیر", "غایب", "موجه"]
attendance_data = {}

# ثبت فونت برای متن فارسی در PDF
FONT_NAME = "Persian"
FONT_PATH = "Vazirmatn-Regular.ttf"

try:
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
        print(f"فونت {FONT_PATH} با موفقیت ثبت شد")
    else:
        print(f"فونت {FONT_PATH} یافت نشد، از فونت پیش‌فرض استفاده می‌شود")
except Exception as e:
    print(f"خطا در ثبت فونت: {e}، از فونت پیش‌فرض استفاده می‌شود")

# تابع ارسال پیام به کاربر
def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"پیام با موفقیت به chat_id {chat_id} ارسال شد")
    else:
        print(f"خطا در ارسال پیام: {response.status_code}, {response.text}")
    return response.json()

# تابع ایجاد کیبورد شیشه‌ای برای انتخاب وضعیت
def create_inline_keyboard(user, edit_mode=False):
    prefix = "edit" if edit_mode else "status"
    keyboard = {
        "inline_keyboard": [[
            {"text": f"✅ {statuses[0]}", "callback_data": f"{prefix}_{user}_{statuses[0]}"},
            {"text": f"⏱ {statuses[1]}", "callback_data": f"{prefix}_{user}_{statuses[1]}"},
            {"text": f"🚫 {statuses[2]}", "callback_data": f"{prefix}_{user}_{statuses[2]}"},
            {"text": f"📄 {statuses[3]}", "callback_data": f"{prefix}_{user}_{statuses[3]}"}
        ]]
    }
    if not edit_mode:
        keyboard["inline_keyboard"].append([{"text": "✏ ویرایش", "callback_data": f"edit_{user}"}])
    return keyboard

# تابع بررسی دسترسی کاربر (بر اساس شماره موبایل یا آیدی)
def is_user_authorized(update):
    user_id = None
    phone_number = None
    
    if "message" in update:
        message = update["message"]
        user_id = message.get("from", {}).get("id")
        phone_number = message.get("contact", {}).get("phone_number")
    elif "callback_query" in update:
        user_id = update["callback_query"].get("from", {}).get("id")
        phone_number = update["callback_query"].get("from", {}).get("phone_number")
    
    # اطمینان از فرمت شماره موبایل
    if phone_number:
        phone_number = f"+{phone_number.lstrip('+')}"
    
    # بررسی دسترسی
    for authorized in AUTHORIZED_USERS:
        if user_id and authorized["user_id"] == user_id:
            return True
        if phone_number and authorized["phone"] == phone_number:
            return True
    return False

# تابع درخواست شماره تماس
def request_phone_number(chat_id):
    keyboard = {
        "keyboard": [[{"text": "ارسال شماره تماس", "request_contact": True}]],
        "one_time_keyboard": True,
        "resize_keyboard": True
    }
    send_message(chat_id, "لطفاً برای احراز هویت، شماره تماس خود را ارسال کنید:", {"reply_markup": keyboard})
    print(f"درخواست شماره تماس برای chat_id {chat_id} ارسال شد")

# تابع مدیریت آپدیت‌های دریافتی
def handle_update(update):
    chat_id = None
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
    elif "callback_query" in update:
        chat_id = update["callback_query"]["message"]["chat"]["id"]

    # بررسی دسترسی کاربر
    if not is_user_authorized(update):
        send_message(chat_id, "❌ شما اجازه دسترسی به این قابلیت را ندارید.\nلطفاً شماره تماس خود را ارسال کنید:")
        request_phone_number(chat_id)
        print(f"تلاش دسترسی غیرمجاز از chat_id {chat_id}")
        return

    if "message" in update:
        message = update["message"]
        text = message.get("text", "")

        if text == "لیست حضور غیاب":
            send_message(chat_id, "سلام مربی عزیز 👋\nبرای ثبت حضور و غیاب، لطفاً روی دکمه زیر کلیک کنید:", 
                        {"inline_keyboard": [[{"text": "📋 شروع ثبت", "callback_data": "start_attendance"}]]})
            print("دریافت دستور: نمایش لیست حضور و غیاب")

        elif text == "نمایش گزارش":
            generate_report(chat_id)
            print("دریافت دستور: تولید گزارش")

    elif "callback_query" in update:
        callback = update["callback_query"]
        callback_data = callback["data"]

        if callback_data == "start_attendance":
            for user in users:
                send_message(chat_id, f"📋 {user}\nلطفاً وضعیت را انتخاب کنید:", create_inline_keyboard(user))
            print("شروع فرآیند حضور و غیاب")

        elif callback_data.startswith("status_") or callback_data.startswith("edit_"):
            parts = callback_data.split("_")
            user = parts[1]
            status = parts[2] if len(parts) > 2 else None
            if status:
                attendance_data[user] = status
                send_message(chat_id, f"✔ وضعیت {user} ثبت شد: {status}")
                print(f"وضعیت به‌روزرسانی شد: {user} - {status}")

        elif callback_data.startswith("edit_"):
            user = callback_data.split("_")[1]
            send_message(chat_id, f"✏ ویرایش وضعیت {user}:\nلطفاً وضعیت جدید را انتخاب کنید:", create_inline_keyboard(user, edit_mode=True))
            print(f"حالت ویرایش برای {user} فعال شد")

# تابع تولید گزارش (متن، JSON و PDF)
def generate_report(chat_id):
    report = ["📋 گزارش نهایی حضور و غیاب:"]
    for user in users:
        status = attendance_data.get(user, "ثبت‌نشده")
        report.append(f"{user} - {status}")
    
    # ارسال گزارش متنی
    send_message(chat_id, "\n".join(report))
    print("گزارش متنی ارسال شد")

    # ذخیره گزارش JSON
    with open("attendance_report.json", "w", encoding="utf-8") as f:
        json.dump(attendance_data, f, ensure_ascii=False, indent=4)
    print("گزارش JSON ذخیره شد")

    # تولید و ارسال PDF
    pdf_file = "attendance_report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=A4)
    try:
        c.setFont(FONT_NAME, 12)
    except:
        c.setFont("Helvetica", 12)
        print("استفاده از فونت پیش‌فرض Helvetica برای PDF")
    
    y = 800
    c.drawString(100, y, "گزارش حضور و غیاب")
    y -= 30
    for line in report[1:]:
        c.drawString(100, y, line)
        y -= 20
    c.save()
    print("گزارش PDF تولید شد")

    # ارسال PDF
    with open(pdf_file, "rb") as f:
        url = f"{BASE_URL}/sendDocument"
        files = {"document": f}
        data = {"chat_id": chat_id, "caption": "📎 گزارش حضور و غیاب (PDF)"}
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("PDF با موفقیت ارسال شد")
        else:
            print(f"خطا در ارسال PDF: {response.status_code}, {response.text}")

# حلقه اصلی برنامه
def main():
    offset = 0
    print("بات شروع به کار کرد...")
    while True:
        try:
            url = f"{BASE_URL}/getUpdates?offset={offset}"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"خطا در دریافت آپدیت‌ها: {response.status_code}, {response.text}")
                continue

            data = response.json()
            if not data.get("ok") or not data.get("result"):
                continue

            for update in data["result"]:
                offset = update["update_id"] + 1
                handle_update(update)

        except Exception as e:
            print(f"خطا در حلقه اصلی: {e}")
            continue

if __name__ == "__main__":
    main()