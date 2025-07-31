import requests
import json
import time
import os
from datetime import datetime
import jdatetime

# فایل کانفیگ
CONFIG_FILE = "room_config.json"

# بارگذاری کانفیگ
def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # کانفیگ پیش‌فرض
            default_config = {
                "bot_token": "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3",
                "admin_id": 574330749,  # مدیر اصلی سیستم
                "teacher_ids": [
                    574330749,  # محمد زارع ۲
                    1114227010,  # محمد ۱
                    1775811194,  # محرابی
                ],
                "data_file": "room_attendance_data.json"
            }
            # ذخیره کانفیگ پیش‌فرض
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            return default_config
    except Exception as e:
        print(f"خطا در بارگذاری کانفیگ: {e}")
        # کانفیگ اضطراری
        return {
            "bot_token": "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3",
            "admin_id": 574330749,
            "teacher_ids": [574330749, 1114227010, 1775811194],
            "data_file": "room_attendance_data.json"
        }

# بارگذاری کانفیگ
config = load_config()

# تنظیمات بات
BOT_TOKEN = config["bot_token"]
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
ADMIN_ID = config["admin_id"]
AUTHORIZED_TEACHER_IDS = config["teacher_ids"]
DATA_FILE = config["data_file"]

# بارگذاری داده‌ها
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"groups": {}, "attendance": {}}
    except Exception as e:
        print(f"خطا در بارگذاری داده‌ها: {e}")
        return {"groups": {}, "attendance": {}}

# ذخیره داده‌ها
def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"خطا در ذخیره داده‌ها: {e}")
        return False

# داده‌های سیستم
data = load_data()

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

# بررسی مجوز مدیر
def is_admin(user_id):
    return user_id == ADMIN_ID

# بررسی مجوز مربی
def is_teacher_authorized(user_id):
    return user_id in AUTHORIZED_TEACHER_IDS

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

# بررسی اینکه آیا کاربر ادمین گروه است
def is_user_admin(chat_id, user_id):
    url = f"{BASE_URL}/getChatMember"
    params = {"chat_id": chat_id, "user_id": user_id}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            result = response.json().get("result", {})
            status = result.get("status", "")
            # بررسی اینکه آیا کاربر ادمین است
            return status in ["creator", "administrator"]
    except:
        pass
    return False

# تابع اضافه کردن کاربر غیر ادمین به لیست
def add_non_admin_user(user_info, chat_id):
    user_id = user_info.get("id")
    first_name = user_info.get("first_name", "")
    last_name = user_info.get("last_name", "")
    username = user_info.get("username", "")
    
    # بررسی اینکه آیا کاربر ادمین است
    if is_user_admin(chat_id, user_id):
        return False, "❌ ادمین‌ها نمی‌توانند در لیست حضور و غیاب ثبت شوند."
    
    # ساخت نام کامل کاربر
    full_name = f"{first_name} {last_name}".strip()
    if not full_name:
        full_name = username if username else f"کاربر{user_id}"
    
    # اطمینان از وجود ساختار داده‌ها
    if "groups" not in data:
        data["groups"] = {}
    
    # تبدیل chat_id به رشته برای استفاده به عنوان کلید
    chat_id_str = str(chat_id)
    
    if chat_id_str not in data["groups"]:
        data["groups"][chat_id_str] = {}
    
    # بررسی اینکه آیا کاربر قبلاً در لیست است
    for existing_user_id, user_data in data["groups"][chat_id_str].items():
        if existing_user_id == str(user_id):
            return False, "این کاربر قبلاً در لیست حضور و غیاب ثبت شده است."
    
    # اضافه کردن کاربر جدید
    data["groups"][chat_id_str][str(user_id)] = {
        "name": full_name,
        "username": username,
        "added_time": datetime.now().strftime("%H:%M:%S"),
        "added_date": get_persian_date()
    }
    
    # ذخیره داده‌ها
    save_data(data)
    
    return True, f"✅ {full_name} به لیست حضور و غیاب اضافه شد."

