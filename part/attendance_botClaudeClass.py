import requests
import json
import time
from datetime import datetime
import jdatetime

class BotConfig:
    def __init__(self):
        self.BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
        self.BASE_URL = f"https://tapi.bale.ai/bot{self.BOT_TOKEN}"

        self.AUTHORIZED_ad_IDS = [
          #  574330749,  # محمد زارع ۲
            1114227010,  # محمد ۱
            1775811194,  # محرابی
             #فدوی     # 1790308237, #ایرانسل  # 2045777722 #رایتل   # رشت بری    # مردانی #مربیان      
             ]
        self.AUTHORIZED_morabbi_IDS =[
               574330749,  # محمد زارع ۲
               1790308237,  #ایرانسل  #
             #  2045777722, #رایتل       #فدوی     # 1790308237, #رایتل   # رشت بری    # مردانی #مربیان      
                 ]

class AttendanceManager:
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

    def get_persian_date(self):
        now = jdatetime.datetime.now()
        weekdays = {
            0: "شنبه", 1: "یکشنبه", 2: "دوشنبه", 3: "سه‌شنبه",
            4: "چهارشنبه", 5: "پنج‌شنبه", 6: "جمعه"
        }
        months = {
            1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
            5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
            9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
        }
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

    def get_statistics(self):
        total = len(self.users)
        present = sum(1 for status in self.attendance_data.values() if status == "حاضر")
        late = sum(1 for status in self.attendance_data.values() if status == "حضور با تاخیر")
        absent = sum(1 for status in self.attendance_data.values() if status == "غایب")
        justified = sum(1 for status in self.attendance_data.values() if status == "غیبت(موجه)")
        pending = total - len(self.attendance_data)
        
        return f"""📈 **آمار کلی حضور و غیاب**

         👥 کل کاربران: {total}
         ✅ حاضر: {present} ({present/total*100:.1f}%)
         ⏰ حضور با تاخیر: {late} ({late/total*100:.1f}%)
         ❌ غایب: {absent} ({absent/total*100:.1f}%)
         📄 غیبت(موجه): {justified} ({justified/total*100:.1f}%)
         ⏳ در انتظار: {pending} ({pending/total*100:.1f}%)

         🕐 زمان آخرین بروزرسانی: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}"""

    def clear_all(self):
        self.attendance_data.clear()

class TelegramBot:
    def __init__(self, config, attendance_manager):
        self.config = config
        self.attendance = attendance_manager

    def send_message(self, chat_id, text, reply_markup=None):
        url = f"{self.config.BASE_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup
        }
        response = requests.post(url, json=payload)
        return response.status_code == 200

    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        url = f"{self.config.BASE_URL}/editMessageText"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "reply_markup": reply_markup
        }
        response = requests.post(url, json=payload)
        return response.status_code == 200

    def answer_callback_query(self, callback_query_id, text=None):
        url = f"{self.config.BASE_URL}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        requests.post(url, json=payload)

    def get_updates(self, offset=None):
        url = f"{self.config.BASE_URL}/getUpdates"
        params = {"offset": offset, "timeout": 30} if offset else {"timeout": 30}
        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"خطا در دریافت آپدیت‌ها: {e}")
        return None

    def is_user_authorized(self, user_id):
        return user_id in self.config.AUTHORIZED_USER_IDS

class KeyboardManager:
    def __init__(self, attendance_manager):
        self.attendance = attendance_manager

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
        for i, user in enumerate(self.attendance.users):
            status = self.attendance.attendance_data.get(user, "⏳")
            status_icon = self.attendance.status_icons.get(status, "⏳")
            keyboard.append([{"text": f"{status_icon} {user}", "callback_data": f"select_user_{i}"}])
        
        keyboard.extend([
            [{"text": "✅ همه حاضر", "callback_data": "all_present"},
             {"text": "❌ همه غایب", "callback_data": "all_absent"}],
            [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]
        ])
        return {"inline_keyboard": keyboard}

    def get_status_keyboard(self, user_index):
        user = self.attendance.users[user_index]
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

