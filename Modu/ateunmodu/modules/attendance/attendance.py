import requests
import jdatetime
from datetime import datetime
from ..config import BASE_URL, AUTHORIZED_USER_IDS, GROUPS

class AttendanceModule:
    def __init__(self):
        self.attendance_data = {}
        self.user_states = {}
        self.status_icons = {
            "حاضر": "✅",
            "حضور با تاخیر": "⏰",
            "غایب": "❌",
            "غیبت(موجه)": "📄",
            "در انتظار": "⏳"
        }
        self.groups = GROUPS
        self.users = {}  # {group_id: [user_names]}

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

    def get_group_members(self, group_id):
        """گرفتن لیست اعضای گروه"""
        try:
            response = requests.post(
                f"{BASE_URL}/getChatAdministrators",
                json={"chat_id": group_id}
            )
            admins = response.json().get("result", [])
            admin_ids = [admin["user"]["id"] for admin in admins]

            response = requests.post(
                f"{BASE_URL}/getChatMembersCount",
                json={"chat_id": group_id}
            )
            total_members = response.json().get("result", 0)

            members = []
            # برای سادگی، فقط 10 عضو اول رو می‌گیرم (API بله محدودیت داره)
            for i in range(min(total_members, 10)):
                response = requests.post(
                    f"{BASE_URL}/getChatMember",
                    json={"chat_id": group_id, "user_id": i}
                )
                if response.json().get("ok"):
                    user = response.json()["result"]["user"]
                    if user["id"] not in admin_ids:
                        members.append(user.get("first_name", f"کاربر{i+1}"))
            return members
        except Exception as e:
            print(f"خطا در گرفتن اعضای گروه: {e}")
            return []

    def update_group_users(self, group_id, teacher_id):
        """به‌روزرسانی لیست کاربران برای حضور و غیاب"""
        if any(g["teacher_id"] == teacher_id for g in self.groups.values()):
            self.users[group_id] = self.get_group_members(group_id)
            return True
        return False

    def get_attendance_list(self, group_id):
        if group_id not in self.users:
            return "❌ گروه انتخاب‌شده معتبر نیست یا کاربران به‌روز نشده‌اند."
        current_time = f"{self.get_persian_date()} - {datetime.now().strftime('%H:%M')}"
        text = f"📊 **لیست حضور و غیاب - {self.groups[group_id]['name']}**\n🕐 آخرین بروزرسانی: {current_time}\n\n"
        for i, user in enumerate(self.users[group_id], 1):
            status = self.attendance_data.get(f"{group_id}_{user}", "در انتظار")
            icon = self.status_icons.get(status, "⏳")
            text += f"{i:2d}. {icon} {user} - {status}\n"
        present = sum(1 for status in self.attendance_data.values() if status == "حاضر" and status.startswith(f"{group_id}_"))
        late = sum(1 for status in self.attendance_data.values() if status == "حضور با تاخیر" and status.startswith(f"{group_id}_"))
        absent = sum(1 for status in self.attendance_data.values() if status == "غایب" and status.startswith(f"{group_id}_"))
        justified = sum(1 for status in self.attendance_data.values() if status == "غیبت(موجه)" and status.startswith(f"{group_id}_"))
        text += f"\n📈 **آمار:**\n"
        text += f"✅ حاضر: {present} | ⏰ تاخیر: {late}\n"
        text += f"❌ غایب: {absent} | 📄 موجه: {justified}"
        return text

    def get_main_menu(self):
        return {
            "inline_keyboard": [
                [{"text": "📊 مشاهده لیست حضور و غیاب", "callback_data": "view_attendance"}],
                [{"text": "✏️ ثبت حضور و غیاب سریع", "callback_data": "quick_attendance"}],
                [{"text": "🔄 به‌روزرسانی لیست گروه", "callback_data": "update_group"}],
                [{"text": "📈 آمار کلی", "callback_data": "statistics"}]
            ]
        }

    def get_quick_attendance_keyboard(self, group_id):
        if group_id not in self.users:
            return {"inline_keyboard": [[{"text": "🔄 به‌روزرسانی لیست گروه", "callback_data": "update_group"}]]}
        keyboard = []
        for i, user in enumerate(self.users[group_id]):
            status = self.attendance_data.get(f"{group_id}_{user}", "در انتظار")
            icon = self.status_icons.get(status, "⏳")
            keyboard.append([{"text": f"{icon} {user}", "callback_data": f"select_user_{group_id}_{i}"}])
        keyboard.extend([
            [{"text": "✅ همه حاضر", "callback_data": f"all_present_{group_id}"}, {"text": "❌ همه غایب", "callback_data": f"all_absent_{group_id}"}],
            [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]
        ])
        return {"inline_keyboard": keyboard}

    def get_status_keyboard(self, group_id, user_index):
        user = self.users[group_id][user_index]
        return {
            "inline_keyboard": [
                [{"text": "✅ حاضر", "callback_data": f"set_status_{group_id}_{user_index}_حاضر"}, {"text": "⏰ حضور با تاخیر", "callback_data": f"set_status_{group_id}_{user_index}_حضور با تاخیر"}],
                [{"text": "❌ غایب", "callback_data": f"set_status_{group_id}_{user_index}_غایب"}, {"text": "📄 غیبت(موجه)", "callback_data": f"set_status_{group_id}_{user_index}_غیبت(موجه)"}],
                [{"text": "🔙 برگشت", "callback_data": f"quick_attendance_{group_id}"}]
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
            group_id = next((gid for gid, g in self.groups.items() if g["teacher_id"] == user_id), None)
            if group_id:
                welcome_text = f"""🎯 **بات حضور و غیاب**

سلام مربی عزیز! 👋
به بات حضور و غیاب خوش آمدید.

🕐 زمان: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 گروه: {self.groups[group_id]["name"]}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                self.user_states[user_id] = {"state": "START", "group_id": group_id}
                keyboard = {"keyboard": [[{"text": "شروع"}, {"text": "خروج"}, {"text": "منوی اصلی"}]], "resize_keyboard": True}
                self.send_message(chat_id, welcome_text, keyboard)
            else:
                self.send_message(chat_id, "❌ شما به هیچ گروهی اختصاص ندارید!")
        elif text == "منوی اصلی":
            group_id = self.user_states.get(user_id, {}).get("group_id")
            if group_id:
                welcome_text = f"""🏠 **منوی اصلی**

🕐 زمان: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 گروه: {self.groups[group_id]["name"]}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
                self.send_message(chat_id, welcome_text, self.get_main_menu())
            else:
                self.send_message(chat_id, "❌ گروه شما مشخص نیست!")
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

        group_id = self.user_states.get(user_id, {}).get("group_id")
        if not group_id:
            self.send_message(chat_id, "❌ گروه شما مشخص نیست!")
            return

        if data == "main_menu":
            self.edit_message(chat_id, message_id, f"🏠 **منوی اصلی**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", self.get_main_menu())
            self.answer_callback_query(callback_query_id)
        elif data == "view_attendance":
            text = self.get_attendance_list(group_id)
            keyboard = {"inline_keyboard": [[{"text": "🔄 بروزرسانی", "callback_data": "view_attendance"}], [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]]}
            self.edit_message(chat_id, message_id, text, keyboard)
            self.answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
        elif data == "quick_attendance":
            self.edit_message(chat_id, message_id, f"✏️ **ثبت سریع حضور و غیاب - {self.groups[group_id]['name']}**\nروی نام هر کاربر کلیک کنید:", self.get_quick_attendance_keyboard(group_id))
            self.answer_callback_query(callback_query_id)
        elif data.startswith("select_user_"):
            parts = data.split("_")
            group_id = parts[2]
            user_index = int(parts[3])
            user = self.users[group_id][user_index]
            current_status = self.attendance_data.get(f"{group_id}_{user}", "در انتظار")
            self.edit_message(chat_id, message_id, f"👤 **{user}**\nوضعیت فعلی: {current_status}\n\nوضعیت جدید را انتخاب کنید:", self.get_status_keyboard(group_id, user_index))
            self.answer_callback_query(callback_query_id, f"انتخاب {user}")
        elif data.startswith("set_status_"):
            parts = data.split("_")
            group_id = parts[2]
            user_index = int(parts[3])
            status = parts[4]
            user = self.users[group_id][user_index]
            self.attendance_data[f"{group_id}_{user}"] = status
            self.edit_message(chat_id, message_id, f"✏️ **ثبت سریع حضور و غیاب - {self.groups[group_id]['name']}**\nروی نام هر کاربر کلیک کنید:", self.get_quick_attendance_keyboard(group_id))
            self.answer_callback_query(callback_query_id, f"✅ {user} - {status}")
        elif data.startswith("all_present_"):
            group_id = data.split("_")[-1]
            for user in self.users.get(group_id, []):
                self.attendance_data[f"{group_id}_{user}"] = "حاضر"
            self.edit_message(chat_id, message_id, "✅ **همه کاربران حاضر علامت گذاری شدند**", {"inline_keyboard": [[{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}], [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]]})
            self.answer_callback_query(callback_query_id, "✅ همه حاضر شدند")
        elif data.startswith("all_absent_"):
            group_id = data.split("_")[-1]
            for user in self.users.get(group_id, []):
                self.attendance_data[f"{group_id}_{user}"] = "غایب"
            self.edit_message(chat_id, message_id, "❌ **همه کاربران غایب علامت گذاری شدند**", {"inline_keyboard": [[{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}], [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]]})
            self.answer_callback_query(callback_query_id, "❌ همه غایب شدند")
        elif data == "update_group":
            if self.update_group_users(group_id, user_id):
                self.edit_message(chat_id, message_id, f"✅ **لیست کاربران گروه {self.groups[group_id]['name']} به‌روز شد**", self.get_main_menu())
                self.answer_callback_query(callback_query_id, "✅ لیست گروه به‌روز شد")
            else:
                self.edit_message(chat_id, message_id, "❌ شما به این گروه دسترسی ندارید!", self.get_main_menu())
                self.answer_callback_query(callback_query_id, "❌ دسترسی ندارید")
        elif data == "statistics":
            total = len(self.users.get(group_id, []))
            present = sum(1 for status in self.attendance_data.values() if status == "حاضر" and status.startswith(f"{group_id}_"))
            late = sum(1 for status in self.attendance_data.values() if status == "حضور با تاخیر" and status.startswith(f"{group_id}_"))
            absent = sum(1 for status in self.attendance_data.values() if status == "غایب" and status.startswith(f"{group_id}_"))
            justified = sum(1 for status in self.attendance_data.values() if status == "غیبت(موجه)" and status.startswith(f"{group_id}_"))
            pending = total - len([k for k in self.attendance_data.keys() if k.startswith(f"{group_id}_")])
            stats_text = f"""📈 **آمار کلی حضور و غیاب - {self.groups[group_id]['name']}**

👥 کل کاربران: {total}
✅ حاضر: {present} ({present/total*100:.1f}% if total else 0)
⏰ حضور با تاخیر: {late} ({late/total*100:.1f}% if total else 0)
❌ غایب: {absent} ({absent/total*100:.1f}% if total else 0)
📄 غیبت(موجه): {justified} ({justified/total*100:.1f}% if total else 0)
⏳ در انتظار: {pending} ({pending/total*100:.1f}% if total else 0)

🕐 زمان آخرین بروزرسانی: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}"""
            self.edit_message(chat_id, message_id, stats_text, {"inline_keyboard": [[{"text": "🔄 بروزرسانی آمار", "callback_data": "statistics"}], [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]]})
            self.answer_callback_query(callback_query_id, "📊 آمار بروزرسانی شد")