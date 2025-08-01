import requests
import jdatetime
from datetime import datetime
from config import BASE_URL, AUTHORIZED_USER_IDS
#  گروه اضافه شد . بعدی 
class AttendanceModule:
    def __init__(self):
        # لیست کاربران ثابت (برای تست)
        self.users = [f"کاربر{i+1}" for i in range(10)]  # کاربر1 تا کاربر10
        self.attendance_data = {}  # داده‌های حضور و غیاب
        self.user_states = {}  # وضعیت کاربران
        self.status_icons = {
            "حاضر": "✅",
            "حضور با تاخیر": "⏰",
            "غایب": "❌",
            "غیبت(موجه)": "📄",
            "در انتظار": "⏳"
        }
        print(f"لیست کاربران در __init__: {self.users}")  # لاگ برای دیباگ

    def send_message(self, chat_id, text, reply_markup=None):
        """ارسال پیام به کاربر"""
        url = f"{BASE_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "reply_markup": reply_markup, "parse_mode": "Markdown"}
        try:
            response = requests.post(url, json=payload)
            print(f"send_message: {response.status_code}, {response.json()}")  # لاگ
            return response.status_code == 200
        except Exception as e:
            print(f"خطا در send_message: {e}")
            return False

    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        """ویرایش پیام موجود"""
        url = f"{BASE_URL}/editMessageText"
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "reply_markup": reply_markup, "parse_mode": "Markdown"}
        try:
            response = requests.post(url, json=payload)
            print(f"edit_message: {response.status_code}, {response.json()}")  # لاگ
            return response.status_code == 200
        except Exception as e:
            print(f"خطا در edit_message: {e}")
            return False

    def answer_callback_query(self, callback_query_id, text=None):
        """پاسخ به callback"""
        url = f"{BASE_URL}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        try:
            response = requests.post(url, json=payload)
            print(f"answer_callback_query: {response.status_code}, {response.json()}")  # لاگ
        except Exception as e:
            print(f"خطا در answer_callback_query: {e}")

    def is_user_authorized(self, user_id):
        """بررسی مجوز کاربر"""
        authorized = user_id in AUTHORIZED_USER_IDS
        print(f"چک کردن دسترسی کاربر {user_id}: {authorized}")  # لاگ
        return authorized

    def get_persian_date(self):
        """تبدیل تاریخ به فارسی"""
        now = jdatetime.datetime.now()
        weekdays = {0: "شنبه", 1: "یکشنبه", 2: "دوشنبه", 3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنج‌شنبه", 6: "جمعه"}
        months = {1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر", 5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان", 9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"}
        return f"{weekdays[now.weekday()]} {now.day} {months[now.month]}"

    def get_attendance_list(self):
        """نمایش لیست حضور و غیاب"""
        if not self.users:
            print("خطا: لیست کاربران خالی است!")  # لاگ
            return "❌ لیست کاربران خالی است!"
        current_time = f"{self.get_persian_date()} - {datetime.now().strftime('%H:%M')}"
        text = f"📊 **لیست حضور و غیاب**\n🕐 آخرین بروزرسانی: {current_time}\n\n"
        for i, user in enumerate(self.users, 1):
            status = self.attendance_data.get(user, "در انتظار")
            icon = self.status_icons.get(status, "⏳")
            text += f"{i:2d}. {icon} {user} - {status}\n"
        present = sum(1 for status in self.attendance_data.values() if status == "حاضر")
        late = sum(1 for status in self.attendance_data.values() if status == "حضور با تاخیر")
        absent = sum(1 for status in self.attendance_data.values() if status == "غایب")
        justified = sum(1 for status in self.attendance_data.values() if status == "غیبت(موجه)")
        text += f"\n📈 **آمار:**\n"
        text += f"✅ حاضر: {present} | ⏰ تاخیر: {late}\n"
        text += f"❌ غایب: {absent} | 📄 موجه: {justified}"
        print(f"لیست حضور و غیاب: {text}")  # لاگ
        return text

    def get_main_menu(self):
        """منوی اصلی"""
        return {
            "inline_keyboard": [
                [{"text": "📊 مشاهده لیست حضور و غیاب", "callback_data": "view_attendance"}],
                [{"text": "✏️ ثبت حضور و غیاب سریع", "callback_data": "quick_attendance"}],
                [{"text": "🔄 پاک کردن همه داده‌ها", "callback_data": "clear_all"}],
                [{"text": "📈 آمار کلی", "callback_data": "statistics"}]
            ]
        }

    def get_quick_attendance_keyboard(self):
        """کیبورد ثبت سریع حضور و غیاب"""
        if not self.users:
            print("خطا: لیست کاربران برای کیبورد خالی است!")  # لاگ
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
        print(f"کیبورد ثبت سریع: {keyboard}")  # لاگ
        return {"inline_keyboard": keyboard}

    def get_status_keyboard(self, user_index):
        """کیبورد انتخاب وضعیت"""
        user = self.users[user_index]
        return {
            "inline_keyboard": [
                [{"text": "✅ حاضر", "callback_data": f"set_status_{user_index}_حاضر"}, {"text": "⏰ حضور با تاخیر", "callback_data": f"set_status_{user_index}_حضور با تاخیر"}],
                [{"text": "❌ غایب", "callback_data": f"set_status_{user_index}_غایب"}, {"text": "📄 غیبت(موجه)", "callback_data": f"set_status_{user_index}_غیبت(موجه)"}],
                [{"text": "🔙 برگشت", "callback_data": "quick_attendance"}]
            ]
        }

    def handle_message(self, message):
        """پردازش پیام‌های متنی"""
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        print(f"پیام دریافتی: user_id={user_id}, text={text}")  # لاگ

        if not self.is_user_authorized(user_id):
            print(f"🤖 id❌ {chat_id}.")
            self.send_message(chat_id, "❌ شما اجازه دسترسی به این بات را ندارید!")
            return

        if text in ["/start", "شروع"]:
            print(f"🤖 start id✅ {chat_id}.")
            welcome_text = f"""🎯 **بات حضور و غیاب**

سلام مربی عزیز! 👋
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
            self.send_message(chat_id, welcome_text, self.get_main_menu())
        elif text == "خروج":
            self.send_message(chat_id, "👋 با تشکر از استفاده شما از بات حضور و غیاب. موفق باشید! 🌟")

    def handle_callback(self, callback):
        """پردازش درخواست‌های callback"""
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        user_id = callback["from"]["id"]
        data = callback["data"]
        callback_query_id = callback["id"]
        print(f"Callback دریافتی: user_id={user_id}, data={data}")  # لاگ

        if not self.is_user_authorized(user_id):
            self.answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
            return

        if data == "main_menu":
            self.edit_message(chat_id, message_id, "🏠 **منوی اصلی**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", self.get_main_menu())
            self.answer_callback_query(callback_query_id)
        elif data == "view_attendance":
            text = self.get_attendance_list()
            keyboard = {"inline_keyboard": [[{"text": "🔄 بروزرسانی", "callback_data": "view_attendance"}], [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]]}
            self.edit_message(chat_id, message_id, text, keyboard)
            self.answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
        elif data == "quick_attendance":
            self.edit_message(chat_id, message_id, "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:", self.get_quick_attendance_keyboard())
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
            self.attendance_data[user] = status
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
            self.edit_message(chat_id, message_id, stats_text, {"inline_keyboard": [[{"text": "🔄 بروزرسانی آمار", "callback_data": "statistics"}], [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]]})
            self.answer_callback_query(callback_query_id, "📊 آمار بروزرسانی شد")