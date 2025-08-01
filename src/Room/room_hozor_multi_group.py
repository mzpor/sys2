import requests
import json
import time
from datetime import datetime
import jdatetime

# تنظیمات بات
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

# مدیران (دسترسی کامل به همه گروه‌ها)
AUTHORIZED_ADMIN_IDS = [
    574330749, #محمد زارع ۲
    1114227010, # محمد  ۱
    1775811194, #محرابی 
]

# مربیان و گروه‌هایشان
AUTHORIZED_TEACHER_IDS = {

     574330749, #محمد زارع ۲
  #  111111: {"name": "مربی علی", "group_id": -1001234567890, "group_name": "گروه ریاضی"},
  #  222222: {"name": "مربی فاطمه", "group_id": -1009876543210, "group_name": "گروه فیزیک"},
  #  333333: {"name": "مربی احمد", "group_id": -1005556667777, "group_name": "گروه شیمی"}
}

# لیست کاربران هر گروه
group_members = {}  # {group_id: [users]}
attendance_data = {}  # {group_id: {user_name: status}}

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
    return user_id in AUTHORIZED_ADMIN_IDS

# بررسی مجوز مربی
def is_teacher(user_id):
    return user_id in AUTHORIZED_TEACHER_IDS

# دریافت گروه مربی
def get_teacher_group(user_id):
    if user_id in AUTHORIZED_TEACHER_IDS:
        return AUTHORIZED_TEACHER_IDS[user_id]["group_id"]
    return None

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

# بررسی اینکه آیا کاربر ادمین است
def is_user_admin(chat_id, user_id):
    url = f"{BASE_URL}/getChatMember"
    params = {"chat_id": chat_id, "user_id": user_id}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            result = response.json().get("result", {})
            status = result.get("status", "")
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
    
    # اطمینان از وجود گروه در لیست
    if chat_id not in group_members:
        group_members[chat_id] = []
    
    # بررسی اینکه آیا کاربر قبلاً در لیست است
    for existing_user in group_members[chat_id]:
        if existing_user.get("id") == user_id:
            return False, "این کاربر قبلاً در لیست حضور و غیاب ثبت شده است."
    
    # اضافه کردن کاربر جدید
    new_user = {
        "id": user_id,
        "name": full_name,
        "username": username,
        "added_time": datetime.now().strftime("%H:%M:%S"),
        "chat_id": chat_id
    }
    group_members[chat_id].append(new_user)
    
    return True, f"✅ {full_name} به لیست حضور و غیاب اضافه شد."

# نمایش لیست کامل کاربران غیر ادمین
def get_complete_members_list(chat_id):
    if chat_id not in group_members or not group_members[chat_id]:
        return "⚠️ هیچ عضوی در لیست حضور و غیاب ثبت نشده است."
    
    text = f"👥 **لیست کامل اعضای ثبت شده**\n\n"
    for i, user in enumerate(group_members[chat_id], 1):
        text += f"{i}. {user['name']}\n"
    text += f"\n📊 تعداد کل: {len(group_members[chat_id])} نفر"
    return text

# منوی اصلی برای مدیران
def get_admin_main_menu():
    return {
        "inline_keyboard": [
            [{"text": "👥 مدیریت مربیان", "callback_data": "manage_teachers"}],
            [{"text": "📊 آمار کلی همه گروه‌ها", "callback_data": "overall_statistics"}],
            [{"text": "🔄 پاک کردن همه داده‌ها", "callback_data": "clear_all_data"}]
        ]
    }

# منوی مربیان برای مدیر
def get_teachers_menu():
    keyboard = []
    for teacher_id, teacher_info in AUTHORIZED_TEACHER_IDS.items():
        group_name = teacher_info["group_name"]
        teacher_name = teacher_info["name"]
        keyboard.append([{"text": f"👤 {teacher_name} - {group_name}", "callback_data": f"select_teacher_{teacher_id}"}])
    
    keyboard.append([{"text": "🏠 برگشت به منوی اصلی", "callback_data": "admin_main_menu"}])
    return {"inline_keyboard": keyboard}

