import os
import json
import re
import requests
from config import BASE_URL, DATA_FILE, TEACHERS, ADMIN_PHONES

class RegistrationModule:
    def __init__(self):
        self.user_data = self.load_data()
        self.user_states = {}

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {}
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=2)

    def send_message(self, chat_id, text, reply_markup=None):
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        requests.post(f"{BASE_URL}/sendMessage", json=payload)

    def make_keyboard(self, buttons):
        return {"keyboard": [[{"text": b} for b in row] for row in buttons], "resize_keyboard": True}

    def make_inline_keyboard(self, buttons):
        return {"inline_keyboard": buttons}

    def is_valid_national_id(self, nid):
        return bool(re.fullmatch(r"\d{10}", nid))

    def is_admin(self, user_id, phone=None):
        if str(user_id) in TEACHERS:
            return True, TEACHERS[str(user_id)]
        if phone and phone in ADMIN_PHONES:
            return True, ADMIN_PHONES[phone]
        return False, None

    def handle_message(self, message):
        chat_id = message["chat"]["id"]
        user_id = str(message["from"]["id"])
        text = message.get("text", "")
        contact = message.get("contact")

        is_admin_user, admin_role = self.is_admin(user_id)
        if is_admin_user and text in ["/start", "شروع مجدد"]:
            self.send_message(
                chat_id,
                f"_👑 {admin_role} عزیز، به پنل مدیریتی خوش آمدید!_",
                reply_markup=self.make_keyboard([["📊 آمار کاربران", "👥 مدیریت کاربران"], ["📚 مدیریت کلاس‌ها", "⚙️ تنظیمات"], ["🔙 بازگشت به حالت عادی"]])
            )
            self.user_states[user_id] = "ADMIN_PANEL"
            return

        if text in ["/start", "شروع مجدد"]:
            self.user_states[user_id] = "START"
            self.send_message(
                chat_id,
                "_🌟 خوش آمدید! به ربات ثبت‌نام آموزشگاه خوش آمدید!_",
                reply_markup=self.make_keyboard([["شروع مجدد", "معرفی آموزشگاه", "خروج"]])
            )
            if user_id not in self.user_data:
                self.user_data[user_id] = {}
                self.send_message(
                    chat_id,
                    "برای شروع ثبت‌نام روی دکمه زیر بزنید:",
                    reply_markup=self.make_inline_keyboard([[{"text": "📝 شروع ثبت‌نام", "callback_data": "start_registration"}]])
                )
            else:
                first_name = self.user_data[user_id].get("first_name", "")
                full_name = self.user_data[user_id].get("full_name", "")
                national_id = self.user_data[user_id].get("national_id", "هنوز مانده")
                phone = self.user_data[user_id].get("phone", "هنوز مانده")
                self.send_message(
                    chat_id,
                    f"_🌟 {first_name} عزیز، خوش آمدی!\nحساب کاربری شما آماده است 👇_\n*نام*: {full_name}\n*کد ملی*: {national_id}\n*تلفن*: {phone}",
                    reply_markup=self.make_inline_keyboard([
                        [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}],
                        [{"text": "📚 انتخاب کلاس", "callback_data": "choose_class"}]
                    ])
                )
            return

        if text == "معرفی آموزشگاه":
            self.send_message(
                chat_id,
                "_🏫 *معرفی آموزشگاه*\n\nآموزشگاه ما با بیش از ۱۰ سال سابقه در زمینه آموزش قرآن کریم، خدمات متنوعی ارائه می‌دهد:\n\n📚 *کلاس‌های موجود:*\n• تجوید قرآن کریم\n• صوت و لحن\n• حفظ قرآن کریم\n• تفسیر قرآن\n\n💎 *مزایای ثبت‌نام:*\n• اساتید مجرب\n• کلاس‌های آنلاین و حضوری\n• گواهی پایان دوره\n• قیمت مناسب_\n\nبرای ثبت‌نام روی دکمه زیر کلیک کنید:",
                reply_markup=self.make_inline_keyboard([[{"text": "📝 ثبت‌نام", "callback_data": "start_registration"}]])
            )
        elif text == "خروج":
            self.send_message(chat_id, "_👋 با تشکر از استفاده شما از ربات ما. موفق باشید! 🌟_")
            self.user_states[user_id] = "START"
        elif text == "برگشت به قبل":
            if user_id in self.user_data:
                if "phone" in self.user_data[user_id]:
                    self.user_data[user_id].pop("phone", None)
                    self.send_message(
                        chat_id,
                        "_لطفاً شماره تلفن خود را دوباره ارسال کنید._",
                        reply_markup={"keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]], "resize_keyboard": True}
                    )
                elif "national_id" in self.user_data[user_id]:
                    self.user_data[user_id].pop("national_id", None)
                    self.send_message(chat_id, "_لطفاً کد ملی خود را دوباره وارد کنید._")
                elif "full_name" in self.user_data[user_id]:
                    self.user_data[user_id].pop("full_name", None)
                    self.send_message(chat_id, "_لطفاً نام خود را دوباره وارد کنید._")
                self.save_data()
        elif user_id in self.user_data:
            state = self.user_data[user_id]
            if "full_name" not in state:
                self.user_data[user_id]["full_name"] = text
                self.user_data[user_id]["first_name"] = text.split()[0]
                self.save_data()
                self.send_message(
                    chat_id,
                    f"_{state['first_name']} عزیز،\nنام شما: {text}\nکد ملی: هنوز مانده\nتلفن: هنوز مانده_\n\nلطفاً کد ملی ۱۰ رقمی خود را وارد کنید.",
                    reply_markup=self.make_keyboard([["شروع مجدد", "خروج", "برگشت به قبل"]])
                )
                self.send_message(
                    chat_id,
                    "می‌خواهید نام را ویرایش کنید؟",
                    reply_markup=self.make_inline_keyboard([[{"text": "✏️ تصحیح نام", "callback_data": "edit_name"}]])
                )
            elif "national_id" not in state:
                if self.is_valid_national_id(text):
                    self.user_data[user_id]["national_id"] = text
                    self.save_data()
                    self.send_message(
                        chat_id,
                        f"_{state['first_name']} عزیز،\nنام شما: {state['full_name']}\nکد ملی: {text}\nتلفن: هنوز مانده_\n\n📱 لطفاً شماره تلفن خود را با دکمه زیر ارسال کنید.",
                        reply_markup=self.make_keyboard([["شروع مجدد", "خروج", "برگشت به قبل"]])
                    )
                    self.send_message(
                        chat_id,
                        "👇👇👇",
                        reply_markup={"keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]], "resize_keyboard": True}
                    )
                else:
                    self.send_message(chat_id, "_❌ کد ملی نامعتبر است. لطفاً ۱۰ رقم وارد کنید._")
            elif "phone" not in state and contact:
                phone_number = contact["phone_number"]
                self.user_data[user_id]["phone"] = phone_number
                self.save_data()
                is_admin_user, admin_role = self.is_admin(user_id, phone_number)
                if is_admin_user:
                    self.send_message(
                        chat_id,
                        f"_👑 {admin_role} عزیز،\nنام: {state['full_name']}\nکد ملی: {state['national_id']}\nتلفن: {phone_number}\n\nشما به عنوان {admin_role} شناسایی شدید! 🌟_",
                        reply_markup=self.make_inline_keyboard([
                            [{"text": "✅ تأیید نهایی", "callback_data": "final_confirm"}],
                            [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}],
                            [{"text": "👑 ورود به پنل مدیریتی", "callback_data": "admin_panel"}]
                        ])
                    )
                else:
                    self.send_message(
                        chat_id,
                        f"_📋 {state['first_name']} عزیز، حساب کاربری شما:\nنام: {state['full_name']}\nکد ملی: {state['national_id']}\nتلفن: {phone_number}_",
                        reply_markup=self.make_inline_keyboard([
                            [{"text": "✅ تأیید نهایی", "callback_data": "final_confirm"}],
                            [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}]
                        ])
                    )

    def handle_callback(self, callback):
        query = callback["callback_query"]
        data = query["data"]
        chat_id = query["message"]["chat"]["id"]
        user_id = str(chat_id)

        if data == "start_registration":
            self.user_data[user_id] = {}
            self.save_data()
            self.send_message(chat_id, "_لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی)._")
        elif data == "edit_name":
            self.user_data[user_id].pop("full_name", None)
            self.save_data()
            self.send_message(chat_id, "_نام جدید را وارد کنید._")
        elif data == "edit_national_id":
            self.user_data[user_id].pop("national_id", None)
            self.save_data()
            self.send_message(chat_id, "_کد ملی جدید را وارد کنید._")
        elif data == "edit_info":
            self.user_data[user_id] = {}
            self.save_data()
            self.send_message(chat_id, "_بیایید دوباره شروع کنیم. لطفاً نام و نام خانوادگی خود را وارد کنید._")
        elif data == "final_confirm":
            self.send_message(chat_id, f"🎉 {self.user_data[user_id]['first_name']} عزیز، ثبت‌نام شما با موفقیت تکمیل شد! موفق باشید!")
            self.user_states[user_id] = "DONE"
        elif data == "choose_class":
            classes = self.user_data.get("classes", [])
            if classes:
                class_text = "_📚 کلاس‌های موجود:_\n\n"
                for i, cls in enumerate(classes, 1):
                    class_text += f"*{i}. {cls['name']}*\n"
                    class_text += f"بخش: {cls['section']}\n"
                    class_text += f"قیمت: {cls['price']} تومان\n\n"
                self.send_message(chat_id, class_text)
            else:
                self.send_message(chat_id, "_📚 در حال حاضر کلاسی موجود نیست. لطفاً بعداً مراجعه کنید._")
        elif data == "admin_panel":
            is_admin_user, admin_role = self.is_admin(user_id)
            if is_admin_user:
                self.send_message(
                    chat_id,
                    f"_👑 {admin_role} عزیز، به پنل مدیریتی خوش آمدید!_",
                    reply_markup=self.make_keyboard([["📊 آمار کاربران", "👥 مدیریت کاربران"], ["📚 مدیریت کلاس‌ها", "⚙️ تنظیمات"], ["🔙 بازگشت به حالت عادی"]])
                )
                self.user_states[user_id] = "ADMIN_PANEL"
            else:
                self.send_message(chat_id, "_❌ شما دسترسی مدیریتی ندارید._")