import requests
import jdatetime
from datetime import datetime
from config import BASE_URL, AUTHORIZED_USER_IDS

class AttendanceModule:
    def __init__(self):
        self.users = [f"کاربر{i+1}" for i in range(10)]
        self.attendance_data = {}
        self.user_states = {}
        self.status_icons = {
            "حاضر": "✅",
            "حضور با تاخیر": "⏰",
            "غایب": "❌",
            "غیبت(موجه)": "📄",
            "در انتظار": "⏳"
        }

    def send_message(self, chat_id, text, reply_markup=None):
        url = f"{BASE_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}
        response = requests.post(url, json=payload)
        return response.status_code == 200

    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        url = f"{BASE_URL}/editMessageText"
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "reply_markup": reply_markup}
        response = requests.post(url, json=payload)
        return response.status_code == 200

    def answer_callback_query(self, callback_query_id, text=None):
        url = f"{BASE_URL}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        requests.post(url, json=payload)

    def is_user_authorized(self, user_id):
        return user_id in AUTHORIZED_USER_IDS

    def get_persian_date(self):
        now = jdatetime.datetime.now()
        weekdays = {0: "شنبه", 1: "یکشنبه", 2: "دوشنبه", 3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنج‌شنبه", 6: "جمعه"}
        months = {1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر", 5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان", 9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"}
        return f"{weekdays[now.weekday()]} {now.day} {months[now.month]}"

    def get_attendance_list(self):
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
        return text

    def get_main_menu(self):
        return {
            "inline_keyboard": [
                [{"text": "📊 مشاهده لیست حضور و غیاب", "callback_data": "view_attendance"}],
                [{"text": "✏️ ثبت حضور و غیاب سریع", "callback_data": "quick_attendance"}],
                [{"text": "🔄 پاک کردن همه داده‌ها", "callback_data": "clear_all"}],
                [{"text": "📈 آمار کلی", "callback_data": "statistics"}]
            ]
        }

    def get_quick_attendance_keyboard(self):
        keyboard = []
        for i, user in enumerate(self.users):
            status = self.attendance_data.get(user, "در انتظار")
            icon = self.status_icons.get(status, "⏳")
            keyboard.append([{"text": f"{icon} {user}", "callback_data": f"select_user_{i}"}])
        keyboard.extend([
            [{"text": "✅ همه حاضر", "callback_data": "all_present"}, {"text": "❌ همه غایب", "callback_data": "all_absent"}],
            [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]
        ])
        return {"inline_keyboard": keyboard}

    def get_status_keyboard(self, user_index):
        user = self.users[user_index]
        return {
            "inline_keyboard": [
                [{"text": "✅ حاضر", "callback_data": f"set_status_{user_index}_حاضر"}, {"text": "⏰ حضور با تاخیر", "callback_data": f"set_status_{user_index}_حضور با تاخیر"}],
                [{"text": "❌ غایب", "callback_data": f"set_status_{user_index}_غایب"}, {"text": "📄 غیبت(موجه)", "callback_data": f"set_status_{user_index}_غیبت(موجه)"}],
                [{"text": "🔙 برگشت", "callback_data": "quick_attendance"}]
            ]
        }

    def handle_message(self, message):
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")

        if not self.is_user_authorized(user_id):
            print(f"🤖 id❌ {chat_id}.")
            self.send_message(chat_id, "❌ شما اجازه دسترسی به این بات را ندارید!")
            return

        if text in ["/start", "شروع"]:
            print(f"🤖 شروع id✅ {chat_id}.")
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
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        user_id = callback["from"]["id"]
        data = callback["data"]
        callback_query_id = callback["id"]

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