# منوی اصلی برای مربیان
def get_teacher_main_menu(group_id):
    group_name = "گروه نامشخص"
    for teacher_info in AUTHORIZED_TEACHER_IDS.values():
        if teacher_info["group_id"] == group_id:
            group_name = teacher_info["group_name"]
            break
    
    return {
        "inline_keyboard": [
            [{"text": f"📊 مشاهده لیست حضور و غیاب ({group_name})", "callback_data": "view_attendance"}],
            [{"text": "✏️ ثبت حضور و غیاب سریع", "callback_data": "quick_attendance"}],
            [{"text": "🔄 پاک کردن داده‌های این گروه", "callback_data": "clear_group_data"}],
            [{"text": "📈 آمار گروه", "callback_data": "group_statistics"}],
            [{"text": "👥 لیست اعضای گروه", "callback_data": "show_group_members"}]
        ]
    }

# نمایش لیست حضور و غیاب با آیکون‌های رنگی
def get_attendance_list(group_id):
    current_time = f"{get_persian_date()} - {datetime.now().strftime('%H:%M')}"
    text = f"📊 **لیست حضور و غیاب**\n🕐 آخرین بروزرسانی: {current_time}\n\n"
    
    if group_id not in group_members or not group_members[group_id]:
        text += "⚠️ هیچ عضوی در لیست حضور و غیاب ثبت نشده است.\n"
        text += "کاربران باید در گروه با دستور /عضو خود را اضافه کنند."
        return text
    
    status_icons = {
        "حاضر": "✅",
        "حضور با تاخیر": "⏰", 
        "غایب": "❌",
        "غیبت(موجه)": "📄",
        "در انتظار": "⏳"
    }
    
    for i, user in enumerate(group_members[group_id], 1):
        status = attendance_data.get(f"{group_id}_{user['name']}", "در انتظار")
        icon = status_icons.get(status, "⏳")
        text += f"{i:2d}. {icon} {user['name']} - {status}\n"
    
    # آمار سریع
    present = sum(1 for key, status in attendance_data.items() 
                  if key.startswith(f"{group_id}_") and status == "حاضر")
    late = sum(1 for key, status in attendance_data.items() 
               if key.startswith(f"{group_id}_") and status == "حضور با تاخیر")
    absent = sum(1 for key, status in attendance_data.items() 
                 if key.startswith(f"{group_id}_") and status == "غایب")
    justified = sum(1 for key, status in attendance_data.items() 
                    if key.startswith(f"{group_id}_") and status == "غیبت(موجه)")
    
    text += f"\n📈 **آمار:**\n"
    text += f"✅ حاضر: {present} | ⏰ تاخیر: {late}\n"
    text += f"❌ غایب: {absent} | 📄 موجه: {justified}"
    
    return text

# کیبورد ثبت سریع حضور و غیاب
def get_quick_attendance_keyboard(group_id):
    if group_id not in group_members or not group_members[group_id]:
        return {"inline_keyboard": [[{"text": "🏠 برگشت به منو", "callback_data": "teacher_main_menu"}]]}
    
    keyboard = []
    # دکمه‌های تک‌تک برای کاربران (هر کاربر در یک ردیف)
    for i, user in enumerate(group_members[group_id]):
        status = attendance_data.get(f"{group_id}_{user['name']}", "⏳")
        status_icon = {"حاضر": "✅", "حضور با تاخیر": "⏰", "غایب": "❌", "غیبت(موجه)": "📄"}.get(status, "⏳")
        keyboard.append([{"text": f"{status_icon} {user['name']}", "callback_data": f"select_user_{group_id}_{i}"}])
    
    # دکمه‌های کنترل
    keyboard.extend([
        [{"text": "✅ همه حاضر", "callback_data": f"all_present_{group_id}"}, 
         {"text": "❌ همه غایب", "callback_data": f"all_absent_{group_id}"}],
        [{"text": "🏠 برگشت به منو", "callback_data": "teacher_main_menu"}]
    ])
    
    return {"inline_keyboard": keyboard}