# نمایش لیست کامل کاربران غیر ادمین یک گروه
def get_complete_members_list(chat_id):
    chat_id_str = str(chat_id)
    
    if "groups" not in data or chat_id_str not in data["groups"] or not data["groups"][chat_id_str]:
        return "⚠️ هیچ عضوی در لیست حضور و غیاب ثبت نشده است."
    
    members = data["groups"][chat_id_str]
    text = f"👥 **لیست کامل اعضای ثبت شده**\n\n"
    
    for i, (user_id, user_data) in enumerate(members.items(), 1):
        text += f"{i}. {user_data['name']}\n"
    
    text += f"\n📊 تعداد کل: {len(members)} نفر"
    return text

# منوی اصلی برای مدیر
def get_admin_main_menu():
    groups = []
    if "groups" in data:
        for group_id in data["groups"]:
            if data["groups"][group_id]:  # فقط گروه‌هایی که عضو دارند
                groups.append([{"text": f"📋 گروه {group_id}", "callback_data": f"admin_select_group_{group_id}"}])
    
    keyboard = [
        [{"text": "📊 مشاهده همه گروه‌ها", "callback_data": "admin_view_all_groups"}],
        [{"text": "🔄 بروزرسانی", "callback_data": "admin_refresh"}],
        [{"text": "⚙️ تنظیمات", "callback_data": "admin_settings"}]
    ]
    
    # اضافه کردن گروه‌ها به منو
    keyboard.extend(groups)
    
    return {"inline_keyboard": keyboard}

# منوی اصلی برای مربی
def get_teacher_main_menu(teacher_id):
    # پیدا کردن گروه‌هایی که مربی در آنها عضو است
    teacher_groups = []
    
    if "groups" in data:
        for group_id in data["groups"]:
            # بررسی اینکه آیا مربی در این گروه عضو است
            try:
                if is_user_admin(int(group_id), teacher_id):
                    teacher_groups.append(group_id)
            except:
                pass
    
    keyboard = []
    
    # اضافه کردن گروه‌های مربی به منو
    for group_id in teacher_groups:
        keyboard.append([{"text": f"📋 گروه {group_id}", "callback_data": f"teacher_select_group_{group_id}"}])
    
    # اضافه کردن دکمه‌های دیگر
    keyboard.append([{"text": "🔄 بروزرسانی", "callback_data": "teacher_refresh"}])
    
    return {"inline_keyboard": keyboard}

# نمایش لیست حضور و غیاب یک گروه
def get_attendance_list(group_id):
    group_id_str = str(group_id)
    current_time = f"{get_persian_date()} - {datetime.now().strftime('%H:%M')}"
    text = f"📊 **لیست حضور و غیاب گروه {group_id_str}**\n🕐 آخرین بروزرسانی: {current_time}\n\n"
    
    if "groups" not in data or group_id_str not in data["groups"] or not data["groups"][group_id_str]:
        text += "⚠️ هیچ عضوی در لیست حضور و غیاب ثبت نشده است.\n"
        text += "کاربران باید در گروه با دستور /عضو خود را اضافه کنند."
        return text
    
    members = data["groups"][group_id_str]
    
    # اطمینان از وجود ساختار داده‌های حضور و غیاب
    if "attendance" not in data:
        data["attendance"] = {}
    
    if group_id_str not in data["attendance"]:
        data["attendance"][group_id_str] = {}
    
    attendance = data["attendance"][group_id_str]
    today = get_persian_date()
    
    status_icons = {
        "حاضر": "✅",
        "حضور با تاخیر": "⏰", 
        "غایب": "❌",
        "غیبت(موجه)": "📄",
        "در انتظار": "⏳"
    }
    
    for i, (user_id, user_data) in enumerate(members.items(), 1):
        user_name = user_data["name"]
        status = "در انتظار"
        
        # بررسی وضعیت حضور و غیاب امروز
        if today in attendance and user_id in attendance[today]:
            status = attendance[today][user_id]
        
        icon = status_icons.get(status, "⏳")
        text += f"{i:2d}. {icon} {user_name} - {status}\n"
    
    # آمار سریع
    if today in attendance:
        present = sum(1 for status in attendance[today].values() if status == "حاضر")
        late = sum(1 for status in attendance[today].values() if status == "حضور با تاخیر")
        absent = sum(1 for status in attendance[today].values() if status == "غایب")
        justified = sum(1 for status in attendance[today].values() if status == "غیبت(موجه)")
        
        text += f"\n📈 **آمار:**\n"
        text += f"✅ حاضر: {present} | ⏰ تاخیر: {late}\n"
        text += f"❌ غایب: {absent} | 📄 موجه: {justified}"
    else:
        text += "\n⚠️ هنوز هیچ حضور و غیابی برای امروز ثبت نشده است."
    
    return text

