import os
import json
import re
import logging
import requests

class RegistrationModule:
    """ماژول مدیریت ثبت‌نام کاربران"""
    
    def __init__(self, bot_token, base_url, data_file):
        """مقداردهی اولیه ماژول ثبت‌نام"""
        self.bot_token = bot_token
        self.base_url = base_url
        self.data_file = data_file
        self.user_data = self.load_data()
        
        # تعریف مدیران و مربیان
        self.teachers = {
            "574330749": "مدیر",  # همراه2
            "1790308237": "معاون",  # رایت
            "1114227010": "مربی1",  # همراه1
        }
        
        # شماره‌های تلفن مدیران
        self.admin_phones = {
            "989942878984": "مدیر",  # شماره مدیر
            "989123456789": "معاون",  # شماره معاون
        }
    
    def load_data(self):
        """بارگذاری یا ایجاد فایل داده‌ها"""
        if not os.path.exists(self.data_file):
            return {}
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_data(self):
        """ذخیره داده‌ها در فایل"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=2)
    
    def send_message(self, chat_id, text, reply_markup=None):
        """ارسال پیام همراه با کیبورد"""
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        requests.post(f"{self.base_url}/sendMessage", json=payload)
    
    def make_keyboard(self, buttons):
        """ساخت کیبورد معمولی"""
        return {"keyboard": [[{"text": b} for b in row] for row in buttons], "resize_keyboard": True}
    
    def make_inline_keyboard(self, buttons):
        """ساخت کیبورد شیشه‌ای"""
        return {"inline_keyboard": buttons}
    
    def is_valid_national_id(self, nid):
        """بررسی اعتبار کد ملی"""
        return bool(re.fullmatch(r"\d{10}", nid))
    
    def is_admin(self, user_id, phone=None):
        """بررسی مدیر بودن کاربر"""
        # بررسی از طریق chat_id
        if user_id in self.teachers:
            return True, self.teachers[user_id]
        
        # بررسی از طریق شماره تلفن
        if phone and phone in self.admin_phones:
            return True, self.admin_phones[phone]
        
        return False, None
    
    def handle_message(self, message):
        """مدیریت پیام‌های دریافتی"""
        text = message.get("text", "")
        chat_id = message["chat"]["id"]
        user_id = str(chat_id)
        contact = message.get("contact")
        
        # بررسی مدیر بودن
        is_admin_user, admin_role = self.is_admin(user_id)
        
        # مدیریت پیام‌های مدیران
        if is_admin_user:
            if text == "/start" or text == "شروع مجدد":
                self.send_message(chat_id, 
                    f"_👑 {admin_role} عزیز، به پنل مدیریتی خوش آمدید!_",
                    reply_markup=self.make_keyboard([["📊 آمار کاربران", "👥 مدیریت کاربران"], ["📚 مدیریت کلاس‌ها", "⚙️ تنظیمات"], ["🔙 بازگشت به حالت عادی"]])
                )
                return True
            elif text == "📊 آمار کاربران":
                total_users = len([u for u in self.user_data.keys() if u != "admin" and u != "classes" and u != "temp_class"])
                completed_users = len([u for u in self.user_data.keys() if u != "admin" and u != "classes" and u != "temp_class" and "phone" in self.user_data[u]])
                self.send_message(chat_id, f"_📊 آمار کاربران:_\n*کل کاربران:* {total_users}\n*تکمیل شده:* {completed_users}\n*ناقص:* {total_users - completed_users}")
                return True
            elif text == "👥 مدیریت کاربران":
                self.send_message(chat_id, "_👥 پنل مدیریت کاربران_", 
                    reply_markup=self.make_inline_keyboard([
                        [{"text": "📋 لیست کاربران", "callback_data": "list_users"}],
                        [{"text": "🔍 جستجوی کاربر", "callback_data": "search_user"}]
                    ])
                )
                return True
            elif text == "📚 مدیریت کلاس‌ها":
                self.send_message(chat_id, "_📚 پنل مدیریت کلاس‌ها_",
                    reply_markup=self.make_inline_keyboard([
                        [{"text": "➕ افزودن کلاس", "callback_data": "add_class"}],
                        [{"text": "📋 لیست کلاس‌ها", "callback_data": "list_classes"}]
                    ])
                )
                return True
            elif text == "🔙 بازگشت به حالت عادی":
                self.send_message(chat_id, "_🌟 خوش آمدید! به ربات ثبت‌نام آموزشگاه خوش آمدید!_",
                    reply_markup=self.make_keyboard([["شروع مجدد", "معرفی آموزشگاه", "خروج"]])
                )
                return True
        
        # مدیریت پیام‌های کاربران عادی
        if text == "/start" or text == "شروع مجدد":
            # همیشه دکمه‌های معمولی را نمایش بده
            self.send_message(chat_id, "_🌟 خوش آمدید! به ربات ثبت‌نام آموزشگاه خوش آمدید!_",
                reply_markup=self.make_keyboard([["شروع مجدد", "معرفی آموزشگاه", "خروج"]])
            )
            
            # بررسی وضعیت کاربر
            if user_id in self.user_data and "full_name" in self.user_data[user_id]:
                first_name = self.user_data[user_id]["first_name"]
                full_name = self.user_data[user_id]["full_name"]
                national_id = self.user_data[user_id].get("national_id", "هنوز مانده")
                phone = self.user_data[user_id].get("phone", "هنوز مانده")
                
                self.send_message(chat_id,
                    f"_🌟 {first_name} عزیز، خوش آمدی!\n"
                    f"حساب کاربری شما آماده است 👇_\n"
                    f"*نام*: {full_name}\n"
                    f"*کد ملی*: {national_id}\n"
                    f"*تلفن*: {phone}",
                    reply_markup=self.make_inline_keyboard([
                        [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}],
                        [{"text": "📚 انتخاب کلاس", "callback_data": "choose_class"}]
                    ])
                )
            else:
                self.user_data[user_id] = {}  # فقط اگر ثبت‌نام نکرده، جدید بساز
                self.save_data()
                self.send_message(chat_id, "برای شروع ثبت‌نام روی دکمه زیر بزنید:",
                    reply_markup=self.make_inline_keyboard([[{"text": "📝 ثبت‌نام در آموزشگاه", "callback_data": "start_registration"}]])
                )
            return True
        
        elif text == "معرفی آموزشگاه":
            self.send_message(chat_id, 
                "_🏫 *معرفی آموزشگاه*\n\n"
                "آموزشگاه ما با بیش از ۱۰ سال سابقه در زمینه آموزش قرآن کریم، "
                "خدمات متنوعی ارائه می‌دهد:\n\n"
                "📚 *کلاس‌های موجود:*\n"
                "• تجوید قرآن کریم\n"
                "• صوت و لحن\n"
                "• حفظ قرآن کریم\n"
                "• تفسیر قرآن\n\n"
                "💎 *مزایای ثبت‌نام:*\n"
                "• اساتید مجرب\n"
                "• کلاس‌های آنلاین و حضوری\n"
                "• گواهی پایان دوره\n"
                "• قیمت مناسب_\n\n"
                "برای ثبت‌نام روی دکمه زیر کلیک کنید:",
                reply_markup=self.make_inline_keyboard([[{"text": "📝 ثبت‌نام در آموزشگاه", "callback_data": "start_registration"}]])
            )
            return True
        
        elif text == "خروج":
            self.send_message(chat_id, "_👋 با تشکر از استفاده شما از ربات ما. موفق باشید! 🌟_")
            return True
        
        elif text == "برگشت به قبل":
            if user_id in self.user_data:
                # برگشت به مرحله قبل
                if "phone" in self.user_data[user_id]:
                    self.user_data[user_id].pop("phone", None)
                    self.save_data()
                    self.send_message(chat_id, "_لطفاً شماره تلفن خود را دوباره ارسال کنید._",
                        reply_markup={"keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]], "resize_keyboard": True}
                    )
                elif "national_id" in self.user_data[user_id]:
                    self.user_data[user_id].pop("national_id", None)
                    self.save_data()
                    self.send_message(chat_id, "_لطفاً کد ملی خود را دوباره وارد کنید._")
                elif "full_name" in self.user_data[user_id]:
                    self.user_data[user_id].pop("full_name", None)
                    self.save_data()
                    self.send_message(chat_id, "_لطفاً نام خود را دوباره وارد کنید._")
            return True
        
        elif user_id in self.user_data:
            state = self.user_data[user_id]
            
            # مرحله: نام
            if "full_name" not in state:
                self.user_data[user_id]["full_name"] = text
                self.user_data[user_id]["first_name"] = text.split()[0]
                self.save_data()
                self.send_message(chat_id, f"_{state['first_name']} عزیز،\nنام شما: {text}\nکد ملی: هنوز مانده\nتلفن: هنوز مانده_\n\nلطفاً کد ملی ۱۰ رقمی خود را وارد کنید.",
                    reply_markup=self.make_keyboard([["شروع مجدد", "خروج", "برگشت به قبل"]]))
                self.send_message(chat_id, "می‌خواهید نام را ویرایش کنید؟",
                    reply_markup=self.make_inline_keyboard([[{"text": "✏️ تصحیح نام", "callback_data": "edit_name"}]]))
                return True
            
            # مرحله: کد ملی
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
                        reply_markup={
                            "keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]],
                            "resize_keyboard": True
                        }
                    )
                    return True
                else:
                    self.send_message(chat_id, "_❌ کد ملی نامعتبر است. لطفاً ۱۰ رقم وارد کنید._")
                    return True
            
            # مرحله: شماره تلفن
            elif "phone" not in state and contact:
                phone_number = contact["phone_number"]
                self.user_data[user_id]["phone"] = phone_number
                self.save_data()
                
                # بررسی مدیر بودن از طریق شماره تلفن
                is_admin_user, admin_role = self.is_admin(user_id, phone_number)
                if is_admin_user:
                    # اگر مدیر است، پیام ویژه نمایش بده
                    self.send_message(
                        chat_id,
                        f"_👑 {admin_role} عزیز،\n"
                        f"نام: {state['full_name']}\n"
                        f"کد ملی: {state['national_id']}\n"
                        f"تلفن: {phone_number}\n\n"
                        f"شما به عنوان {admin_role} شناسایی شدید! 🌟_",
                        reply_markup=self.make_inline_keyboard([
                            [{"text": "✅ تأیید نهایی", "callback_data": "final_confirm"}],
                            [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}],
                            [{"text": "👑 ورود به پنل مدیریتی", "callback_data": "admin_panel"}]
                        ])
                    )
                    return True
                else:
                    # کاربر عادی
                    self.send_message(
                        chat_id,
                        f"_📋 {state['first_name']} عزیز، حساب کاربری شما:\nنام: {state['full_name']}\nکد ملی: {state['national_id']}\nتلفن: {phone_number}_",
                        reply_markup=self.make_inline_keyboard([
                            [{"text": "✅ تأیید نهایی", "callback_data": "final_confirm"}],
                            [{"text": "✏️ تصحیح اطلاعات", "callback_data": "edit_info"}]
                        ])
                    )
                    return True
        
        return False  # پیام پردازش نشد
    
    def handle_callback(self, callback):
        """مدیریت کال‌بک‌های دریافتی"""
        query = callback
        data = query["data"]
        chat_id = query["message"]["chat"]["id"]
        user_id = str(chat_id)
        
        if data == "start_registration":
            self.user_data[user_id] = {}
            self.save_data()
            self.send_message(chat_id, "_لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی)._")
            return True
        elif data == "edit_name":
            self.user_data[user_id].pop("full_name", None)
            self.save_data()
            self.send_message(chat_id, "_نام جدید را وارد کنید._")
            return True
        elif data == "edit_national_id":
            self.user_data[user_id].pop("national_id", None)
            self.save_data()
            self.send_message(chat_id, "_کد ملی جدید را وارد کنید._")
            return True
        elif data == "edit_info":
            self.user_data[user_id] = {}
            self.save_data()
            self.send_message(chat_id, "_بیایید دوباره شروع کنیم. لطفاً نام و نام خانوادگی خود را وارد کنید._")
            return True
        elif data == "final_confirm":
            self.send_message(chat_id, f"🎉 {self.user_data[user_id]['first_name']} عزیز، ثبت‌نام شما با موفقیت تکمیل شد! موفق باشید!")
            return True
        elif data == "choose_class":
            # نمایش کلاس‌های موجود
            classes = self.user_data.get("classes", [])
            if classes:
                class_text = "_📚 کلاس‌های موجود:_\n\n"
                for i, cls in enumerate(classes, 1):
                    class_text += f"*{i}. {cls['name']}*\n"
                    class_text += f"بخش: {cls['section']}\n"
                    class_text += f"قیمت: {cls['price']} تومان\n\n"
                self.send_message(chat_id, class_text)
                return True
            else:
                self.send_message(chat_id, "_📚 در حال حاضر کلاسی موجود نیست. لطفاً بعداً مراجعه کنید._")
                return True
        elif data == "admin_panel":
            # ورود به پنل مدیریتی
            is_admin_user, admin_role = self.is_admin(user_id)
            if is_admin_user:
                self.send_message(chat_id, 
                    f"_👑 {admin_role} عزیز، به پنل مدیریتی خوش آمدید!_",
                    reply_markup=self.make_keyboard([["📊 آمار کاربران", "👥 مدیریت کاربران"], ["📚 مدیریت کلاس‌ها", "⚙️ تنظیمات"], ["🔙 بازگشت به حالت عادی"]])
                )
                return True
            else:
                self.send_message(chat_id, "_❌ شما دسترسی مدیریتی ندارید._")
                return True
        
        return False  # کال‌بک پردازش نشد