class UpdateHandler:
    def __init__(self, bot, keyboard_manager, attendance_manager):
        self.bot = bot
        self.keyboard = keyboard_manager
        self.attendance = attendance_manager

    def handle_callback_query(self, callback):
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        user_id = callback["from"]["id"]
        data = callback["data"]
        callback_query_id = callback["id"]

        if not self.bot.is_user_authorized(user_id):
            self.bot.answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
            return

        if data == "main_menu":
            self.bot.edit_message(chat_id, message_id,
                                "🏠 **منوی اصلی**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                                self.keyboard.get_main_menu())
            self.bot.answer_callback_query(callback_query_id)

        elif data == "view_attendance":
            text = self.attendance.get_attendance_list()
            keyboard = {"inline_keyboard": [[{"text": "🔄 بروزرسانی", "callback_data": "view_attendance"}],
                                        [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]]}
            self.bot.edit_message(chat_id, message_id, text, keyboard)
            self.bot.answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")

        elif data == "quick_attendance":
            self.bot.edit_message(chat_id, message_id,
                                "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:",
                                self.keyboard.get_quick_attendance_keyboard())
            self.bot.answer_callback_query(callback_query_id)

        elif data.startswith("select_user_"):
            user_index = int(data.split("_")[-1])
            user = self.attendance.users[user_index]
            current_status = self.attendance.attendance_data.get(user, "در انتظار")
            self.bot.edit_message(chat_id, message_id,
                                f"👤 **{user}**\nوضعیت فعلی: {current_status}\n\nوضعیت جدید را انتخاب کنید:",
                                self.keyboard.get_status_keyboard(user_index))
            self.bot.answer_callback_query(callback_query_id, f"انتخاب {user}")

        elif data.startswith("set_status_"):
            parts = data.split("_")
            user_index = int(parts[2])
            status = parts[3]
            user = self.attendance.users[user_index]
            self.attendance.attendance_data[user] = status
            self.bot.edit_message(chat_id, message_id,
                                "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:",
                                self.keyboard.get_quick_attendance_keyboard())
            self.bot.answer_callback_query(callback_query_id, f"✅ {user} - {status}")

        elif data == "all_present":
            for user in self.attendance.users:
                self.attendance.attendance_data[user] = "حاضر"
            self.bot.edit_message(chat_id, message_id,
                                "✅ **همه کاربران حاضر علامت گذاری شدند**",
                                {"inline_keyboard": [
                                    [{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}],
                                    [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
                                ]})
            self.bot.answer_callback_query(callback_query_id, "✅ همه حاضر شدند")

        elif data == "all_absent":
            for user in self.attendance.users:
                self.attendance.attendance_data[user] = "غایب"
            self.bot.edit_message(chat_id, message_id,
                                "❌ **همه کاربران غایب علامت گذاری شدند**",
                                {"inline_keyboard": [
                                    [{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}],
                                    [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
                                ]})
            self.bot.answer_callback_query(callback_query_id, "❌ همه غایب شدند")

        elif data == "clear_all":
            self.attendance.clear_all()
            self.bot.edit_message(chat_id, message_id,
                                "🗑️ **همه داده‌ها پاک شدند**",
                                {"inline_keyboard": [
                                    [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
                                ]})
            self.bot.answer_callback_query(callback_query_id, "🗑️ داده‌ها پاک شدند")

        elif data == "statistics":
            self.bot.edit_message(chat_id, message_id, self.attendance.get_statistics(),
                                {"inline_keyboard": [
                                    [{"text": "🔄 بروزرسانی آمار", "callback_data": "statistics"}],
                                    [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]
                                ]})
            self.bot.answer_callback_query(callback_query_id, "📊 آمار بروزرسانی شد")

    def handle_message(self, message):
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")

        if not self.bot.is_user_authorized(user_id):
            print(f"🤖 id❌ {chat_id}.")
            self.bot.send_message(chat_id, "❌ شما اجازه دسترسی به این بات را ندارید!")
            return

        welcome_text = f"""🎯 **بات حضور و غیاب**

                   سلام مربی عزیز! 👋
                   به بات حضور و غیاب خوش آمدید diligently

        keyboard = {
                    "keyboard": [
                        [{"text": "شروع"}, {"text": "خروج"}, {"text": "منوی اصلی"}],
                        "resize_keyboard": True
                    ]
                }


        if text in ["/start", "شروع"]:
            print(f"🤖 شروع id✅ {chat_id}.")
            self.bot.send_message(chat_id, welcome_text, keyboard)

        elif text == "منوی اصلی":
            self.bot.send_message(chat_id, f"🏠 **منوی اصلی**\n\n🕐 زمان: {self.attendance.get_persian_date()} - {datetime.now().strftime('%H:%M')}\n👥 تعداد کاربران: {len(self.attendance.users)}\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", self.keyboard.get_main_menu())

        elif text == "خروج":
            self.bot.send_message(chat_id, "👋 با تشکر از استفاده شما از بات حضور و غیاب. موفق باشید! 🌟")

    def handle_update(self, update):
        try:
            if "message" in update:
                self.handle_message(update["message"])
            elif "callback_query" in update:
                self.handle_callback_query(update["callback_query"])
        except Exception as e:
            print(f"خطا در پردازش آپدیت: {e}")

class AttendanceBot:
    def __init__(self):
        self.config = BotConfig()
        self.attendance = AttendanceManager()
        self.bot = TelegramBot(self.config, self.attendance)
        self.keyboard = KeyboardManager(self.attendance)
        self.handler = UpdateHandler(self.bot, self.keyboard, self.attendance)

    def run(self):
        offset = 0
        print("🤖 بات حضور و غیاب شروع شد...")
        print(f"🕐 زمان شروع: {self.attendance.get_persian_date()} - {datetime.now().strftime('%H:%M:%S')}")
        
        while True:
            try:
                updates = self.bot.get_updates(offset)
                if updates and updates.get("ok") and updates.get("result"):
                    for update in updates["result"]:
                        offset = update["update_id"] + 1
                        self.handler.handle_update(update)
                else:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⛔ بات متوقف شد.")
                break
            except Exception as e:
                print(f"خطای غیرمنتظره: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = AttendanceBot()
    bot.run()