# کیبورد ثبت سریع حضور و غیاب برای یک گروه
def get_quick_attendance_keyboard(group_id):
    group_id_str = str(group_id)
    
    if "groups" not in data or group_id_str not in data["groups"] or not data["groups"][group_id_str]:
        return {"inline_keyboard": [[{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]]}
    
    members = data["groups"][group_id_str]
    
    # اطمینان از وجود ساختار داده‌های حضور و غیاب
    if "attendance" not in data:
        data["attendance"] = {}
    
    if group_id_str not in data["attendance"]:
        data["attendance"][group_id_str] = {}
    
    attendance = data["attendance"][group_id_str]
    today = get_persian_date()
    
    if today not in attendance:
        attendance[today] = {}
    
    keyboard = []
    # دکمه‌های تک‌تک برای کاربران (هر کاربر در یک ردیف)
    for user_id, user_data in members.items():
        user_name = user_data["name"]
        status = "در انتظار"
        
        # بررسی وضعیت حضور و غیاب امروز
        if user_id in attendance[today]:
            status = attendance[today][user_id]
        
        status_icon = {"حاضر": "✅", "حضور با تاخیر": "⏰", "غایب": "❌", "غیبت(موجه)": "📄"}.get(status, "⏳")
        keyboard.append([{"text": f"{status_icon} {user_name}", "callback_data": f"select_user_{group_id_str}_{user_id}"}])
    
    # دکمه‌های کنترل
    keyboard.extend([
        [{"text": "✅ همه حاضر", "callback_data": f"all_present_{group_id_str}"}, 
         {"text": "❌ همه غایب", "callback_data": f"all_absent_{group_id_str}"}],
        [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]
    ])
    
    return {"inline_keyboard": keyboard}

# کیبورد انتخاب وضعیت برای هر کاربر
def get_status_keyboard(group_id, user_id):
    return {
        "inline_keyboard": [
            [
                {"text": "✅ حاضر", "callback_data": f"set_status_{group_id}_{user_id}_حاضر"},
                {"text": "⏰ حضور با تاخیر", "callback_data": f"set_status_{group_id}_{user_id}_حضور با تاخیر"}
            ],
            [
                {"text": "❌ غایب", "callback_data": f"set_status_{group_id}_{user_id}_غایب"},
                {"text": "📄 غیبت(موجه)", "callback_data": f"set_status_{group_id}_{user_id}_غیبت(موجه)"}
            ],
            [
                {"text": "🔙 برگشت", "callback_data": f"quick_attendance_{group_id}"}
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
    
    # بررسی نوع کاربر
    is_user_admin_role = is_admin(user_id)
    is_user_teacher = is_teacher_authorized(user_id)
    
    # منوی اصلی
    if data == "main_menu":
        if is_user_admin_role:
            edit_message(chat_id, message_id, 
                        "🏠 **منوی اصلی مدیر**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", 
                        get_admin_main_menu())
        elif is_user_teacher:
            edit_message(chat_id, message_id, 
                        "🏠 **منوی اصلی مربی**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", 
                        get_teacher_main_menu(user_id))
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
            return
        
        answer_callback_query(callback_query_id)
    
    # بروزرسانی منوی مدیر
    elif data == "admin_refresh":
        if is_user_admin_role:
            edit_message(chat_id, message_id, 
                        "🏠 **منوی اصلی مدیر**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", 
                        get_admin_main_menu())
            answer_callback_query(callback_query_id, "✅ منو بروزرسانی شد")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # بروزرسانی منوی مربی
    elif data == "teacher_refresh":
        if is_user_teacher:
            edit_message(chat_id, message_id, 
                        "🏠 **منوی اصلی مربی**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", 
                        get_teacher_main_menu(user_id))
            answer_callback_query(callback_query_id, "✅ منو بروزرسانی شد")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # مدیر - مشاهده همه گروه‌ها
    elif data == "admin_view_all_groups":
        if is_user_admin_role:
            if "groups" not in data or not data["groups"]:
                text = "⚠️ هیچ گروهی یافت نشد."
            else:
                text = "📋 **لیست همه گروه‌ها**\n\n"
                for i, (group_id, members) in enumerate(data["groups"].items(), 1):
                    text += f"{i}. گروه {group_id} - {len(members)} عضو\n"
            
            keyboard = {"inline_keyboard": [[{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]]}
            edit_message(chat_id, message_id, text, keyboard)
            answer_callback_query(callback_query_id)
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # مدیر - انتخاب گروه
    elif data.startswith("admin_select_group_"):
        if is_user_admin_role:
            group_id = data.replace("admin_select_group_", "")
            keyboard = {"inline_keyboard": [
                [{"text": "📊 مشاهده لیست حضور و غیاب", "callback_data": f"admin_view_attendance_{group_id}"}],
                [{"text": "✏️ ثبت حضور و غیاب سریع", "callback_data": f"admin_quick_attendance_{group_id}"}],
                [{"text": "🔄 پاک کردن داده‌های گروه", "callback_data": f"admin_clear_group_{group_id}"}],
                [{"text": "📈 آمار گروه", "callback_data": f"admin_statistics_{group_id}"}],
                [{"text": "👥 لیست اعضای گروه", "callback_data": f"admin_show_members_{group_id}"}],
                [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]
            ]}
            edit_message(chat_id, message_id, f"📋 **مدیریت گروه {group_id}**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", keyboard)
            answer_callback_query(callback_query_id)
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # مربی - انتخاب گروه
    elif data.startswith("teacher_select_group_"):
        if is_user_teacher:
            group_id = data.replace("teacher_select_group_", "")
            keyboard = {"inline_keyboard": [
                [{"text": "📊 مشاهده لیست حضور و غیاب", "callback_data": f"teacher_view_attendance_{group_id}"}],
                [{"text": "✏️ ثبت حضور و غیاب سریع", "callback_data": f"teacher_quick_attendance_{group_id}"}],
                [{"text": "👥 لیست اعضای گروه", "callback_data": f"teacher_show_members_{group_id}"}],
                [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]
            ]}
            edit_message(chat_id, message_id, f"📋 **مدیریت گروه {group_id}**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", keyboard)
            answer_callback_query(callback_query_id)
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # مدیر - مشاهده لیست حضور و غیاب گروه
    elif data.startswith("admin_view_attendance_"):
        if is_user_admin_role:
            group_id = data.replace("admin_view_attendance_", "")
            text = get_attendance_list(group_id)
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": f"admin_view_attendance_{group_id}"}],
                [{"text": "🏠 برگشت به منو گروه", "callback_data": f"admin_select_group_{group_id}"}]
            ]}
            edit_message(chat_id, message_id, text, keyboard)
            answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # مربی - مشاهده لیست حضور و غیاب گروه
    elif data.startswith("teacher_view_attendance_"):
        if is_user_teacher:
            group_id = data.replace("teacher_view_attendance_", "")
            text = get_attendance_list(group_id)
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": f"teacher_view_attendance_{group_id}"}],
                [{"text": "🏠 برگشت به منو گروه", "callback_data": f"teacher_select_group_{group_id}"}]
            ]}
            edit_message(chat_id, message_id, text, keyboard)
            answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # مدیر - ثبت سریع حضور و غیاب گروه
    elif data.startswith("admin_quick_attendance_"):
        if is_user_admin_role:
            group_id = data.replace("admin_quick_attendance_", "")
            edit_message(chat_id, message_id, 
                        f"✏️ **ثبت سریع حضور و غیاب گروه {group_id}**\nروی نام هر کاربر کلیک کنید:", 
                        get_quick_attendance_keyboard(group_id))
            answer_callback_query(callback_query_id)
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # مربی - ثبت سریع حضور و غیاب گروه
    elif data.startswith("teacher_quick_attendance_"):
        if is_user_teacher:
            group_id = data.replace("teacher_quick_attendance_", "")
            edit_message(chat_id, message_id, 
                        f"✏️ **ثبت سریع حضور و غیاب گروه {group_id}**\nروی نام هر کاربر کلیک کنید:", 
                        get_quick_attendance_keyboard(group_id))
            answer_callback_query(callback_query_id)
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # انتخاب کاربر برای تغییر وضعیت
    elif data.startswith("select_user_"):
        if is_user_admin_role or is_user_teacher:
            parts = data.split("_")
            group_id = parts[2]
            user_id = parts[3]
            
            # بررسی اینکه آیا مربی مجاز به تغییر وضعیت این گروه است
            if is_user_teacher and not is_user_admin_role:
                try:
                    if not is_user_admin(int(group_id), user_id):
                        answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی به این گروه را ندارید!")
                        return
                except:
                    answer_callback_query(callback_query_id, "❌ خطا در بررسی دسترسی!")
                    return
            
            group_id_str = str(group_id)
            user_id_str = str(user_id)
            
            if "groups" in data and group_id_str in data["groups"] and user_id_str in data["groups"][group_id_str]:
                user_data = data["groups"][group_id_str][user_id_str]
                user_name = user_data["name"]
                
                # اطمینان از وجود ساختار داده‌های حضور و غیاب
                if "attendance" not in data:
                    data["attendance"] = {}
                
                if group_id_str not in data["attendance"]:
                    data["attendance"][group_id_str] = {}
                
                today = get_persian_date()
                
                if today not in data["attendance"][group_id_str]:
                    data["attendance"][group_id_str][today] = {}
                
                current_status = "در انتظار"
                if user_id_str in data["attendance"][group_id_str][today]:
                    current_status = data["attendance"][group_id_str][today][user_id_str]
                
                edit_message(chat_id, message_id, 
                            f"👤 **{user_name}**\nوضعیت فعلی: {current_status}\n\nوضعیت جدید را انتخاب کنید:", 
                            get_status_keyboard(group_id, user_id))
                answer_callback_query(callback_query_id, f"انتخاب {user_name}")
            else:
                answer_callback_query(callback_query_id, "❌ کاربر یافت نشد")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # تنظیم وضعیت کاربر
    elif data.startswith("set_status_"):
        if is_user_admin_role or is_user_teacher:
            parts = data.split("_")
            group_id = parts[2]
            user_id = parts[3]
            status = parts[4]
            
            # بررسی اینکه آیا مربی مجاز به تغییر وضعیت این گروه است
            if is_user_teacher and not is_user_admin_role:
                try:
                    if not is_user_admin(int(group_id), user_id):
                        answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی به این گروه را ندارید!")
                        return
                except:
                    answer_callback_query(callback_query_id, "❌ خطا در بررسی دسترسی!")
                    return
            
            group_id_str = str(group_id)
            user_id_str = str(user_id)
            
            # اطمینان از وجود ساختار داده‌های حضور و غیاب
            if "attendance" not in data:
                data["attendance"] = {}
            
            if group_id_str not in data["attendance"]:
                data["attendance"][group_id_str] = {}
            
            today = get_persian_date()
            
            if today not in data["attendance"][group_id_str]:
                data["attendance"][group_id_str][today] = {}
            
            # ثبت وضعیت جدید
            data["attendance"][group_id_str][today][user_id_str] = status
            save_data(data)
            
            # برگشت به لیست ثبت سریع
            if is_user_admin_role:
                edit_message(chat_id, message_id, 
                            f"✏️ **ثبت سریع حضور و غیاب گروه {group_id}**\nروی نام هر کاربر کلیک کنید:", 
                            get_quick_attendance_keyboard(group_id))
            else:
                edit_message(chat_id, message_id, 
                            f"✏️ **ثبت سریع حضور و غیاب گروه {group_id}**\nروی نام هر کاربر کلیک کنید:", 
                            get_quick_attendance_keyboard(group_id))
            
            # نمایش نام کاربر در پیام کوتاه
            user_name = "کاربر"
            if "groups" in data and group_id_str in data["groups"] and user_id_str in data["groups"][group_id_str]:
                user_name = data["groups"][group_id_str][user_id_str]["name"]
            
            answer_callback_query(callback_query_id, f"✅ {user_name} - {status}")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # همه حاضر
    elif data.startswith("all_present_"):
        if is_user_admin_role or is_user_teacher:
            group_id = data.replace("all_present_", "")
            
            # بررسی اینکه آیا مربی مجاز به تغییر وضعیت این گروه است
            if is_user_teacher and not is_user_admin_role:
                try:
                    if not is_user_admin(int(group_id), user_id):
                        answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی به این گروه را ندارید!")
                        return
                except:
                    answer_callback_query(callback_query_id, "❌ خطا در بررسی دسترسی!")
                    return
            
            group_id_str = str(group_id)
            
            if "groups" in data and group_id_str in data["groups"]:
                # اطمینان از وجود ساختار داده‌های حضور و غیاب
                if "attendance" not in data:
                    data["attendance"] = {}
                
                if group_id_str not in data["attendance"]:
                    data["attendance"][group_id_str] = {}
                
                today = get_persian_date()
                
                if today not in data["attendance"][group_id_str]:
                    data["attendance"][group_id_str][today] = {}
                
                # ثبت همه کاربران به عنوان حاضر
                for user_id in data["groups"][group_id_str]:
                    data["attendance"][group_id_str][today][user_id] = "حاضر"
                
                save_data(data)
                
                # نمایش پیام تأیید
                if is_user_admin_role:
                    keyboard = {"inline_keyboard": [
                        [{"text": "📊 مشاهده لیست", "callback_data": f"admin_view_attendance_{group_id}"}],
                        [{"text": "🏠 برگشت به منو گروه", "callback_data": f"admin_select_group_{group_id}"}]
                    ]}
                else:
                    keyboard = {"inline_keyboard": [
                        [{"text": "📊 مشاهده لیست", "callback_data": f"teacher_view_attendance_{group_id}"}],
                        [{"text": "🏠 برگشت به منو گروه", "callback_data": f"teacher_select_group_{group_id}"}]
                    ]}
                
                edit_message(chat_id, message_id, 
                            f"✅ **همه کاربران گروه {group_id} حاضر علامت گذاری شدند**", 
                            keyboard)
                answer_callback_query(callback_query_id, "✅ همه حاضر شدند")
            else:
                answer_callback_query(callback_query_id, "❌ گروه یافت نشد")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # همه غایب
    elif data.startswith("all_absent_"):
        if is_user_admin_role or is_user_teacher:
            group_id = data.replace("all_absent_", "")
            
            # بررسی اینکه آیا مربی مجاز به تغییر وضعیت این گروه است
            if is_user_teacher and not is_user_admin_role:
                try:
                    if not is_user_admin(int(group_id), user_id):
                        answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی به این گروه را ندارید!")
                        return
                except:
                    answer_callback_query(callback_query_id, "❌ خطا در بررسی دسترسی!")
                    return
            
            group_id_str = str(group_id)
            
            if "groups" in data and group_id_str in data["groups"]:
                # اطمینان از وجود ساختار داده‌های حضور و غیاب
                if "attendance" not in data:
                    data["attendance"] = {}
                
                if group_id_str not in data["attendance"]:
                    data["attendance"][group_id_str] = {}
                
                today = get_persian_date()
                
                if today not in data["attendance"][group_id_str]:
                    data["attendance"][group_id_str][today] = {}
                
                # ثبت همه کاربران به عنوان غایب
                for user_id in data["groups"][group_id_str]:
                    data["attendance"][group_id_str][today][user_id] = "غایب"
                
                save_data(data)
                
                # نمایش پیام تأیید
                if is_user_admin_role:
                    keyboard = {"inline_keyboard": [
                        [{"text": "📊 مشاهده لیست", "callback_data": f"admin_view_attendance_{group_id}"}],
                        [{"text": "🏠 برگشت به منو گروه", "callback_data": f"admin_select_group_{group_id}"}]
                    ]}
                else:
                    keyboard = {"inline_keyboard": [
                        [{"text": "📊 مشاهده لیست", "callback_data": f"teacher_view_attendance_{group_id}"}],
                        [{"text": "🏠 برگشت به منو گروه", "callback_data": f"teacher_select_group_{group_id}"}]
                    ]}
                
                edit_message(chat_id, message_id, 
                            f"❌ **همه کاربران گروه {group_id} غایب علامت گذاری شدند**", 
                            keyboard)
                answer_callback_query(callback_query_id, "❌ همه غایب شدند")
            else:
                answer_callback_query(callback_query_id, "❌ گروه یافت نشد")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # مدیر - پاک کردن داده‌های گروه
    elif data.startswith("admin_clear_group_"):
        if is_user_admin_role:
            group_id = data.replace("admin_clear_group_", "")
            group_id_str = str(group_id)
            
            # پاک کردن داده‌های حضور و غیاب گروه
            if "attendance" in data and group_id_str in data["attendance"]:
                data["attendance"][group_id_str] = {}
            
            save_data(data)
            
            edit_message(chat_id, message_id, 
                        f"🗑️ **داده‌های حضور و غیاب گروه {group_id} پاک شدند**", 
                        {"inline_keyboard": [[{"text": "🏠 برگشت به منو گروه", "callback_data": f"admin_select_group_{group_id}"}]]})
            answer_callback_query(callback_query_id, "🗑️ داده‌ها پاک شدند")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # مدیر - آمار گروه
    elif data.startswith("admin_statistics_"):
        if is_user_admin_role:
            group_id = data.replace("admin_statistics_", "")
            group_id_str = str(group_id)
            
            if "groups" in data and group_id_str in data["groups"]:
                total = len(data["groups"][group_id_str])
                
                if total == 0:
                    stats_text = "⚠️ هیچ عضوی در لیست حضور و غیاب ثبت نشده است."
                else:
                    today = get_persian_date()
                    present = 0
                    late = 0
                    absent = 0
                    justified = 0
                    pending = total
                    
                    if "attendance" in data and group_id_str in data["attendance"] and today in data["attendance"][group_id_str]:
                        attendance_today = data["attendance"][group_id_str][today]
                        present = sum(1 for status in attendance_today.values() if status == "حاضر")
                        late = sum(1 for status in attendance_today.values() if status == "حضور با تاخیر")
                        absent = sum(1 for status in attendance_today.values() if status == "غایب")
                        justified = sum(1 for status in attendance_today.values() if status == "غیبت(موجه)")
                        pending = total - len(attendance_today)
                    
                    stats_text = f"""📈 **آمار کلی حضور و غیاب گروه {group_id}**

👥 کل کاربران: {total}
✅ حاضر: {present} ({present/total*100:.1f}%)
⏰ حضور با تاخیر: {late} ({late/total*100:.1f}%)

❌ غایب: {absent} ({absent/total*100:.1f}%)
📄 غیبت(موجه): {justified} ({justified/total*100:.1f}%)
⏳ در انتظار: {pending} ({pending/total*100:.1f}%)

🕐 زمان آخرین بروزرسانی: {get_persian_date()} - {datetime.now().strftime("%H:%M")}"""                
                
                keyboard = {"inline_keyboard": [
                    [{"text": "🔄 بروزرسانی آمار", "callback_data": f"admin_statistics_{group_id}"}],
                    [{"text": "🏠 برگشت به منو گروه", "callback_data": f"admin_select_group_{group_id}"}]
                ]}
                
                edit_message(chat_id, message_id, stats_text, keyboard)
                answer_callback_query(callback_query_id, "📊 آمار بروزرسانی شد")
            else:
                answer_callback_query(callback_query_id, "❌ گروه یافت نشد")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # مدیر - نمایش لیست اعضای گروه
    elif data.startswith("admin_show_members_"):
        if is_user_admin_role:
            group_id = data.replace("admin_show_members_", "")
            text = get_complete_members_list(group_id)
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": f"admin_show_members_{group_id}"}],
                [{"text": "🏠 برگشت به منو گروه", "callback_data": f"admin_select_group_{group_id}"}]
            ]}
            edit_message(chat_id, message_id, text, keyboard)
            answer_callback_query(callback_query_id, "👥 لیست اعضا")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
    
    # مربی - نمایش لیست اعضای گروه
    elif data.startswith("teacher_show_members_"):
        if is_user_teacher:
            group_id = data.replace("teacher_show_members_", "")
            
            # بررسی اینکه آیا مربی مجاز به دیدن این گروه است
            try:
                if not is_user_admin(int(group_id), user_id):
                    answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی به این گروه را ندارید!")
                    return
            except:
                answer_callback_query(callback_query_id, "❌ خطا در بررسی دسترسی!")
                return
            
            text = get_complete_members_list(group_id)
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": f"teacher_show_members_{group_id}"}],
                [{"text": "🏠 برگشت به منو گروه", "callback_data": f"teacher_select_group_{group_id}"}]
            ]}
            edit_message(chat_id, message_id, text, keyboard)
            answer_callback_query(callback_query_id, "👥 لیست اعضا")
        else:
            answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")

