import os
import json
import logging
import requests

class AdminModule:
    """ماژول مدیریت پنل ادمین"""
    
    def __init__(self, bot_token, base_url, data_file):
        """مقداردهی اولیه ماژول مدیریت"""
        self.bot_token = bot_token
        self.base_url = base_url
        self.data_file = data_file
        self.data = self.load_data()
        self.admin_states = {}
    
    def load_data(self):
        """بارگذاری یا ایجاد فایل اطلاعات"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                # فایل وجود ندارد - ایجاد فایل جدید
                empty_data = {"admin": {}, "classes": []}
                self.save_data(empty_data)
                return empty_data
        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            # فایل خراب است - پاک کردن و ایجاد مجدد
            logging.error(f"خطا در بارگذاری فایل: {e}")
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
            empty_data = {"admin": {}, "classes": []}
            self.save_data(empty_data)
            return empty_data
    
    def save_data(self, data_to_save=None):
        """ذخیره داده‌ها در فایل"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data_to_save if data_to_save else self.data, f, ensure_ascii=False, indent=2)
            logging.info("داده‌ها با موفقیت ذخیره شدند")
        except Exception as e:
            logging.error(f"خطا در ذخیره فایل: {e}")
    
    def send_message(self, chat_id, text, reply_markup=None):
        """ارسال پیام"""
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            if reply_markup:
                payload["reply_markup"] = reply_markup
            response = requests.post(f"{self.base_url}/sendMessage", json=payload)
            if response.status_code != 200:
                logging.error(f"خطا در ارسال پیام: {response.text}")
        except Exception as e:
            logging.error(f"خطا در ارسال پیام: {e}")
    
    def get_main_keyboard(self):
        """کیبورد اصلی"""
        return {"keyboard": [["شروع مجدد", "پنل کاربری"]], "resize_keyboard": True}
    
    def get_inline_name_request(self):
        """کیبورد درخواست نام"""
        return {"inline_keyboard": [[{"text": "📝 وارد کردن نام و نام خانوادگی", "callback_data": "enter_name"}]]}
    
    def get_inline_national_id(self):
        """کیبورد درخواست کد ملی"""
        return {"inline_keyboard": [[{"text": "📍 وارد کردن کد ملی", "callback_data": "enter_nid"}]]}
    
    def get_inline_confirm_admin(self):
        """کیبورد تأیید اطلاعات مدیر"""
        return {"inline_keyboard": [[{"text": "✅ تأیید اطلاعات", "callback_data": "confirm_admin"}]]}
    
    def get_inline_add_class(self):
        """کیبورد افزودن کلاس"""
        return {"inline_keyboard": [[{"text": "➕ افزودن کلاس جدید", "callback_data": "add_class"}]]}
    
    def get_inline_class_menu(self):
        """کیبورد منوی کلاس"""
        return {"inline_keyboard": [
            [{"text": "📄 مشاهده کلاس‌ها", "callback_data": "view_classes"}],
            [{"text": "➕ افزودن کلاس", "callback_data": "add_class"}],
            [{"text": "✏️ ویرایش کلاس", "callback_data": "edit_class"}]
        ]}
    
    def handle_message(self, message):
        """مدیریت پیام‌های دریافتی"""
        chat_id = message["chat"]["id"]
        user_id = str(chat_id)
        text = message.get("text", "")
        
        # مدیریت ثبت‌نام مدیر
        if self.admin_states.get(user_id) == "awaiting_admin_name":
            self.data["admin"]["full_name"] = text
            self.data["admin"]["user_id"] = user_id
            self.save_data()
            self.admin_states[user_id] = "awaiting_admin_nid"
            self.send_message(chat_id, "📍 لطفاً کد ملی خود را وارد کنید:")
            return True
        
        if self.admin_states.get(user_id) == "awaiting_admin_nid":
            self.data["admin"]["national_id"] = text
            self.data["admin"]["user_id"] = user_id  # ثبت user_id مدیر
            self.save_data()
            self.admin_states[user_id] = "main_menu"
            self.send_message(chat_id, "✅ اطلاعات شما ثبت شد.", reply_markup=self.get_inline_confirm_admin())
            return True
        
        # اگر مدیر قبلاً ثبت شده باشد
        if self.data["admin"].get("user_id") == user_id:
            state = self.admin_states.get(user_id, "main_menu")
            
            if text == "شروع مجدد":
                self.admin_states[user_id] = "main_menu"
                self.send_message(chat_id, "🔄 بازگشت به منوی اصلی.", reply_markup=self.get_main_keyboard())
                return True
            elif text == "پنل کاربری":
                self.send_message(chat_id, "👤 پنل مدیریت:", reply_markup=self.get_inline_class_menu())
                return True
            elif state == "awaiting_class_name":
                self.admin_states[user_id] = "awaiting_class_section"
                self.data["temp_class"] = {"name": text}
                self.send_message(chat_id, "✍️ لطفاً بخش کلاس را وارد کنید:")
                return True
            elif state == "awaiting_class_section":
                self.admin_states[user_id] = "awaiting_class_price"
                self.data["temp_class"]["section"] = text
                self.send_message(chat_id, "💰 لطفاً هزینه کلاس را وارد کنید:")
                return True
            elif state == "awaiting_class_price":
                self.admin_states[user_id] = "awaiting_class_link"
                self.data["temp_class"]["price"] = text
                self.send_message(chat_id, "🔗 لطفاً لینک گروه کلاس را وارد کنید:")
                return True
            elif state == "awaiting_class_link":
                class_obj = self.data["temp_class"]
                class_obj["link"] = text
                self.data["classes"].append(class_obj)
                self.save_data()
                self.admin_states[user_id] = "main_menu"
                self.send_message(chat_id, "✅ کلاس با موفقیت اضافه شد.", reply_markup=self.get_inline_class_menu())
                return True
            else:
                self.send_message(chat_id, "❓ لطفاً یکی از گزینه‌ها را انتخاب کنید.", reply_markup=self.get_main_keyboard())
                return True
        else:
            # اگر مدیر ثبت نشده باشد
            if "full_name" not in self.data["admin"]:
                self.send_message(chat_id, "🌟 به پنل مدیریت خوش آمدید!", reply_markup=self.get_inline_name_request())
                return True
            else:
                self.send_message(chat_id, "⛔ شما اجازه دسترسی ندارید.")
                return False
    
    def handle_callback(self, callback):
        """مدیریت کال‌بک‌های دریافتی"""
        chat_id = callback["message"]["chat"]["id"]
        user_id = str(chat_id)
        data_id = callback["id"]
        data_call = callback["data"]
        
        if data_call == "enter_name":
            self.admin_states[user_id] = "awaiting_admin_name"
            self.send_message(chat_id, "👤 لطفاً نام و نام خانوادگی خود را وارد کنید:")
            return True
        elif data_call == "enter_nid":
            self.admin_states[user_id] = "awaiting_admin_nid"
            self.send_message(chat_id, "📍 لطفاً کد ملی خود را وارد کنید:")
            return True
        elif data_call == "confirm_admin":
            self.data["admin"]["user_id"] = user_id
            self.save_data()
            self.send_message(chat_id, "✅ ثبت‌نام شما با موفقیت انجام شد.", reply_markup=self.get_main_keyboard())
            return True
        elif data_call == "add_class":
            self.admin_states[user_id] = "awaiting_class_name"
            self.send_message(chat_id, "📝 لطفاً نام کلاس را وارد کنید:")
            return True
        elif data_call == "view_classes":
            if not self.data["classes"]:
                self.send_message(chat_id, "❗ هیچ کلاسی ثبت نشده است.")
            else:
                text = "📚 لیست کلاس‌ها:\n"
                for idx, c in enumerate(self.data["classes"], 1):
                    text += f"{idx}. {c['name']} | بخش: {c['section']} | 💰 {c['price']} | لینک: {c['link']}\n"
                self.send_message(chat_id, text)
            return True
        
        return False  # کال‌بک پردازش نشد