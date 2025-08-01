import requests
import jdatetime
from datetime import datetime
from config import BASE_URL, AUTHORIZED_USER_IDS, ADMIN_USER_ID

class AttendanceModule:
    def __init__(self):
        # مقداردهی اولیه لیست کاربران
        self.users = []  # به‌جای لیست تستی، بعداً از گروه پر می‌شه
        self.attendance_data = {}  # دیکشنری برای ذخیره وضعیت حضور و غیاب کاربران
        self.group_attendance = {}  # دیکشنری برای ذخیره وضعیت حضور و غیاب به تفکیک گروه‌ها
        self.current_group_id = None  # گروه فعلی که کاربر در حال مشاهده یا ویرایش آن است
        self.user_states = {}
        self.status_icons = {
            "حاضر": "✅",
            "حضور با تاخیر": "⏰",
            "غایب": "❌",
            "غیبت(موجه)": "📄",
            "در انتظار": "⏳"
        }
        print("AttendanceModule initialized with group-specific attendance tracking")

    def send_message(self, chat_id, text, reply_markup=None):
        # ارسال پیام به کاربر
        url = f"{BASE_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "reply_markup": reply_markup, "parse_mode": "Markdown"}
        try:
            response = requests.post(url, json=payload)
            print(f"send_message: {response.status_code}, {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error in send_message: {e}")
            return False

    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        # ویرایش پیام موجود
        url = f"{BASE_URL}/editMessageText"
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "reply_markup": reply_markup, "parse_mode": "Markdown"}
        try:
            response = requests.post(url, json=payload)
            print(f"edit_message: {response.status_code}, {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error in edit_message: {e}")
            return False

    def answer_callback_query(self, callback_query_id, text=None):
        # پاسخ به callback
        url = f"{BASE_URL}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        try:
            response = requests.post(url, json=payload)
            print(f"answer_callback_query: {response.status_code}, {response.json()}")
        except Exception as e:
            print(f"Error in answer_callback_query: {e}")

    def is_user_authorized(self, user_id):
        # بررسی مجوز کاربر
        if isinstance(user_id, str):
            try:
                user_id = int(user_id)
            except ValueError:
                return False
        authorized = user_id in AUTHORIZED_USER_IDS or user_id == ADMIN_USER_ID
        print(f"Checking user access {user_id}: {authorized}")
        return authorized

    def get_persian_date(self):
        # تبدیل تاریخ به فارسی
        now = jdatetime.datetime.now()
        weekdays = {0: "شنبه", 1: "یکشنبه", 2: "دوشنبه", 3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنج‌شنبه", 6: "جمعه"}
        months = {1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر", 5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان", 9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"}
        return f"{weekdays[now.weekday()]} {now.day} {months[now.month]}"

    def get_attendance_list(self, group_id=None):
        # نمایش لیست حضور و غیاب
        if not self.users:
            print("Error: User list is empty!")
            return "❌ لیست کاربران خالی است!"
        
        # دریافت تاریخ و زمان فعلی
        current_time = f"{self.get_persian_date()} - {datetime.now().strftime('%H:%M')}"
        
        # تنظیم متن گروه
        group_text = f" گروه {group_id}" if group_id else ""
        
        # ساخت عنوان لیست
        text = f"📊 **لیست حضور و غیاب{group_text}**\n🕐 آخرین بروزرسانی: {current_time}\n\n"
        
        # استفاده از دیکشنری مخصوص گروه اگر گروه مشخص شده باشد
        if group_id:
            # اگر این گروه قبلاً در دیکشنری نباشد، آن را اضافه می‌کنیم
            if group_id not in self.group_attendance:
                self.group_attendance[group_id] = {}
            
            # نمایش وضعیت حضور و غیاب کاربران در این گروه
            for i, user in enumerate(self.users, 1):
                # دریافت وضعیت کاربر در این گروه
                status = self.group_attendance[group_id].get(user, "در انتظار")
                icon = self.status_icons.get(status, "⏳")
                
                # دریافت اطلاعات کاربر (نام و نام خانوادگی)
                user_name = user  # مقدار پیش‌فرض
                # اینجا می‌توان کد دریافت نام کاربر را اضافه کرد
                
                text += f"{i:2d}. {icon} {user_name} - {status}\n"
            
            # محاسبه آمار حضور و غیاب برای این گروه
            user_statuses = [self.group_attendance[group_id].get(user, "در انتظار") for user in self.users]
        else:
            # نمایش وضعیت حضور و غیاب کلی کاربران
            for i, user in enumerate(self.users, 1):
                status = self.attendance_data.get(user, "در انتظار")
                icon = self.status_icons.get(status, "⏳")
                text += f"{i:2d}. {icon} {user} - {status}\n"
            
            # محاسبه آمار حضور و غیاب کلی
            user_statuses = [self.attendance_data.get(user, "در انتظار") for user in self.users]
        
        # محاسبه آمار بر اساس وضعیت‌های کاربران
        present = sum(1 for status in user_statuses if status == "حاضر")
        late = sum(1 for status in user_statuses if status == "حضور با تاخیر")
        absent = sum(1 for status in user_statuses if status == "غایب")
        justified = sum(1 for status in user_statuses if status == "غیبت(موجه)")
        waiting = sum(1 for status in user_statuses if status == "در انتظار")
        
        # اضافه کردن آمار به متن
        text += f"\n📈 **آمار:**\n"
        text += f"✅ حاضر: {present} | ⏰ تاخیر: {late}\n"
        text += f"❌ غایب: {absent} | 📄 موجه: {justified}\n"
        text += f"⏳ در انتظار: {waiting} | 👥 کل: {len(self.users)}"
        
        # ثبت در لاگ
        print(f"Attendance list for group {group_id}: {len(self.users)} users")
        return text

    def get_main_menu(self, user_id):
        # منوی اصلی (فقط برای مدیر و مربی‌ها)
        if not self.is_user_authorized(user_id):
            return {"inline_keyboard": [[{"text": "ℹ️ راهنما", "callback_data": "help"}]]}
        return {
            "inline_keyboard": [
                [{"text": "📊 مشاهده لیست حضور و غیاب", "callback_data": "view_attendance"}],
                [{"text": "✏️ ثبت حضور و غیاب سریع", "callback_data": "quick_attendance"}],
                [{"text": "🔄 پاک کردن همه داده‌ها", "callback_data": "clear_all"}],
                [{"text": "📈 آمار کلی", "callback_data": "statistics"}],
                [{"text": "👥 مدیریت گروه‌ها", "callback_data": "group_menu"}]
            ]
        }

    def get_quick_attendance_keyboard(self):
        # کیبورد ثبت سریع حضور و غیاب
        if not self.users:
            print("Error: User list is empty for keyboard!")
            return {"inline_keyboard": [[{"text": "❌ لیست کاربران خالی است", "callback_data": "main_menu"}]]}
        keyboard = []
        for i, user in enumerate(self.users):
            status = self.attendance_data.get(user, "در انتظار")
            icon = self.status_icons.get(status, "⏳")
            keyboard.append([{"text": f"{icon} {user}", "callback_data": f"select_user_{i}"}])
        keyboard.extend([
            [{"text": "✅ همه حاضر", "callback_data": "all_present"}, {"text": "❌ همه غایب", "callback_data": "all_absent"}],
            [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]
        ])
        print(f"Quick attendance keyboard: {keyboard}")
        return {"inline_keyboard": keyboard}

    def get_status_keyboard(self, user_index):
        # کیبورد انتخاب وضعیت
        user = self.users[user_index]
        return {
            "inline_keyboard": [
                [{"text": "✅ حاضر", "callback_data": f"set_status_{user_index}_حاضر"}, {"text": "⏰ حضور با تاخیر", "callback_data": f"set_status_{user_index}_حضور با تاخیر"}],
                [{"text": "❌ غایب", "callback_data": f"set_status_{user_index}_غایب"}, {"text": "📄 غیبت(موجه)", "callback_data": f"set_status_{user_index}_غیبت(موجه)"}],
                [{"text": "🔙 برگشت", "callback_data": "quick_attendance"}]
            ]
        }

    def handle_message(self, message):
        # پردازش پیام‌های متنی
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        print(f"Received message: user_id={user_id}, text={text}")

        if not self.is_user_authorized(user_id) and text != "/group":
            print(f"🤖 id❌ {chat_id}.")
            self.send_message(chat_id, "❌ شما اجازه دسترسی به این بات را ندارید!")
            return

        if text in ["/start", "شروع"]:
            print(f"🤖 start id✅ {chat_id}.")
            welcome_text = f"""🎯 **بات حضور و غیاب**

سلام {'مدیر' if user_id == ADMIN_USER_ID else 'مربی'} عزیز! 👋
به بات حضور و غیاب خوش آمدید.

🕐 زمان: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد کاربران: {len(self.users)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
            keyboard = {"keyboard": [[{"text": "شروع"}, {"text": "خروج"}, {"text": "منوی اصلی"}]], "resize_keyboard": True}
            self.send_message(chat_id, welcome_text, keyboard)
        elif text == "منوی اصلی":
            welcome_text = f"""🏠 **منوی اصلی**

🕐 زمان: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد کاربران: {len(self.users)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
            self.send_message(chat_id, welcome_text, self.get_main_menu(user_id))
        elif text == "خروج":
            self.send_message(chat_id, "👋 با تشکر از استفاده شما از بات حضور و غیاب. موفق باشید! 🌟")
        elif text == "/group":
            self.send_message(chat_id, "📋 **مدیریت گروه‌ها**\nلطفاً گروه یا مربی را انتخاب کنید:", {"inline_keyboard": [[{"text": "👥 گروه‌ها", "callback_data": "group_menu"}]]})

    def handle_callback(self, callback):
        # پردازش درخواست‌های callback
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        user_id = callback["from"]["id"]
        data = callback["data"]
        callback_query_id = callback["id"]
        print(f"Received callback: user_id={user_id}, data={data}")

        if not self.is_user_authorized(user_id):
            self.answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
            return

        if data == "main_menu":
            # دریافت اطلاعات کاربر
            user_info = self.get_user_info(user_id)
            first_name = user_info.get("first_name", "کاربر")
            
            # پاک کردن گروه فعلی
            self.current_group_id = None
            
            # بررسی نقش کاربر
            is_admin = self.is_user_admin(user_id)
            is_teacher = self.is_user_teacher(user_id)
            
            # پیام خوش‌آمدگویی شخصی‌سازی شده
            if is_admin:
                welcome_text = f"سلام مدیر {first_name}\n{self.get_persian_date()}\nبه سیستم مدیریت حضور و غیاب خوش آمدید!"
            elif is_teacher:
                welcome_text = f"سلام مربی {first_name}\n{self.get_persian_date()}\nبه سیستم مدیریت حضور و غیاب خوش آمدید!"
            else:
                welcome_text = f"سلام {first_name}\n{self.get_persian_date()}\nبه سیستم مدیریت حضور و غیاب خوش آمدید!"
            
            # نمایش کیبورد مناسب بر اساس نقش کاربر
            keyboard = self.get_main_menu(user_id)
            self.edit_message(chat_id, message_id, welcome_text, keyboard)
            self.answer_callback_query(callback_query_id, "به منوی اصلی بازگشتید")
        elif data == "view_attendance":
            # پاک کردن گروه فعلی چون این حالت برای مشاهده کلی است
            self.current_group_id = None
            
            text = self.get_attendance_list()
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": "view_attendance"}],
                [{"text": "✏️ ثبت سریع", "callback_data": "quick_attendance"}],
                [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
            ]}
            self.edit_message(chat_id, message_id, text, keyboard)
            self.answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
        elif data == "quick_attendance":
            # پاک کردن گروه فعلی چون این حالت برای ثبت کلی است
            self.current_group_id = None
            
            # دریافت تاریخ شمسی
            persian_date = self.get_persian_date()
            
            self.edit_message(chat_id, message_id, f"✏️ **ثبت سریع حضور و غیاب**\n{persian_date}\nروی نام هر قرآن‌آموز کلیک کنید:", self.get_quick_attendance_keyboard())
            self.answer_callback_query(callback_query_id)
        elif data.startswith("select_user_"):
            user_index = int(data.split("_")[-1])
            user = self.users[user_index]
            current_status = self.attendance_data.get(user, "در انتظار")
            self.edit_message(chat_id, message_id, f"👤 **{user}**\nوضعیت فعلی: {current_status}\n\nوضعیت جدید را انتخاب کنید:", self.get_status_keyboard(user_index))
            self.answer_callback_query(callback_query_id, f"انتخاب {user}")
        elif data.startswith("set_status_"):
            parts = data.split("_")
            user_index = int(parts[2])
            status = parts[3]
            user = self.users[user_index]
            
            # ذخیره وضعیت در دیکشنری کلی
            self.attendance_data[user] = status
            
            # اگر گروه فعلی مشخص شده باشد، وضعیت را در دیکشنری مخصوص آن گروه هم ذخیره می‌کنیم
            if self.current_group_id:
                # اطمینان از وجود کلید گروه در دیکشنری
                if self.current_group_id not in self.group_attendance:
                    self.group_attendance[self.current_group_id] = {}
                
                # ذخیره وضعیت کاربر در گروه فعلی
                self.group_attendance[self.current_group_id][user] = status
                print(f"Set status for user {user} in group {self.current_group_id} to {status}")
            self.edit_message(chat_id, message_id, "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:", self.get_quick_attendance_keyboard())
            self.answer_callback_query(callback_query_id, f"✅ {user} - {status}")
        elif data == "all_present":
            for user in self.users:
                self.attendance_data[user] = "حاضر"
            self.edit_message(chat_id, message_id, "✅ **همه کاربران حاضر علامت گذاری شدند**", {"inline_keyboard": [[{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}], [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]]})
            self.answer_callback_query(callback_query_id, "✅ همه حاضر شدند")
        elif data == "all_absent":
            for user in self.users:
                self.attendance_data[user] = "غایب"
            self.edit_message(chat_id, message_id, "❌ **همه کاربران غایب علامت گذاری شدند**", {"inline_keyboard": [[{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}], [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]]})
            self.answer_callback_query(callback_query_id, "❌ همه غایب شدند")
        elif data == "clear_all":
            self.attendance_data.clear()
            self.edit_message(chat_id, message_id, "🗑️ **همه داده‌ها پاک شدند**", {"inline_keyboard": [[{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]]})
            self.answer_callback_query(callback_query_id, "🗑️ داده‌ها پاک شدند")
        elif data == "statistics":
            total = len(self.users)
            present = sum(1 for status in self.attendance_data.values() if status == "حاضر")
            late = sum(1 for status in self.attendance_data.values() if status == "حضور با تاخیر")
            absent = sum(1 for status in self.attendance_data.values() if status == "غایب")
            justified = sum(1 for status in self.attendance_data.values() if status == "غیبت(موجه)")
            pending = total - len(self.attendance_data)
            stats_text = f"""📈 **آمار کلی حضور و غیاب**

👥 کل کاربران: {total}
✅ حاضر: {present} ({present/total*100:.1f}%)
⏰ حضور با تاخیر: {late} ({late/total*100:.1f}%)
❌ غایب: {absent} ({absent/total*100:.1f}%)
📄 غیبت(موجه): {justified} ({justified/total*100:.1f}%)
⏳ در انتظار: {pending} ({pending/total*100:.1f}%)

🕐 زمان آخرین بروزرسانی: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}"""
            self.edit_message(chat_id, message_id, stats_text, {"inline_keyboard": [[{"text": "🔄 بروزرسانی آمار", "callback_data": "statistics"}], [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]]})
            self.answer_callback_query(callback_query_id, "📊 آمار بروزرسانی شد")