# پردازش پیام‌های متنی
def handle_message(message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")
    chat_type = message["chat"].get("type", "")
    
    # بررسی نوع چت
    is_private = chat_type == "private"
    is_group = chat_type in ["group", "supergroup"]
    
    # بررسی نوع کاربر
    is_user_admin_role = is_admin(user_id)
    is_user_teacher = is_teacher_authorized(user_id)
    
    if text == "/start":
        print(f"🤖 start id✅ {chat_id}.")
        
        if is_private:
            # در خصوصی - برای مدیر یا مربی
            if is_user_admin_role:
                welcome_text = f"""🎯 **بات حضور و غیاب - مدیر**

سلام مدیر عزیز! 👋
به پنل مدیریت حضور و غیاب خوش آمدید.

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                
                send_message(chat_id, welcome_text, get_admin_main_menu())
            elif is_user_teacher:
                welcome_text = f"""🎯 **بات حضور و غیاب - مربی**

سلام مربی عزیز! 👋
به پنل مدیریت حضور و غیاب خوش آمدید.

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                
                send_message(chat_id, welcome_text, get_teacher_main_menu(user_id))
            else:
                send_message(chat_id, "❌ شما اجازه دسترسی به پنل مدیریت را ندارید!")
        
        elif is_group:
            # در گروه - برای همه
            welcome_text = f"""🎯 **بات حضور و غیاب**

سلام! 👋
به بات حضور و غیاب خوش آمدید.

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}

برای عضویت در لیست حضور و غیاب، دستور /عضو را بزنید."""
            
            send_message(chat_id, welcome_text)
    
    elif text == "/عضو":
        print(f"🤖 عضو id✅ {chat_id}.")
        
        if is_group:
            # فقط در گروه می‌توان عضو شد
            user_info = message["from"]
            success, message_text = add_non_admin_user(user_info, chat_id)
            send_message(chat_id, message_text)
            
            # نمایش لیست کامل اعضا
            members_text = get_complete_members_list(chat_id)
            send_message(chat_id, members_text)
        else:
            send_message(chat_id, "❌ دستور /عضو فقط در گروه قابل استفاده است.")
    
    elif is_private and (is_user_admin_role or is_user_teacher):
        # در خصوصی و مدیر یا مربی مجاز - منوی مدیریت
        if text == "منوی اصلی":
            if is_user_admin_role:
                welcome_text = f"""🏠 **منوی اصلی مدیر**

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                
                send_message(chat_id, welcome_text, get_admin_main_menu())
            else:
                welcome_text = f"""🏠 **منوی اصلی مربی**

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                
                send_message(chat_id, welcome_text, get_teacher_main_menu(user_id))
        
        elif text == "شروع":
            if is_user_admin_role:
                welcome_text = f"""🎯 **بات حضور و غیاب - مدیر**

سلام مدیر عزیز! 👋
به پنل مدیریت حضور و غیاب خوش آمدید.

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                
                send_message(chat_id, welcome