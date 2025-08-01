# kargah_module.py
import requests
import json
from datetime import datetime
from config import BASE_URL, ADMIN_USER_IDS
import logging
from typing import Dict, List, Optional, Any

# تنظیم لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KargahModule:
    def __init__(self):
        self.workshops = {}  # ذخیره کارگاه‌ها
        self.user_states = {}  # وضعیت کاربران
        self.temp_data = {}  # داده‌های موقت برای اضافه/ویرایش
        self.load_workshops()
        logger.info("KargahModule initialized successfully")

    def load_workshops(self):
        """بارگذاری کارگاه‌ها از فایل"""
        try:
            with open('workshops.json', 'r', encoding='utf-8') as f:
                self.workshops = json.load(f)
        except FileNotFoundError:
            self.workshops = {}
            logger.info("No workshops file found, starting with empty workshops")
        except Exception as e:
            logger.error(f"Error loading workshops: {e}")
            self.workshops = {}

    def save_workshops(self):
        """ذخیره کارگاه‌ها در فایل"""
        try:
            with open('workshops.json', 'w', encoding='utf-8') as f:
                json.dump(self.workshops, f, ensure_ascii=False, indent=2)
            logger.info("Workshops saved successfully")
        except Exception as e:
            logger.error(f"Error saving workshops: {e}")

    def _make_request(self, url: str, payload: Dict[str, Any]) -> Optional[requests.Response]:
        """ارسال درخواست HTTP با مدیریت خطا"""
        try:
            response = requests.post(url, json=payload, timeout=10)
            logger.debug(f"Request to {url}: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Error in request to {url}: {e}")
            return None

    def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> bool:
        """ارسال پیام"""
        if not text or not text.strip():
            logger.error("Empty message text provided")
            return False
            
        url = f"{BASE_URL}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": text[:4096],
            "parse_mode": "Markdown"
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
            
        response = self._make_request(url, payload)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                logger.info(f"Message sent successfully to {chat_id}")
                return True
            else:
                logger.error(f"Telegram API error: {result.get('description', 'Unknown error')}")
        
        logger.error(f"Failed to send message to {chat_id}")
        return False

    def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: Optional[Dict] = None) -> bool:
        """ویرایش پیام"""
        if not text or not text.strip():
            logger.error("Empty message text provided for edit")
            return False
            
        url = f"{BASE_URL}/editMessageText"
        payload = {
            "chat_id": chat_id, 
            "message_id": message_id, 
            "text": text[:4096],
            "parse_mode": "Markdown"
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
            
        response = self._make_request(url, payload)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                logger.info(f"Message edited successfully in {chat_id}")
                return True
            else:
                logger.error(f"Telegram API error: {result.get('description', 'Unknown error')}")
        
        logger.error(f"Failed to edit message in {chat_id}")
        return False

    def answer_callback_query(self, callback_query_id: str, text: Optional[str] = None) -> bool:
        """پاسخ به callback query"""
        url = f"{BASE_URL}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        
        if text:
            payload["text"] = text[:200]  # محدودیت طول متن
            
        response = self._make_request(url, payload)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                logger.info(f"Callback query answered successfully")
                return True
            else:
                logger.error(f"Telegram API error: {result.get('description', 'Unknown error')}")
        
        logger.error(f"Failed to answer callback query")
        return False

    def is_user_admin(self, user_id: int) -> bool:
        """بررسی اینکه آیا کاربر مدیر است"""
        return user_id in ADMIN_USER_IDS

    def get_workshop_list_keyboard(self) -> Dict[str, List]:
        """کیبورد لیست کارگاه‌ها"""
        keyboard = []
        
        if not self.workshops:
            keyboard.append([{"text": "📝 کارگاه جدید", "callback_data": "kargah_add"}])
            keyboard.append([{"text": "🔙 بازگشت", "callback_data": "kargah_back"}])
        else:
            for workshop_id, workshop in self.workshops.items():
                instructor_name = workshop.get('instructor_name', 'نامشخص')
                cost = workshop.get('cost', 'نامشخص')
                keyboard.append([{
                    "text": f"📚 {instructor_name} - {cost}",
                    "callback_data": f"kargah_view_{workshop_id}"
                }])
            
            keyboard.append([{"text": "📝 کارگاه جدید", "callback_data": "kargah_add"}])
            keyboard.append([{"text": "🔙 بازگشت", "callback_data": "kargah_back"}])
        
        return {"inline_keyboard": keyboard}

    def get_workshop_management_keyboard(self) -> Dict[str, List]:
        """کیبورد مدیریت کارگاه - ساده و کاربردی"""
        keyboard = []
        
        # نمایش لیست کارگاه‌ها
        if self.workshops:
            for workshop_id, workshop in self.workshops.items():
                instructor_name = workshop.get('instructor_name', 'نامشخص')
                cost = workshop.get('cost', 'نامشخص')
                keyboard.append([{
                    "text": f"📚 {instructor_name} - {cost}",
                    "callback_data": f"kargah_view_{workshop_id}"
                }])
        
        # دکمه‌های عملیات
        keyboard.append([{"text": "📝 اضافه کردن کارگاه", "callback_data": "kargah_add"}])
        keyboard.append([{"text": "🔙 بازگشت", "callback_data": "kargah_back"}])
        
        return {"inline_keyboard": keyboard}

    def get_workshop_edit_keyboard(self, workshop_id: str) -> Dict[str, List]:
        """کیبورد ویرایش کارگاه"""
        keyboard = [
            [{"text": "✏️ ویرایش نام مربی", "callback_data": f"kargah_edit_instructor_{workshop_id}"}],
            [{"text": "💰 ویرایش هزینه", "callback_data": f"kargah_edit_cost_{workshop_id}"}],
            [{"text": "🔗 ویرایش لینک", "callback_data": f"kargah_edit_link_{workshop_id}"}],
            [{"text": "🗑️ حذف کارگاه", "callback_data": f"kargah_delete_{workshop_id}"}],
            [{"text": "🔙 بازگشت", "callback_data": "kargah_list"}]
        ]
        return {"inline_keyboard": keyboard}

    def handle_message(self, message: Dict):
        """پردازش پیام‌های متنی"""
        if not self.validate_message_structure(message):
            return
        
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        
        if not self.is_user_admin(user_id):
            return
        
        # بررسی وضعیت کاربر
        user_state = self.user_states.get(user_id, "")
        
        if user_state.startswith("kargah_add_"):
            self._handle_add_workshop_step(chat_id, user_id, text, user_state)
        elif user_state.startswith("kargah_edit_"):
            self._handle_edit_workshop_step(chat_id, user_id, text, user_state)
        elif text == "/kargah":
            self._handle_kargah_command(chat_id, user_id)

    def handle_callback(self, callback: Dict):
        """پردازش callback query ها"""
        if not self.validate_callback_structure(callback):
            return
        
        chat_id = callback["message"]["chat"]["id"]
        user_id = callback["from"]["id"]
        message_id = callback["message"]["message_id"]
        data = callback["data"]
        callback_query_id = callback["id"]
        
        # بررسی callback های دانش‌آموزان (بدون نیاز به دسترسی ادمین)
        if data.startswith("student_") or data == "student_back_to_menu":
            self._route_callback(chat_id, message_id, user_id, data, callback_query_id)
            return
        
        # برای سایر callback ها، بررسی دسترسی ادمین
        if not self.is_user_admin(user_id):
            self.answer_callback_query(callback_query_id, "❌ شما دسترسی لازم را ندارید")
            return
        
        self._route_callback(chat_id, message_id, user_id, data, callback_query_id)

    def validate_message_structure(self, message: Dict) -> bool:
        """اعتبارسنجی ساختار پیام"""
        required_fields = ["chat", "from", "text"]
        return all(field in message for field in required_fields)

    def validate_callback_structure(self, callback: Dict) -> bool:
        """اعتبارسنجی ساختار callback"""
        required_fields = ["message", "from", "data", "id"]
        return all(field in callback for field in required_fields)

    def _route_callback(self, chat_id: int, message_id: int, user_id: int, data: str, callback_query_id: str):
        """مسیریابی callback ها"""
        try:
            logger.info(f"Routing callback: {data}")
            
            # Callback های مربوط به دانش‌آموزان (بدون نیاز به دسترسی ادمین)
            if data.startswith("student_select_workshop_"):
                workshop_id = data.replace("student_select_workshop_", "")
                self._handle_student_select_workshop(chat_id, message_id, user_id, workshop_id, callback_query_id)
            elif data.startswith("student_pay_workshop_"):
                workshop_id = data.replace("student_pay_workshop_", "")
                self._handle_student_pay_workshop(chat_id, message_id, user_id, workshop_id, callback_query_id)
            elif data == "student_back_to_workshops":
                self._handle_student_back_to_workshops(chat_id, message_id, user_id, callback_query_id)
            elif data == "student_back_to_menu":
                self._handle_student_back_to_menu(chat_id, message_id, callback_query_id)
            # Callback های مربوط به ادمین‌ها
            elif data == "kargah_add":
                if not self.is_user_admin(user_id):
                    self.answer_callback_query(callback_query_id, "❌ شما دسترسی لازم را ندارید")
                    return
                self._handle_add_workshop(chat_id, message_id, user_id, callback_query_id)
            elif data == "kargah_back":
                if not self.is_user_admin(user_id):
                    self.answer_callback_query(callback_query_id, "❌ شما دسترسی لازم را ندارید")
                    return
                self._handle_back_to_main(chat_id, message_id, callback_query_id)
            elif data.startswith("kargah_view_"):
                if not self.is_user_admin(user_id):
                    self.answer_callback_query(callback_query_id, "❌ شما دسترسی لازم را ندارید")
                    return
                workshop_id = data.replace("kargah_view_", "")
                self._handle_view_workshop(chat_id, message_id, workshop_id, callback_query_id)
            elif data.startswith("kargah_edit_instructor_"):
                if not self.is_user_admin(user_id):
                    self.answer_callback_query(callback_query_id, "❌ شما دسترسی لازم را ندارید")
                    return
                workshop_id = data.replace("kargah_edit_instructor_", "")
                self._handle_edit_instructor(chat_id, message_id, user_id, workshop_id, callback_query_id)
            elif data.startswith("kargah_edit_cost_"):
                if not self.is_user_admin(user_id):
                    self.answer_callback_query(callback_query_id, "❌ شما دسترسی لازم را ندارید")
                    return
                workshop_id = data.replace("kargah_edit_cost_", "")
                self._handle_edit_cost(chat_id, message_id, user_id, workshop_id, callback_query_id)
            elif data.startswith("kargah_edit_link_"):
                if not self.is_user_admin(user_id):
                    self.answer_callback_query(callback_query_id, "❌ شما دسترسی لازم را ندارید")
                    return
                workshop_id = data.replace("kargah_edit_link_", "")
                self._handle_edit_link(chat_id, message_id, user_id, workshop_id, callback_query_id)
            elif data.startswith("kargah_delete_"):
                if not self.is_user_admin(user_id):
                    self.answer_callback_query(callback_query_id, "❌ شما دسترسی لازم را ندارید")
                    return
                workshop_id = data.replace("kargah_delete_", "")
                self._handle_delete_workshop(chat_id, message_id, workshop_id, callback_query_id)
            else:
                logger.warning(f"Unknown callback data: {data}")
                self.answer_callback_query(callback_query_id, "❌ دستور نامعلوم!")
                
        except Exception as e:
            logger.error(f"Error in callback routing: {e}")
            self.answer_callback_query(callback_query_id, "❌ خطا در پردازش!")

    def _handle_kargah_command(self, chat_id: int, user_id: int):
        """پردازش دستور /kargah"""
        if not self.workshops:
            text = "🏭 *مدیریت کارگاه‌ها*\n\n❌ هیچ کارگاهی ثبت نشده است.\nبرای شروع، کارگاه جدید اضافه کنید:"
        else:
            text = "🏭 *مدیریت کارگاه‌ها*\n\n📋 لیست کارگاه‌های ثبت شده:\n"
            for workshop_id, workshop in self.workshops.items():
                instructor_name = workshop.get('instructor_name', 'نامشخص')
                cost = workshop.get('cost', 'نامشخص')
                text += f"• {instructor_name} - {cost}\n"
            text += "\nبرای ویرایش، روی کارگاه مورد نظر کلیک کنید:"
        
        reply_markup = self.get_workshop_management_keyboard()
        self.send_message(chat_id, text, reply_markup)

    def _handle_list_workshops(self, chat_id: int, message_id: int, callback_query_id: str):
        """نمایش لیست کارگاه‌ها"""
        if not self.workshops:
            text = "📋 *لیست کارگاه‌ها*\n\n❌ هیچ کارگاهی ثبت نشده است."
        else:
            text = "📋 *لیست کارگاه‌ها*\n\n"
            for workshop_id, workshop in self.workshops.items():
                instructor_name = workshop.get('instructor_name', 'نامشخص')
                cost = workshop.get('cost', 'نامشخص')
                link = workshop.get('link', 'نامشخص')
                text += f"🏭 *{instructor_name}*\n"
                text += f"💰 هزینه: {cost}\n"
                text += f"🔗 لینک: {link}\n\n"
        
        reply_markup = self.get_workshop_list_keyboard()
        self.edit_message(chat_id, message_id, text, reply_markup)
        self.answer_callback_query(callback_query_id)

    def _handle_add_workshop(self, chat_id: int, message_id: int, user_id: int, callback_query_id: str):
        """شروع فرآیند اضافه کردن کارگاه"""
        self.user_states[user_id] = "kargah_add_instructor"
        self.temp_data[user_id] = {}
        
        text = "📝 *اضافه کردن کارگاه جدید*\n\nلطفاً نام مربی را وارد کنید:"
        self.edit_message(chat_id, message_id, text)
        self.answer_callback_query(callback_query_id)

    def _handle_add_workshop_step(self, chat_id: int, user_id: int, text: str, user_state: str):
        """پردازش مراحل اضافه کردن کارگاه"""
        try:
            logger.info(f"Processing add workshop step: {user_state}")
            
            if user_state == "kargah_add_instructor":
                self.temp_data[user_id]["instructor_name"] = text
                self.user_states[user_id] = "kargah_add_cost"
                
                response_text = "💰 لطفاً هزینه کارگاه را وارد کنید:\nمثال: 500,000 تومان"
                self.send_message(chat_id, response_text)
                
            elif user_state == "kargah_add_cost":
                # نرمال‌سازی متن هزینه
                normalized_cost = self._normalize_cost_text(text)
                self.temp_data[user_id]["cost"] = normalized_cost
                self.user_states[user_id] = "kargah_add_link"
                
                response_text = "🔗 لطفاً لینک گروه را وارد کنید:\nمثال: https://t.me/workshop_group"
                self.send_message(chat_id, response_text)
                
            elif user_state == "kargah_add_link":
                self.temp_data[user_id]["link"] = text
                
                # ایجاد کارگاه جدید
                workshop_id = str(len(self.workshops) + 1).zfill(2)
                self.workshops[workshop_id] = self.temp_data[user_id].copy()
                self.save_workshops()
                
                # پاک کردن داده‌های موقت
                del self.user_states[user_id]
                del self.temp_data[user_id]
                
                # نمایش منوی جدید با کارگاه اضافه شده
                response_text = f"✅ کارگاه *{self.temp_data[user_id]['instructor_name']}* با موفقیت اضافه شد!"
                reply_markup = self.get_workshop_management_keyboard()
                self.send_message(chat_id, response_text, reply_markup)
                
        except Exception as e:
            logger.error(f"Error in add workshop step: {e}")
            # پاک کردن وضعیت در صورت خطا
            if user_id in self.user_states:
                del self.user_states[user_id]
            if user_id in self.temp_data:
                del self.temp_data[user_id]
            
            response_text = "❌ خطا در اضافه کردن کارگاه. لطفاً دوباره تلاش کنید."
            reply_markup = self.get_workshop_management_keyboard()
            self.send_message(chat_id, response_text, reply_markup)

    def _handle_edit_workshop_menu(self, chat_id: int, message_id: int, callback_query_id: str):
        """نمایش منوی ویرایش کارگاه"""
        if not self.workshops:
            text = "❌ هیچ کارگاهی برای ویرایش وجود ندارد."
            reply_markup = self.get_workshop_management_keyboard()
        else:
            text = "✏️ *ویرایش کارگاه*\n\nلطفاً کارگاهی را انتخاب کنید:"
            keyboard = []
            for workshop_id, workshop in self.workshops.items():
                instructor_name = workshop.get('instructor_name', 'نامشخص')
                keyboard.append([{
                    "text": f"✏️ {instructor_name}",
                    "callback_data": f"kargah_view_{workshop_id}"
                }])
            keyboard.append([{"text": "🔙 بازگشت", "callback_data": "kargah_back"}])
            reply_markup = {"inline_keyboard": keyboard}
        
        self.edit_message(chat_id, message_id, text, reply_markup)
        self.answer_callback_query(callback_query_id)

    def _handle_view_workshop(self, chat_id: int, message_id: int, workshop_id: str, callback_query_id: str):
        """نمایش جزئیات کارگاه"""
        if workshop_id not in self.workshops:
            text = "❌ کارگاه مورد نظر یافت نشد."
            reply_markup = self.get_workshop_management_keyboard()
        else:
            workshop = self.workshops[workshop_id]
            instructor_name = workshop.get('instructor_name', 'نامشخص')
            cost = workshop.get('cost', 'نامشخص')
            link = workshop.get('link', 'نامشخص')
            
            text = f"🏭 *جزئیات کارگاه*\n\n"
            text += f"👨‍🏫 نام مربی: {instructor_name}\n"
            text += f"💰 هزینه: {cost}\n"
            text += f"🔗 لینک: {link}\n"
            text += f"🆔 کد: {workshop_id}"
            
            reply_markup = self.get_workshop_edit_keyboard(workshop_id)
        
        self.edit_message(chat_id, message_id, text, reply_markup)
        self.answer_callback_query(callback_query_id)

    def _handle_edit_instructor(self, chat_id: int, message_id: int, user_id: int, workshop_id: str, callback_query_id: str):
        """شروع ویرایش نام مربی"""
        if workshop_id not in self.workshops:
            self.answer_callback_query(callback_query_id, "❌ کارگاه مورد نظر یافت نشد")
            return
        
        self.user_states[user_id] = f"kargah_edit_instructor_{workshop_id}"
        self.temp_data[user_id] = {"workshop_id": workshop_id}
        
        text = "👨‍🏫 لطفاً نام جدید مربی را وارد کنید:"
        self.edit_message(chat_id, message_id, text)
        self.answer_callback_query(callback_query_id)

    def _handle_edit_cost(self, chat_id: int, message_id: int, user_id: int, workshop_id: str, callback_query_id: str):
        """شروع ویرایش هزینه"""
        if workshop_id not in self.workshops:
            self.answer_callback_query(callback_query_id, "❌ کارگاه مورد نظر یافت نشد")
            return
        
        self.user_states[user_id] = f"kargah_edit_cost_{workshop_id}"
        self.temp_data[user_id] = {"workshop_id": workshop_id}
        
        current_cost = self.workshops[workshop_id].get('cost', 'نامشخص')
        text = f"💰 *ویرایش هزینه کارگاه*\n\nهزینه فعلی: {current_cost}\n\nلطفاً هزینه جدید را وارد کنید:\n\nمثال‌ها:\n• 500,000 تومان\n• 750000 تومان\n• 1000000 تومان\n• ۱,۰۰۰,۰۰۰ تومان"
        self.edit_message(chat_id, message_id, text)
        self.answer_callback_query(callback_query_id)

    def _handle_edit_link(self, chat_id: int, message_id: int, user_id: int, workshop_id: str, callback_query_id: str):
        """شروع ویرایش لینک"""
        if workshop_id not in self.workshops:
            self.answer_callback_query(callback_query_id, "❌ کارگاه مورد نظر یافت نشد")
            return
        
        self.user_states[user_id] = f"kargah_edit_link_{workshop_id}"
        self.temp_data[user_id] = {"workshop_id": workshop_id}
        
        text = "🔗 لطفاً لینک جدید را وارد کنید:"
        self.edit_message(chat_id, message_id, text)
        self.answer_callback_query(callback_query_id)

    def _normalize_cost_text(self, text: str) -> str:
        """پاک کردن و نرمال‌سازی متن هزینه"""
        # تبدیل اعداد فارسی به انگلیسی
        persian_to_english = {
            '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
            '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
        }
        
        normalized_text = text
        for persian, english in persian_to_english.items():
            normalized_text = normalized_text.replace(persian, english)
        
        # حذف فاصله‌های اضافی
        normalized_text = normalized_text.strip()
        
        # اگر فقط عدد وارد شده، تومان اضافه کن
        if normalized_text.isdigit():
            normalized_text = f"{normalized_text} تومان"
        
        return normalized_text

    def _handle_edit_workshop_step(self, chat_id: int, user_id: int, text: str, user_state: str):
        """پردازش مراحل ویرایش کارگاه"""
        try:
            logger.info(f"Processing edit workshop step: {user_state}")
            
            if user_state.startswith("kargah_edit_instructor_"):
                workshop_id = user_state.replace("kargah_edit_instructor_", "")
                if workshop_id in self.workshops:
                    self.workshops[workshop_id]["instructor_name"] = text
                    self.save_workshops()
                    
                    del self.user_states[user_id]
                    if user_id in self.temp_data:
                        del self.temp_data[user_id]
                    
                    response_text = f"✅ نام مربی کارگاه *{workshop_id}* با موفقیت به *{text}* تغییر یافت!"
                    reply_markup = self.get_workshop_management_keyboard()
                    self.send_message(chat_id, response_text, reply_markup)
                else:
                    response_text = "❌ کارگاه مورد نظر یافت نشد!"
                    reply_markup = self.get_workshop_management_keyboard()
                    self.send_message(chat_id, response_text, reply_markup)
                    
            elif user_state.startswith("kargah_edit_cost_"):
                workshop_id = user_state.replace("kargah_edit_cost_", "")
                if workshop_id in self.workshops:
                    # نرمال‌سازی متن هزینه
                    normalized_cost = self._normalize_cost_text(text)
                    self.workshops[workshop_id]["cost"] = normalized_cost
                    self.save_workshops()
                    
                    del self.user_states[user_id]
                    if user_id in self.temp_data:
                        del self.temp_data[user_id]
                    
                    response_text = f"✅ هزینه کارگاه *{workshop_id}* با موفقیت به *{normalized_cost}* تغییر یافت!"
                    reply_markup = self.get_workshop_management_keyboard()
                    self.send_message(chat_id, response_text, reply_markup)
                else:
                    response_text = "❌ کارگاه مورد نظر یافت نشد!"
                    reply_markup = self.get_workshop_management_keyboard()
                    self.send_message(chat_id, response_text, reply_markup)
                    
            elif user_state.startswith("kargah_edit_link_"):
                workshop_id = user_state.replace("kargah_edit_link_", "")
                if workshop_id in self.workshops:
                    self.workshops[workshop_id]["link"] = text
                    self.save_workshops()
                    
                    del self.user_states[user_id]
                    if user_id in self.temp_data:
                        del self.temp_data[user_id]
                    
                    response_text = f"✅ لینک کارگاه *{workshop_id}* با موفقیت تغییر یافت!"
                    reply_markup = self.get_workshop_management_keyboard()
                    self.send_message(chat_id, response_text, reply_markup)
                else:
                    response_text = "❌ کارگاه مورد نظر یافت نشد!"
                    reply_markup = self.get_workshop_management_keyboard()
                    self.send_message(chat_id, response_text, reply_markup)
                    
        except Exception as e:
            logger.error(f"Error in edit workshop step: {e}")
            # پاک کردن وضعیت در صورت خطا
            if user_id in self.user_states:
                del self.user_states[user_id]
            if user_id in self.temp_data:
                del self.temp_data[user_id]
            
            response_text = "❌ خطا در ویرایش کارگاه. لطفاً دوباره تلاش کنید."
            reply_markup = self.get_workshop_management_keyboard()
            self.send_message(chat_id, response_text, reply_markup)

    def _handle_delete_workshop(self, chat_id: int, message_id: int, workshop_id: str, callback_query_id: str):
        """حذف کارگاه"""
        if workshop_id not in self.workshops:
            self.answer_callback_query(callback_query_id, "❌ کارگاه مورد نظر یافت نشد")
            return
        
        workshop_name = self.workshops[workshop_id].get('instructor_name', 'نامشخص')
        del self.workshops[workshop_id]
        self.save_workshops()
        
        text = f"🗑️ کارگاه {workshop_name} با موفقیت حذف شد!"
        reply_markup = self.get_workshop_management_keyboard()
        self.edit_message(chat_id, message_id, text, reply_markup)
        self.answer_callback_query(callback_query_id)

    def _handle_back_to_main(self, chat_id: int, message_id: int, callback_query_id: str):
        """بازگشت به منوی اصلی"""
        text = "🏭 *مدیریت کارگاه‌ها*\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
        reply_markup = self.get_workshop_management_keyboard()
        self.edit_message(chat_id, message_id, text, reply_markup)
        self.answer_callback_query(callback_query_id)

    def show_workshops_for_student(self, chat_id: int, user_id: int):
        """نمایش لیست کارگاه‌ها برای دانش‌آموز"""
        if not self.workshops:
            text = """📚 **انتخاب کلاس**

❌ در حال حاضر هیچ کلاسی برای ثبت‌نام موجود نیست.
لطفاً بعداً دوباره تلاش کنید یا با مدیر تماس بگیرید."""
            
            self.send_message(chat_id, text,
                reply_markup=self.build_reply_keyboard([
                    ["🏠 بازگشت به منو", "خروج"]
                ])
            )
        else:
            text = """📚 **انتخاب کلاس**

لطفاً یکی از کلاس‌های زیر را انتخاب کنید:"""
            
            # ساخت کیبورد برای انتخاب کارگاه
            keyboard = []
            for workshop_id, workshop in self.workshops.items():
                instructor_name = workshop.get('instructor_name', 'نامشخص')
                cost = workshop.get('cost', 'نامشخص')
                keyboard.append([{
                    "text": f"📚 {instructor_name} - {cost}",
                    "callback_data": f"student_select_workshop_{workshop_id}"
                }])
            
            keyboard.append([{"text": "🏠 بازگشت به منو", "callback_data": "student_back_to_menu"}])
            
            reply_markup = {"inline_keyboard": keyboard}
            self.send_message(chat_id, text, reply_markup)

    def build_reply_keyboard(self, buttons: List[List[str]]) -> Dict:
        """ساخت کیبورد معمولی"""
        return {
            "keyboard": [[{"text": btn} for btn in row] for row in buttons],
            "resize_keyboard": True
        }

    def _handle_student_select_workshop(self, chat_id: int, message_id: int, user_id: int, workshop_id: str, callback_query_id: str):
        """پردازش انتخاب کارگاه توسط دانش‌آموز"""
        if workshop_id not in self.workshops:
            self.answer_callback_query(callback_query_id, "❌ کارگاه مورد نظر یافت نشد!")
            return
        
        workshop = self.workshops[workshop_id]
        instructor_name = workshop.get('instructor_name', 'نامشخص')
        cost = workshop.get('cost', 'نامشخص')
        link = workshop.get('link', 'نامشخص')
        
        text = f"""📚 **جزئیات کلاس انتخاب شده**

🏭 **مربی:** {instructor_name}
💰 **هزینه:** {cost}
🔗 **لینک گروه:** {link}

✅ شما این کلاس را انتخاب کرده‌اید.
برای تکمیل ثبت‌نام، لطفاً روی دکمه پرداخت کلیک کنید."""
        
        keyboard = [
            [{"text": "💳 پرداخت و ثبت‌نام", "callback_data": f"student_pay_workshop_{workshop_id}"}],
            [{"text": "🔙 بازگشت به لیست کلاس‌ها", "callback_data": "student_back_to_workshops"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "student_back_to_menu"}]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self.edit_message(chat_id, message_id, text, reply_markup)
        self.answer_callback_query(callback_query_id)

    def _handle_student_back_to_menu(self, chat_id: int, message_id: int, callback_query_id: str):
        """بازگشت دانش‌آموز به منوی اصلی"""
        text = """🏠 **بازگشت به منوی اصلی**

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
        
        self.edit_message(chat_id, message_id, text,
            reply_markup=self.build_reply_keyboard([
                ["📚 انتخاب کلاس"],
                ["📊 مشاهده لیست حضور و غیاب"],
                ["📈 آمار کلی"],
                ["🏠 برگشت به منو", "خروج"]
            ])
        )
        self.answer_callback_query(callback_query_id)

    def _handle_student_pay_workshop(self, chat_id: int, message_id: int, user_id: int, workshop_id: str, callback_query_id: str):
        """پردازش پرداخت کارگاه توسط دانش‌آموز"""
        if workshop_id not in self.workshops:
            self.answer_callback_query(callback_query_id, "❌ کارگاه مورد نظر یافت نشد!")
            return
        
        workshop = self.workshops[workshop_id]
        instructor_name = workshop.get('instructor_name', 'نامشخص')
        cost = workshop.get('cost', 'نامشخص')
        
        text = f"""💳 **پرداخت و ثبت‌نام**

🏭 **کلاس انتخاب شده:** {instructor_name}
💰 **هزینه:** {cost}

برای تکمیل ثبت‌نام، لطفاً روی دکمه پرداخت کلیک کنید."""
        
        # اینجا باید به ماژول پرداخت ارسال شود
        # فعلاً پیام ساده نمایش می‌دهیم
        keyboard = [
            [{"text": "💳 پرداخت", "callback_data": f"pay_workshop_{workshop_id}"}],
            [{"text": "🔙 بازگشت", "callback_data": f"student_select_workshop_{workshop_id}"}]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self.edit_message(chat_id, message_id, text, reply_markup)
        self.answer_callback_query(callback_query_id)

    def _handle_student_back_to_workshops(self, chat_id: int, message_id: int, user_id: int, callback_query_id: str):
        """بازگشت دانش‌آموز به لیست کارگاه‌ها"""
        if not self.workshops:
            text = """📚 **انتخاب کلاس**

❌ در حال حاضر هیچ کلاسی برای ثبت‌نام موجود نیست.
لطفاً بعداً دوباره تلاش کنید یا با مدیر تماس بگیرید."""
            
            self.edit_message(chat_id, message_id, text,
                reply_markup=self.build_reply_keyboard([
                    ["🏠 بازگشت به منو", "خروج"]
                ])
            )
        else:
            text = """📚 **انتخاب کلاس**

لطفاً یکی از کلاس‌های زیر را انتخاب کنید:"""
            
            # ساخت کیبورد برای انتخاب کارگاه
            keyboard = []
            for workshop_id, workshop in self.workshops.items():
                instructor_name = workshop.get('instructor_name', 'نامشخص')
                cost = workshop.get('cost', 'نامشخص')
                keyboard.append([{
                    "text": f"📚 {instructor_name} - {cost}",
                    "callback_data": f"student_select_workshop_{workshop_id}"
                }])
            
            keyboard.append([{"text": "🏠 بازگشت به منو", "callback_data": "student_back_to_menu"}])
            
            reply_markup = {"inline_keyboard": keyboard}
            self.edit_message(chat_id, message_id, text, reply_markup)
        
        self.answer_callback_query(callback_query_id) 