# کیبورد انتخاب وضعیت برای هر کاربر
def get_status_keyboard(group_id, user_index):
    if group_id not in group_members or user_index >= len(group_members[group_id]):
        return {"inline_keyboard": [[{"text": "🔙 برگشت", "callback_data": f"quick_attendance_{group_id}"}]]}
    
    user = group_members[group_id][user_index]
    return {
        "inline_keyboard": [
            [
                {"text": "✅ حاضر", "callback_data": f"set_status_{group_id}_{user_index}_حاضر"},
                {"text": "⏰ حضور با تاخیر", "callback_data": f"set_status_{group_id}_{user_index}_حضور با تاخیر"}
            ],
            [
                {"text": "❌ غایب", "callback_data": f"set_status_{group_id}_{user_index}_غایب"},
                {"text": "📄 غیبت(موجه)", "callback_data": f"set_status_{group_id}_{user_index}_غیبت(موجه)"}
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
    
    # بررسی مجوز
    if not is_admin(user_id) and not is_teacher(user_id):
        answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
        return
    
    # منوی اصلی مدیر
    if data == "admin_main_menu":
        edit_message(chat_id, message_id, 
                    "🏠 **منوی اصلی مدیر**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", 
                    get_admin_main_menu())
        answer_callback_query(callback_query_id)
    
    # مدیریت مربیان
    elif data == "manage_teachers":
        edit_message(chat_id, message_id, 
                    "👥 **مدیریت مربیان**\nمربی مورد نظر را انتخاب کنید:", 
                    get_teachers_menu())
        answer_callback_query(callback_query_id)
    
    # انتخاب مربی
    elif data.startswith("select_teacher_"):
        teacher_id = int(data.split("_")[-1])
        teacher_info = AUTHORIZED_TEACHER_IDS[teacher_id]
        group_id = teacher_info["group_id"]
        group_name = teacher_info["group_name"]
        
        # نمایش حضور و غیاب گروه مربی
        text = get_attendance_list(group_id)
        keyboard = {"inline_keyboard": [
            [{"text": "🔄 بروزرسانی", "callback_data": f"view_teacher_group_{teacher_id}"}],
            [{"text": "👥 مدیریت مربیان", "callback_data": "manage_teachers"}],
            [{"text": "🏠 منوی اصلی", "callback_data": "admin_main_menu"}]
        ]}
        edit_message(chat_id, message_id, text, keyboard)
        answer_callback_query(callback_query_id, f"✅ گروه {group_name}")
    
    # مشاهده گروه مربی
    elif data.startswith("view_teacher_group_"):
        teacher_id = int(data.split("_")[-1])
        teacher_info = AUTHORIZED_TEACHER_IDS[teacher_id]
        group_id = teacher_info["group_id"]
        group_name = teacher_info["group_name"]
        
        text = get_attendance_list(group_id)
        keyboard = {"inline_keyboard": [
            [{"text": "🔄 بروزرسانی", "callback_data": f"view_teacher_group_{teacher_id}"}],
            [{"text": "👥 مدیریت مربیان", "callback_data": "manage_teachers"}],
            [{"text": "🏠 منوی اصلی", "callback_data": "admin_main_menu"}]
        ]}
        edit_message(chat_id, message_id, text, keyboard)
        answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
    
    # آمار کلی
    elif data == "overall_statistics":
        total_groups = len(AUTHORIZED_TEACHER_IDS)
        total_members = sum(len(members) for members in group_members.values())
        
        stats_text = f"""📈 **آمار کلی همه گروه‌ها**

👥 تعداد گروه‌ها: {total_groups}
👤 تعداد کل اعضا: {total_members}

📊 **آمار گروه‌ها:**\n"""
        
        for teacher_id, teacher_info in AUTHORIZED_TEACHER_IDS.items():
            group_id = teacher_info["group_id"]
            group_name = teacher_info["group_name"]
            group_members_count = len(group_members.get(group_id, []))
            
            present = sum(1 for key, status in attendance_data.items() 
                         if key.startswith(f"{group_id}_") and status == "حاضر")
            absent = sum(1 for key, status in attendance_data.items() 
                        if key.startswith(f"{group_id}_") and status == "غایب")
            
            stats_text += f"• {group_name}: {group_members_count} عضو (✅{present} ❌{absent})\n"
        
        stats_text += f"\n🕐 زمان آخرین بروزرسانی: {get_persian_date()} - {datetime.now().strftime('%H:%M')}"
        
        edit_message(chat_id, message_id, stats_text, 
                    {"inline_keyboard": [
                        [{"text": "🔄 بروزرسانی آمار", "callback_data": "overall_statistics"}],
                        [{"text": "🏠 منوی اصلی", "callback_data": "admin_main_menu"}]
                    ]})
        answer_callback_query(callback_query_id, "📊 آمار بروزرسانی شد")
    
    # پاک کردن همه داده‌ها
    elif data == "clear_all_data":
        attendance_data.clear()
        group_members.clear()
        edit_message(chat_id, message_id, 
                    "🗑️ **همه داده‌ها پاک شدند**", 
                    {"inline_keyboard": [
                        [{"text": "🏠 منوی اصلی", "callback_data": "admin_main_menu"}]
                    ]})
        answer_callback_query(callback_query_id, "🗑️ داده‌ها پاک شدند")
    
    # منوی اصلی مربی
    elif data == "teacher_main_menu":
        if is_teacher(user_id):
            group_id = get_teacher_group(user_id)
            group_name = AUTHORIZED_TEACHER_IDS[user_id]["group_name"]
            edit_message(chat_id, message_id, 
                        f"🏠 **منوی مربی - {group_name}**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", 
                        get_teacher_main_menu(group_id))
        answer_callback_query(callback_query_id)
    
    # مشاهده لیست حضور و غیاب (مربی)
    elif data == "view_attendance":
        if is_teacher(user_id):
            group_id = get_teacher_group(user_id)
            text = get_attendance_list(group_id)
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": "view_attendance"}],
                [{"text": "🏠 منوی اصلی", "callback_data": "teacher_main_menu"}]
            ]}
            edit_message(chat_id, message_id, text, keyboard)
            answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
    
    # ثبت سریع حضور و غیاب (مربی)
    elif data == "quick_attendance":
        if is_teacher(user_id):
            group_id = get_teacher_group(user_id)
            if group_id not in group_members or not group_members[group_id]:
                edit_message(chat_id, message_id, 
                            "⚠️ هیچ عضوی در لیست حضور و غیاب ثبت نشده است.\n"
                            "کاربران باید در گروه با دستور /عضو خود را اضافه کنند.", 
                            {"inline_keyboard": [[{"text": "🏠 منوی اصلی", "callback_data": "teacher_main_menu"}]]})
            else:
                edit_message(chat_id, message_id, 
                            "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:", 
                            get_quick_attendance_keyboard(group_id))
            answer_callback_query(callback_query_id)
    
    # انتخاب کاربر (مربی)
    elif data.startswith("select_user_"):
        if is_teacher(user_id):
            parts = data.split("_")
            group_id = int(parts[2])
            user_index = int(parts[3])
            
            if group_id == get_teacher_group(user_id) and group_id in group_members and user_index < len(group_members[group_id]):
                user = group_members[group_id][user_index]
                current_status = attendance_data.get(f"{group_id}_{user['name']}", "در انتظار")
                edit_message(chat_id, message_id, 
                            f"👤 **{user['name']}**\nوضعیت فعلی: {current_status}\n\nوضعیت جدید را انتخاب کنید:", 
                            get_status_keyboard(group_id, user_index))
                answer_callback_query(callback_query_id, f"انتخاب {user['name']}")
            else:
                answer_callback_query(callback_query_id, "❌ کاربر یافت نشد")
    
    # تنظیم وضعیت (مربی)
    elif data.startswith("set_status_"):
        if is_teacher(user_id):
            parts = data.split("_")
            group_id = int(parts[2])
            user_index = int(parts[3])
            status = parts[4]
            
            if group_id == get_teacher_group(user_id) and group_id in group_members and user_index < len(group_members[group_id]):
                user = group_members[group_id][user_index]
                attendance_data[f"{group_id}_{user['name']}"] = status
                
                edit_message(chat_id, message_id, 
                            "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:", 
                            get_quick_attendance_keyboard(group_id))
                answer_callback_query(callback_query_id, f"✅ {user['name']} - {status}")
            else:
                answer_callback_query(callback_query_id, "❌ کاربر یافت نشد")
    
    # همه حاضر (مربی)
    elif data.startswith("all_present_"):
        if is_teacher(user_id):
            group_id = int(data.split("_")[-1])
            if group_id == get_teacher_group(user_id) and group_id in group_members:
                for user in group_members[group_id]:
                    attendance_data[f"{group_id}_{user['name']}"] = "حاضر"
                edit_message(chat_id, message_id, 
                            "✅ **همه کاربران حاضر علامت گذاری شدند**", 
                            {"inline_keyboard": [
                                [{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}],
                                [{"text": "🏠 منوی اصلی", "callback_data": "teacher_main_menu"}]
                            ]})
                answer_callback_query(callback_query_id, "✅ همه حاضر شدند")
    
    # همه غایب (مربی)
    elif data.startswith("all_absent_"):
        if is_teacher(user_id):
            group_id = int(data.split("_")[-1])
            if group_id == get_teacher_group(user_id) and group_id in group_members:
                for user in group_members[group_id]:
                    attendance_data[f"{group_id}_{user['name']}"] = "غایب"
                edit_message(chat_id, message_id, 
                            "❌ **همه کاربران غایب علامت گذاری شدند**", 
                            {"inline_keyboard": [
                                [{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}],
                                [{"text": "🏠 منوی اصلی", "callback_data": "teacher_main_menu"}]
                            ]})
                answer_callback_query(callback_query_id, "❌ همه غایب شدند")
    
    # پاک کردن داده‌های گروه (مربی)
    elif data == "clear_group_data":
        if is_teacher(user_id):
            group_id = get_teacher_group(user_id)
            # پاک کردن فقط داده‌های این گروه
            keys_to_remove = [key for key in attendance_data.keys() if key.startswith(f"{group_id}_")]
            for key in keys_to_remove:
                del attendance_data[key]
            
            edit_message(chat_id, message_id, 
                        "🗑️ **داده‌های گروه پاک شدند**", 
                        {"inline_keyboard": [
                            [{"text": "🏠 منوی اصلی", "callback_data": "teacher_main_menu"}]
                        ]})
            answer_callback_query(callback_query_id, "🗑️ داده‌های گروه پاک شدند")
    
    # آمار گروه (مربی)
    elif data == "group_statistics":
        if is_teacher(user_id):
            group_id = get_teacher_group(user_id)
            group_name = AUTHORIZED_TEACHER_IDS[user_id]["group_name"]
            total = len(group_members.get(group_id, []))
            
            if total == 0:
                stats_text = "⚠️ هیچ عضوی در لیست حضور و غیاب ثبت نشده است."
            else:
                present = sum(1 for key, status in attendance_data.items() 
                             if key.startswith(f"{group_id}_") and status == "حاضر")
                late = sum(1 for key, status in attendance_data.items() 
                           if key.startswith(f"{group_id}_") and status == "حضور با تاخیر")
                absent = sum(1 for key, status in attendance_data.items() 
                             if key.startswith(f"{group_id}_") and status == "غایب")
                justified = sum(1 for key, status in attendance_data.items() 
                                if key.startswith(f"{group_id}_") and status == "غیبت(موجه)")
                pending = total - len([key for key in attendance_data.keys() if key.startswith(f"{group_id}_")])
                
                stats_text = f"""📈 **آمار گروه {group_name}**

👥 کل کاربران: {total}
✅ حاضر: {present} ({present/total*100:.1f}%)
⏰ حضور با تاخیر: {late} ({late/total*100:.1f}%)

❌ غایب: {absent} ({absent/total*100:.1f}%)
📄 غیبت(موجه): {justified} ({justified/total*100:.1f}%)
⏳ در انتظار: {pending} ({pending/total*100:.1f}%)

🕐 زمان آخرین بروزرسانی: {get_persian_date()} - {datetime.now().strftime("%H:%M")}"""
            
            edit_message(chat_id, message_id, stats_text, 
                        {"inline_keyboard": [
                            [{"text": "🔄 بروزرسانی آمار", "callback_data": "group_statistics"}],
                            [{"text": "🏠 منوی اصلی", "callback_data": "teacher_main_menu"}]
                        ]})
            answer_callback_query(callback_query_id, "📊 آمار بروزرسانی شد")
    
    # نمایش لیست اعضای گروه (مربی)
    elif data == "show_group_members":
        if is_teacher(user_id):
            group_id = get_teacher_group(user_id)
            group_name = AUTHORIZED_TEACHER_IDS[user_id]["group_name"]
            
            if group_id not in group_members or not group_members[group_id]:
                members_text = "⚠️ هیچ عضوی در لیست حضور و غیاب ثبت نشده است."
            else:
                members_text = f"👥 **لیست اعضای گروه {group_name}**\n\n"
                for i, user in enumerate(group_members[group_id], 1):
                    members_text += f"{i}. {user['name']}\n"
                members_text += f"\n📊 تعداد کل: {len(group_members[group_id])} نفر"
            
            edit_message(chat_id, message_id, members_text, 
                        {"inline_keyboard": [
                            [{"text": "🔄 بروزرسانی", "callback_data": "show_group_members"}],
                            [{"text": "🏠 منوی اصلی", "callback_data": "teacher_main_menu"}]
                        ]})
            answer_callback_query(callback_query_id, "👥 لیست اعضا")

# پردازش پیام‌های متنی
def handle_message(message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")
    chat_type = message["chat"].get("type", "")
    
    # بررسی نوع چت
    is_private = chat_type == "private"
    is_group = chat_type in ["group", "supergroup"]
    
    if text == "/start":
        print(f"🤖 start id✅ {chat_id}.")
        
        if is_private:
            # در خصوصی
            if is_admin(user_id):
                # مدیر
                welcome_text = f"""🎯 **بات حضور و غیاب - مدیر**

سلام مدیر عزیز! 👋
به پنل مدیریت حضور و غیاب خوش آمدید.

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد گروه‌ها: {len(AUTHORIZED_TEACHER_IDS)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                
                send_message(chat_id, welcome_text, get_admin_main_menu())
            
            elif is_teacher(user_id):
                # مربی
                teacher_info = AUTHORIZED_TEACHER_IDS[user_id]
                group_name = teacher_info["group_name"]
                group_id = teacher_info["group_id"]
                group_members_count = len(group_members.get(group_id, []))
                
                welcome_text = f"""🎯 **بات حضور و غیاب - مربی**

سلام مربی عزیز! 👋
به پنل مدیریت حضور و غیاب خوش آمدید.

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 گروه شما: {group_name}
👤 تعداد اعضای ثبت شده: {group_members_count}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                
                send_message(chat_id, welcome_text, get_teacher_main_menu(group_id))
            
            else:
                send_message(chat_id, "❌ شما اجازه دسترسی به این بات را ندارید!")
        
        elif is_group:
            # در گروه - برای همه
            welcome_text = f"""🎯 **بات حضور و غیاب**

سلام! 👋
به بات حضور و غیاب خوش آمدید.

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد اعضای ثبت شده: {len(group_members.get(chat_id, []))}

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
            if chat_id in group_members and group_members[chat_id]:
                members_text = get_complete_members_list(chat_id)
                send_message(chat_id, members_text)
        else:
            send_message(chat_id, "❌ دستور /عضو فقط در گروه قابل استفاده است.")
    
    elif is_private:
        # در خصوصی
        if is_admin(user_id):
            # مدیر
            if text == "منوی اصلی":
                welcome_text = f"""🏠 **منوی اصلی مدیر**

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد گروه‌ها: {len(AUTHORIZED_TEACHER_IDS)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                
                send_message(chat_id, welcome_text, get_admin_main_menu())
            
            elif text == "شروع":
                welcome_text = f"""🎯 **بات حضور و غیاب - مدیر**

سلام مدیر عزیز! 👋
به پنل مدیریت حضور و غیاب خوش آمدید.

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد گروه‌ها: {len(AUTHORIZED_TEACHER_IDS)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                
                send_message(chat_id, welcome_text, get_admin_main_menu())
        
        elif is_teacher(user_id):
            # مربی
            teacher_info = AUTHORIZED_TEACHER_IDS[user_id]
            group_name = teacher_info["group_name"]
            group_id = teacher_info["group_id"]
            group_members_count = len(group_members.get(group_id, []))
            
            if text == "منوی اصلی":
                welcome_text = f"""🏠 **منوی اصلی مربی**

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 گروه شما: {group_name}
👤 تعداد اعضای ثبت شده: {group_members_count}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                
                send_message(chat_id, welcome_text, get_teacher_main_menu(group_id))
            
            elif text == "شروع":
                welcome_text = f"""🎯 **بات حضور و غیاب - مربی**

سلام مربی عزیز! 👋
به پنل مدیریت حضور و غیاب خوش آمدید.

🕐 زمان: {get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 گروه شما: {group_name}
👤 تعداد اعضای ثبت شده: {group_members_count}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                
                send_message(chat_id, welcome_text, get_teacher_main_menu(group_id))
        
        if text == "خروج":
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
    print("🤖 بات حضور و غیاب چند گروهی شروع شد...")
    print(f"🕐 زمان شروع: {get_persian_date()} - {datetime.now().strftime('%H:%M:%S')}")
    print(f"👥 تعداد گروه‌ها: {len(AUTHORIZED_TEACHER_IDS)}")
    print(f"👤 تعداد مربیان: {len(AUTHORIZED_TEACHER_IDS)}")
    print(f"👨‍💼 تعداد مدیران: {len(AUTHORIZED_ADMIN_IDS)}")
    
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