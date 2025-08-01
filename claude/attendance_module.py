# attendance_module.py
import requests
import jdatetime
from datetime import datetime
from config import BASE_URL, AUTHORIZED_USER_IDS, ADMIN_USER_IDS, HELPER_COACH_USER_IDS
import logging
from typing import Dict, List, Optional, Any
import time

# تنظیم لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttendanceModule:
    def __init__(self):
        self.users: List[int] = []
        self.attendance_data: Dict[int, str] = {}
        self.user_states: Dict[int, str] = {}
        self.current_group_id: Optional[int] = None
        self.user_names_cache: Dict[int, str] = {}
        self.group_names_cache: Dict[int, str] = {}
        
        # آیکون‌های وضعیت
        self.status_icons = {
            "حاضر": "✅",
            "حضور با تاخیر": "⏰", 
            "غایب": "❌",
            "غیبت(موجه)": "📄",
            "در انتظار": "⏳"
        }
        
        # وضعیت‌های معتبر
        self.valid_statuses = {"حاضر", "حضور با تاخیر", "غایب", "غیبت(موجه)", "در انتظار"}
        
        # محدودیت تعداد تلاش‌های مجدد
        self.max_retries = 3
        self.retry_delay = 1  # ثانیه
        
        logger.info("AttendanceModule initialized successfully")

    def _make_request(self, url: str, payload: Dict[str, Any], retries: int = 0) -> Optional[requests.Response]:
        """ارسال درخواست HTTP با مدیریت خطا و تلاش مجدد"""
        try:
            response = requests.post(url, json=payload, timeout=10)
            logger.debug(f"Request to {url}: {response.status_code}")
            return response
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error for {url}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {url}")
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
        
        # تلاش مجدد
        if retries < self.max_retries:
            time.sleep(self.retry_delay)
            return self._make_request(url, payload, retries + 1)
        
        return None

    def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> bool:
        """ارسال پیام با مدیریت بهتر خطا"""
        if not text or not text.strip():
            logger.error("Empty message text provided")
            return False
            
        url = f"{BASE_URL}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": text[:4096],  # محدودیت طول پیام تلگرام
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
        """ویرایش پیام با مدیریت بهتر خطا"""
        if not text or not text.strip():
            logger.error("Empty message text provided for edit")
            return False
            
        url = f"{BASE_URL}/editMessageText"
        payload = {
            "chat_id": chat_id, 
            "message_id": message_id, 
            "text": text[:4096],  # محدودیت طول پیام تلگرام
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
                error_desc = result.get('description', 'Unknown error')
                if "message is not modified" not in error_desc:
                    logger.error(f"Telegram API error: {error_desc}")
        
        logger.error(f"Failed to edit message in {chat_id}")
        return False

    def answer_callback_query(self, callback_query_id: str, text: Optional[str] = None) -> bool:
        """پاسخ به callback query با مدیریت خطا"""
        url = f"{BASE_URL}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        
        if text:
            payload["text"] = text[:200]  # محدودیت طول callback query
            
        response = self._make_request(url, payload)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                return True
            else:
                logger.error(f"Callback query error: {result.get('description', 'Unknown error')}")
        
        return False

    def get_user_name(self, user_id: int, user_info: Optional[Dict] = None) -> str:
        """دریافت نام کاربر با مدیریت کش بهتر"""
        if not isinstance(user_id, int):
            logger.error(f"Invalid user_id type: {type(user_id)}")
            return f"کاربر نامعلوم"
            
        # بررسی کش
        if user_id in self.user_names_cache:
            return self.user_names_cache[user_id]
        
        # استفاده از user_info ارائه شده
        if user_info and isinstance(user_info, dict):
            name = self._extract_user_name(user_info, user_id)
            if name:
                self.user_names_cache[user_id] = name
                return name
        
        # تلاش برای دریافت از گروه‌ها
        name = self._get_user_name_from_groups(user_id)
        if name:
            self.user_names_cache[user_id] = name
            return name
        
        # نام پیش‌فرض
        default_name = f"کاربر {user_id}"
        self.user_names_cache[user_id] = default_name
        return default_name

    def _extract_user_name(self, user_info: Dict, user_id: int) -> Optional[str]:
        """استخراج نام کاربر از اطلاعات user_info"""
        try:
            first_name = user_info.get("first_name", "").strip()
            last_name = user_info.get("last_name", "").strip()
            username = user_info.get("username", "").strip()
            
            if first_name and last_name:
                return f"{first_name} {last_name}"
            elif first_name and username:
                return f"{first_name} (@{username})"
            elif first_name:
                return first_name
            elif username:
                return f"@{username}"
            
        except Exception as e:
            logger.error(f"Error extracting user name: {e}")
        
        return None

    def _get_user_name_from_groups(self, user_id: int) -> Optional[str]:
        """دریافت نام کاربر از گروه‌ها"""
        try:
            from config import GROUP_TEACHERS
            for group_id in GROUP_TEACHERS.keys():
                member_info = self.get_chat_member(group_id, user_id)
                if member_info and "user" in member_info:
                    name = self._extract_user_name(member_info["user"], user_id)
                    if name:
                        return name
        except Exception as e:
            logger.error(f"Error getting user name from groups: {e}")
        
        return None

    def get_group_name(self, chat_id: int) -> str:
        """دریافت نام گروه با مدیریت کش بهتر"""
        if not isinstance(chat_id, int):
            logger.error(f"Invalid chat_id type: {type(chat_id)}")
            return f"گروه نامعلوم"
            
        # بررسی کش
        if chat_id in self.group_names_cache:
            return self.group_names_cache[chat_id]
        
        url = f"{BASE_URL}/getChat"
        payload = {"chat_id": chat_id}
        
        response = self._make_request(url, payload)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                chat_info = result.get("result", {})
                group_name = chat_info.get("title", "").strip()
                if group_name:
                    self.group_names_cache[chat_id] = group_name
                    return group_name
        
        # نام پیش‌فرض
        default_name = f"گروه {chat_id}"
        self.group_names_cache[chat_id] = default_name
        return default_name

    def get_chat_member(self, chat_id: int, user_id: int) -> Optional[Dict]:
        """دریافت اطلاعات عضو گروه با مدیریت خطا"""
        if not isinstance(chat_id, int) or not isinstance(user_id, int):
            logger.error(f"Invalid parameter types: chat_id={type(chat_id)}, user_id={type(user_id)}")
            return None
            
        url = f"{BASE_URL}/getChatMember"
        payload = {"chat_id": chat_id, "user_id": user_id}
        
        response = self._make_request(url, payload)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                return result.get("result")
            else:
                logger.debug(f"User {user_id} not found in chat {chat_id}: {result.get('description', '')}")
        
        return None

    def is_user_authorized(self, user_id: int) -> bool:
        """بررسی مجوز کاربر با validation بهتر"""
        if not isinstance(user_id, int):
            logger.error(f"Invalid user_id type for authorization: {type(user_id)}")
            return False
            
        authorized = user_id in AUTHORIZED_USER_IDS or user_id in ADMIN_USER_IDS or user_id in HELPER_COACH_USER_IDS
        logger.debug(f"Authorization check for user {user_id}: {authorized}")
        return authorized

    def is_user_admin(self, user_id: int) -> bool:
        """بررسی اینکه آیا کاربر مدیر است یا نه"""
        if not isinstance(user_id, int):
            logger.error(f"Invalid user_id type for admin check: {type(user_id)}")
            return False
            
        is_admin = user_id in ADMIN_USER_IDS
        logger.debug(f"Admin check for user {user_id}: {is_admin}")
        return is_admin

    def is_user_coach(self, user_id: int) -> bool:
        """بررسی اینکه آیا کاربر مربی است یا نه"""
        if not isinstance(user_id, int):
            logger.error(f"Invalid user_id type for coach check: {type(user_id)}")
            return False
            
        is_coach = user_id in AUTHORIZED_USER_IDS
        logger.debug(f"Coach check for user {user_id}: {is_coach}")
        return is_coach

    def is_user_helper_coach(self, user_id: int) -> bool:
        """بررسی اینکه آیا کاربر کمک مربی است یا نه"""
        if not isinstance(user_id, int):
            logger.error(f"Invalid user_id type for helper coach check: {type(user_id)}")
            return False
            
        is_helper_coach = user_id in HELPER_COACH_USER_IDS
        logger.debug(f"Helper coach check for user {user_id}: {is_helper_coach}")
        return is_helper_coach

    def get_user_role(self, user_id: int) -> str:
        """دریافت نقش کاربر"""
        if self.is_user_admin(user_id):
            return "مدیر"
        elif self.is_user_coach(user_id):
            return "مربی"
        elif self.is_user_helper_coach(user_id):
            return "کمک مربی"
        else:
            return "قرآن‌آموز"

    def get_persian_date(self) -> str:
        """دریافت تاریخ فارسی با مدیریت خطا"""
        try:
            now = jdatetime.datetime.now()
            weekdays = {0: "شنبه", 1: "یکشنبه", 2: "دوشنبه", 3: "سه‌شنبه", 
                       4: "چهارشنبه", 5: "پنج‌شنبه", 6: "جمعه"}
            months = {1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر", 
                     5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان", 
                     9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"}
            
            weekday = weekdays.get(now.weekday(), "نامعلوم")
            month = months.get(now.month, "نامعلوم")
            
            return f"{weekday} {now.day} {month}"
        except Exception as e:
            logger.error(f"Error getting Persian date: {e}")
            return "تاریخ نامعلوم"

    def get_attendance_list(self) -> str:
        """تولید لیست حضور و غیاب با بهبودهای امنیتی"""
        if not self.users:
            logger.warning("Attendance list requested but user list is empty")
            return "❌ لیست کاربران خالی است!"
        
        try:
            current_time = f"{self.get_persian_date()} - {datetime.now().strftime('%H:%M')}"
            group_name = self.get_group_name(self.current_group_id) if self.current_group_id else "کلاس"
            
            text = f"📊 **لیست حضور و غیاب - {group_name}**\n"
            text += f"🕐 آخرین بروزرسانی: {current_time}\n\n"
            
            # نمایش لیست کاربران
            for i, user in enumerate(self.users, 1):
                if not isinstance(user, int):
                    logger.error(f"Invalid user type in list: {type(user)}")
                    continue
                    
                status = self.attendance_data.get(user, "در انتظار")
                if status not in self.valid_statuses:
                    logger.warning(f"Invalid status for user {user}: {status}")
                    status = "در انتظار"
                    
                icon = self.status_icons.get(status, "⏳")
                user_name = self.get_user_name(user)
                text += f"{i:2d}. {icon} {user_name} - {status}\n"
            
            # محاسبه آمار
            stats = self._calculate_attendance_stats()
            text += f"\n📈 **آمار:**\n"
            text += f"✅ حاضر: {stats['present']} | ⏰ تاخیر: {stats['late']}\n"
            text += f"❌ غایب: {stats['absent']} | 📄 موجه: {stats['justified']} | ⏳ در انتظار: {stats['pending']}"
            
            logger.info("Attendance list generated successfully")
            return text
            
        except Exception as e:
            logger.error(f"Error generating attendance list: {e}")
            return "❌ خطا در تولید لیست حضور و غیاب!"

    def _calculate_attendance_stats(self) -> Dict[str, int]:
        """محاسبه آمار حضور و غیاب"""
        try:
            total = len(self.users)
            present = sum(1 for status in self.attendance_data.values() if status == "حاضر")
            late = sum(1 for status in self.attendance_data.values() if status == "حضور با تاخیر")
            absent = sum(1 for status in self.attendance_data.values() if status == "غایب")
            justified = sum(1 for status in self.attendance_data.values() if status == "غیبت(موجه)")
            pending = total - len(self.attendance_data)
            
            return {
                'total': total,
                'present': present,
                'late': late,
                'absent': absent,
                'justified': justified,
                'pending': pending
            }
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            return {'total': 0, 'present': 0, 'late': 0, 'absent': 0, 'justified': 0, 'pending': 0}

    def get_main_menu(self, user_id: int) -> Dict[str, List]:
        """منوی اصلی با بررسی مجوز"""
        if not self.is_user_authorized(user_id):
            return {"inline_keyboard": [[{"text": "ℹ️ راهنما", "callback_data": "help"}]]}
        
        return {
            "inline_keyboard": [
                [{"text": "👥 مدیریت گروه‌ها", "callback_data": "group_menu"}],
                [{"text": "📊 مشاهده لیست حضور و غیاب", "callback_data": "view_attendance"}],
                [{"text": "✏️ ثبت حضور و غیاب سریع", "callback_data": "quick_attendance"}],
                [{"text": "🔄 پاک کردن داده‌ها", "callback_data": "clear_all"}],
                [{"text": "📈 آمار کلی", "callback_data": "statistics"}]
            ]
        }

    def get_quick_attendance_keyboard(self) -> Dict[str, List]:
        """کیبورد ثبت سریع حضور و غیاب"""
        if not self.users:
            logger.warning("Quick attendance keyboard requested but user list is empty")
            return {"inline_keyboard": [[{"text": "❌ لیست کاربران خالی است", "callback_data": "main_menu"}]]}
        
        try:
            keyboard = []
            for i, user in enumerate(self.users):
                if not isinstance(user, int):
                    logger.error(f"Invalid user type in keyboard: {type(user)}")
                    continue
                    
                status = self.attendance_data.get(user, "در انتظار")
                if status not in self.valid_statuses:
                    status = "در انتظار"
                    
                icon = self.status_icons.get(status, "⏳")
                user_name = self.get_user_name(user)
                keyboard.append([{"text": f"{icon} {user_name}", "callback_data": f"select_user_{i}"}])
            
            keyboard.extend([
                [{"text": "✅ همه حاضر", "callback_data": "all_present"}, 
                 {"text": "❌ همه غایب", "callback_data": "all_absent"}],
                [{"text": "🏠 برگشت به منو", "callback_data": "main_menu"}]
            ])
            
            logger.debug("Quick attendance keyboard generated successfully")
            return {"inline_keyboard": keyboard}
            
        except Exception as e:
            logger.error(f"Error generating quick attendance keyboard: {e}")
            return {"inline_keyboard": [[{"text": "❌ خطا در تولید کیبورد", "callback_data": "main_menu"}]]}

    def get_status_keyboard(self, user_index: int) -> Dict[str, List]:
        """کیبورد انتخاب وضعیت برای کاربر"""
        if not (0 <= user_index < len(self.users)):
            logger.error(f"Invalid user index: {user_index}")
            return {"inline_keyboard": [[{"text": "❌ خطا", "callback_data": "quick_attendance"}]]}
            
        try:
            user = self.users[user_index]
            user_name = self.get_user_name(user)
            
            return {
                "inline_keyboard": [
                    [{"text": f"✅ حاضر", "callback_data": f"set_status_{user_index}_حاضر"}, 
                     {"text": f"⏰ حضور با تاخیر", "callback_data": f"set_status_{user_index}_حضور با تاخیر"}],
                    [{"text": f"❌ غایب", "callback_data": f"set_status_{user_index}_غایب"}, 
                     {"text": f"📄 غیبت(موجه)", "callback_data": f"set_status_{user_index}_غیبت(موجه)"}],
                    [{"text": "🔙 برگشت", "callback_data": "quick_attendance"}]
                ]
            }
        except Exception as e:
            logger.error(f"Error generating status keyboard: {e}")
            return {"inline_keyboard": [[{"text": "❌ خطا", "callback_data": "quick_attendance"}]]}

    def validate_message_structure(self, message: Dict) -> bool:
        """اعتبارسنجی ساختار پیام"""
        required_keys = ["chat", "from"]
        for key in required_keys:
            if key not in message:
                logger.error(f"Missing required key in message: {key}")
                return False
        
        if "id" not in message["chat"] or "id" not in message["from"]:
            logger.error("Missing id in chat or from")
            return False
            
        return True

    def handle_message(self, message: Dict):
        """مدیریت پیام‌ها با اعتبارسنجی بهتر"""
        try:
            # اعتبارسنجی ساختار پیام
            if not self.validate_message_structure(message):
                return

            chat_id = message["chat"]["id"]
            user_id = message["from"]["id"]
            text = message.get("text", "").strip()
            
            logger.info(f"Processing message from user {user_id}: {text[:50]}...")

            # بررسی مجوز
            if not self.is_user_authorized(user_id) and text not in ["/start", "/group"]:
                logger.warning(f"Unauthorized access attempt from user {user_id}")
                self.send_message(chat_id, "❌ شما اجازه دسترسی به این بات را ندارید!")
                return

            # پردازش دستورات
            if text in ["/start", "شروع"]:
                self._handle_start_command(chat_id, user_id)
            elif text == "پنل مدیر":
                self._handle_admin_panel_command(chat_id, user_id)
            elif text == "پنل مربی":
                self._handle_coach_panel_command(chat_id, user_id)
            elif text == "پنل کمک مربی":
                self._handle_helper_coach_panel_command(chat_id, user_id)
            elif text == "پنل قرآن‌آموز":
                self._handle_quran_student_panel_command(chat_id, user_id)
            elif text == "منوی اصلی":
                self._handle_main_menu_command(chat_id, user_id)
            elif text == "راهنما":
                self._handle_help_command(chat_id)
            elif text == "خروج":
                self._handle_exit_command(chat_id)
            # مدیریت دکمه‌های پنل مربی
            elif text == "📊 مشاهده لیست حضور و غیاب":
                self._handle_view_attendance_from_coach_panel(chat_id, user_id)
            elif text == "✏️ ثبت حضور و غیاب سریع":
                self._handle_quick_attendance_from_coach_panel(chat_id, user_id)
            elif text == "📈 آمار کلی":
                self._handle_statistics_from_coach_panel(chat_id, user_id)
            elif text == "🔄 پاک کردن داده‌ها":
                self._handle_clear_all_from_coach_panel(chat_id, user_id)
            elif text == "🏠 برگشت به منو":
                self._handle_start_command(chat_id, user_id)
            # مدیریت دکمه‌های پنل کمک مربی
            elif text == "📊 مشاهده لیست حضور و غیاب" and self.is_user_helper_coach(user_id):
                self._handle_view_attendance_from_helper_coach_panel(chat_id, user_id)
            elif text == "✏️ ثبت حضور و غیاب سریع" and self.is_user_helper_coach(user_id):
                self._handle_quick_attendance_from_helper_coach_panel(chat_id, user_id)
            elif text == "📈 آمار کلی" and self.is_user_helper_coach(user_id):
                self._handle_statistics_from_helper_coach_panel(chat_id, user_id)
            elif text == "🔄 پاک کردن داده‌ها" and self.is_user_helper_coach(user_id):
                self._handle_clear_all_from_helper_coach_panel(chat_id, user_id)
            # مدیریت دکمه‌های پنل قرآن‌آموز
            elif text == "📊 مشاهده لیست حضور و غیاب" and not self.is_user_authorized(user_id):
                self._handle_view_attendance_from_quran_student_panel(chat_id, user_id)
            elif text == "📈 آمار کلی" and not self.is_user_authorized(user_id):
                self._handle_statistics_from_quran_student_panel(chat_id, user_id)
            else:
                logger.debug(f"Unknown command: {text}")

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def _handle_start_command(self, chat_id: int, user_id: int):
        """مدیریت دستور شروع"""
        try:
            user_role = self.get_user_role(user_id)
            welcome_text = f"""🎯 **بات حضور و غیاب قرآن‌آموزان**

سلام {user_role} عزیز! 👋
به بات حضور و غیاب خوش آمدید.

🕐 زمان: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد کاربران فعلی: {len(self.users)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
            
            # نمایش دکمه‌های مناسب بر اساس نقش کاربر
            if self.is_user_admin(user_id):
                # دکمه‌های مدیر
                keyboard = {
                    "keyboard": [
                        [{"text": "شروع"}, {"text": "خروج"}],
                        [{"text": "پنل مدیر"}]
                    ], 
                    "resize_keyboard": True
                }
            elif self.is_user_coach(user_id):
                # دکمه‌های مربی
                keyboard = {
                    "keyboard": [
                        [{"text": "شروع"}, {"text": "خروج"}],
                        [{"text": "پنل مربی"}]
                    ], 
                    "resize_keyboard": True
                }
            elif self.is_user_helper_coach(user_id):
                # دکمه‌های کمک مربی
                keyboard = {
                    "keyboard": [
                        [{"text": "شروع"}, {"text": "خروج"}],
                        [{"text": "پنل کمک مربی"}]
                    ], 
                    "resize_keyboard": True
                }
            else:
                # دکمه‌های قرآن‌آموز
                keyboard = {
                    "keyboard": [
                        [{"text": "شروع"}, {"text": "خروج"}],
                        [{"text": "پنل قرآن‌آموز"}]
                    ], 
                    "resize_keyboard": True
                }
            
            self.send_message(chat_id, welcome_text, keyboard)
        except Exception as e:
            logger.error(f"Error in start command: {e}")

    def _handle_main_menu_command(self, chat_id: int, user_id: int):
        """مدیریت دستور منوی اصلی"""
        try:
            welcome_text = f"""🏠 **منوی اصلی**

🕐 زمان: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد کاربران فعلی: {len(self.users)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
            self.send_message(chat_id, welcome_text, self.get_main_menu(user_id))
        except Exception as e:
            logger.error(f"Error in main menu command: {e}")

    def _handle_help_command(self, chat_id: int):
        """مدیریت دستور راهنما"""
        help_text = """📖 **راهنمای استفاده از بات**

🔹 **برای مدیر و مربیان:**
- ابتدا گروه‌های خود را مدیریت کنید
- از منوی "مدیریت گروه‌ها" استفاده کنید
- برای هر گروه می‌توانید حضور و غیاب ثبت کنید

🔹 **برای قرآن‌آموزان:**
- در گروه از دستور `/عضو` استفاده کنید
- فقط لیست حضور و غیاب را مشاهده خواهید کرد

🔹 **نحوه کار:**
1️⃣ ربات را به گروه اضافه کنید
2️⃣ اعضا با `/عضو` ثبت نام کنند
3️⃣ مربیان از بخش خصوصی حضور و غیاب ثبت کنند"""
        self.send_message(chat_id, help_text)

    def _handle_exit_command(self, chat_id: int):
        """مدیریت دستور خروج"""
        self.send_message(chat_id, "👋 با تشکر از استفاده شما از بات حضور و غیاب. موفق باشید! 🌟")

    def _handle_admin_panel_command(self, chat_id: int, user_id: int):
        """مدیریت پنل مدیر"""
        try:
            welcome_text = f"""⚙️ **پنل مدیر**

سلام مدیر عزیز! 👋
به پنل مدیریت خوش آمدید.

🕐 زمان: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد کاربران فعلی: {len(self.users)}

لطفاً یکی از گزینه‌های مدیریتی زیر را انتخاب کنید:"""
            
            # ارسال منوی اصلی به جای کیبورد جدید
            self.send_message(chat_id, welcome_text, self.get_main_menu(user_id))
        except Exception as e:
            logger.error(f"Error in admin panel command: {e}")

    def _handle_coach_panel_command(self, chat_id: int, user_id: int):
        """مدیریت پنل مربی"""
        try:
            welcome_text = f"""👨‍🏫 **پنل مربی**

سلام مربی عزیز! 👋
به پنل مربی خوش آمدید.

🕐 زمان: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد کاربران فعلی: {len(self.users)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
            
            keyboard = {
                "keyboard": [
                    [{"text": "📊 مشاهده لیست حضور و غیاب"}, {"text": "✏️ ثبت حضور و غیاب سریع"}],
                    [{"text": "📈 آمار کلی"}, {"text": "🔄 پاک کردن داده‌ها"}],
                    [{"text": "🏠 برگشت به منو"}, {"text": "خروج"}]
                ], 
                "resize_keyboard": True
            }
            
            self.send_message(chat_id, welcome_text, keyboard)
        except Exception as e:
            logger.error(f"Error in coach panel command: {e}")

    def _handle_helper_coach_panel_command(self, chat_id: int, user_id: int):
        """مدیریت پنل کمک مربی"""
        try:
            welcome_text = f"""👨‍🏫 **پنل کمک مربی**

سلام کمک مربی عزیز! 👋
به پنل کمک مربی خوش آمدید.

🕐 زمان: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد کاربران فعلی: {len(self.users)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
            
            keyboard = {
                "keyboard": [
                    [{"text": "📊 مشاهده لیست حضور و غیاب"}, {"text": "✏️ ثبت حضور و غیاب سریع"}],
                    [{"text": "📈 آمار کلی"}, {"text": "🔄 پاک کردن داده‌ها"}],
                    [{"text": "🏠 برگشت به منو"}, {"text": "خروج"}]
                ], 
                "resize_keyboard": True
            }
            
            self.send_message(chat_id, welcome_text, keyboard)
        except Exception as e:
            logger.error(f"Error in helper coach panel command: {e}")

    def _handle_quran_student_panel_command(self, chat_id: int, user_id: int):
        """مدیریت پنل قرآن‌آموز"""
        try:
            welcome_text = f"""📖 **پنل قرآن‌آموز**

سلام قرآن‌آموز عزیز! 👋
به پنل قرآن‌آموز خوش آمدید.

🕐 زمان: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}
👥 تعداد کاربران فعلی: {len(self.users)}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"""
            
            keyboard = {
                "keyboard": [
                    [{"text": "📊 مشاهده لیست حضور و غیاب"}],
                    [{"text": "📈 آمار کلی"}],
                    [{"text": "🏠 برگشت به منو"}, {"text": "خروج"}]
                ], 
                "resize_keyboard": True
            }
            
            self.send_message(chat_id, welcome_text, keyboard)
        except Exception as e:
            logger.error(f"Error in quran student panel command: {e}")

    def _handle_view_attendance_from_coach_panel(self, chat_id: int, user_id: int):
        """مدیریت مشاهده لیست حضور و غیاب از پنل مربی"""
        try:
            attendance_list = self.get_attendance_list()
            self.send_message(chat_id, attendance_list)
        except Exception as e:
            logger.error(f"Error in view attendance from coach panel: {e}")

    def _handle_quick_attendance_from_coach_panel(self, chat_id: int, user_id: int):
        """مدیریت ثبت سریع حضور و غیاب از پنل مربی"""
        try:
            welcome_text = "✏️ **ثبت سریع حضور و غیاب**\n\nلطفاً کاربر مورد نظر را انتخاب کنید:"
            self.send_message(chat_id, welcome_text, self.get_quick_attendance_keyboard())
        except Exception as e:
            logger.error(f"Error in quick attendance from coach panel: {e}")

    def _handle_statistics_from_coach_panel(self, chat_id: int, user_id: int):
        """مدیریت آمار کلی از پنل مربی"""
        try:
            stats = self._calculate_attendance_stats()
            stats_text = f"""📈 **آمار کلی حضور و غیاب**

✅ حاضر: {stats.get('حاضر', 0)} نفر
⏰ حضور با تاخیر: {stats.get('حضور با تاخیر', 0)} نفر
❌ غایب: {stats.get('غایب', 0)} نفر
📄 غیبت(موجه): {stats.get('غیبت(موجه)', 0)} نفر
⏳ در انتظار: {stats.get('در انتظار', 0)} نفر

📊 **مجموع**: {len(self.users)} نفر"""
            self.send_message(chat_id, stats_text)
        except Exception as e:
            logger.error(f"Error in statistics from coach panel: {e}")

    def _handle_clear_all_from_coach_panel(self, chat_id: int, user_id: int):
        """مدیریت پاک کردن داده‌ها از پنل مربی"""
        try:
            self.attendance_data.clear()
            self.user_states.clear()
            self.clear_cache()
            self.send_message(chat_id, "🔄 **داده‌ها پاک شدند**\n\nتمام اطلاعات حضور و غیاب پاک شد.")
        except Exception as e:
            logger.error(f"Error in clear all from coach panel: {e}")

    def _handle_view_attendance_from_helper_coach_panel(self, chat_id: int, user_id: int):
        """مدیریت مشاهده لیست حضور و غیاب از پنل کمک مربی"""
        try:
            attendance_list = self.get_attendance_list()
            self.send_message(chat_id, attendance_list)
        except Exception as e:
            logger.error(f"Error in view attendance from helper coach panel: {e}")

    def _handle_quick_attendance_from_helper_coach_panel(self, chat_id: int, user_id: int):
        """مدیریت ثبت سریع حضور و غیاب از پنل کمک مربی"""
        try:
            welcome_text = "✏️ **ثبت سریع حضور و غیاب**\n\nلطفاً کاربر مورد نظر را انتخاب کنید:"
            self.send_message(chat_id, welcome_text, self.get_quick_attendance_keyboard())
        except Exception as e:
            logger.error(f"Error in quick attendance from helper coach panel: {e}")

    def _handle_statistics_from_helper_coach_panel(self, chat_id: int, user_id: int):
        """مدیریت آمار کلی از پنل کمک مربی"""
        try:
            stats = self._calculate_attendance_stats()
            stats_text = f"""📈 **آمار کلی حضور و غیاب**

✅ حاضر: {stats.get('حاضر', 0)} نفر
⏰ حضور با تاخیر: {stats.get('حضور با تاخیر', 0)} نفر
❌ غایب: {stats.get('غایب', 0)} نفر
📄 غیبت(موجه): {stats.get('غیبت(موجه)', 0)} نفر
⏳ در انتظار: {stats.get('در انتظار', 0)} نفر

📊 **مجموع**: {len(self.users)} نفر"""
            self.send_message(chat_id, stats_text)
        except Exception as e:
            logger.error(f"Error in statistics from helper coach panel: {e}")

    def _handle_clear_all_from_helper_coach_panel(self, chat_id: int, user_id: int):
        """مدیریت پاک کردن داده‌ها از پنل کمک مربی"""
        try:
            self.attendance_data.clear()
            self.user_states.clear()
            self.clear_cache()
            self.send_message(chat_id, "🔄 **داده‌ها پاک شدند**\n\nتمام اطلاعات حضور و غیاب پاک شد.")
        except Exception as e:
            logger.error(f"Error in clear all from helper coach panel: {e}")

    def _handle_view_attendance_from_quran_student_panel(self, chat_id: int, user_id: int):
        """مدیریت مشاهده لیست حضور و غیاب از پنل قرآن‌آموز"""
        try:
            attendance_list = self.get_attendance_list()
            self.send_message(chat_id, attendance_list)
        except Exception as e:
            logger.error(f"Error in view attendance from quran student panel: {e}")

    def _handle_statistics_from_quran_student_panel(self, chat_id: int, user_id: int):
        """مدیریت آمار کلی از پنل قرآن‌آموز"""
        try:
            stats = self._calculate_attendance_stats()
            stats_text = f"""📈 **آمار کلی حضور و غیاب**

✅ حاضر: {stats.get('حاضر', 0)} نفر
⏰ حضور با تاخیر: {stats.get('حضور با تاخیر', 0)} نفر
❌ غایب: {stats.get('غایب', 0)} نفر
📄 غیبت(موجه): {stats.get('غیبت(موجه)', 0)} نفر
⏳ در انتظار: {stats.get('در انتظار', 0)} نفر

📊 **مجموع**: {len(self.users)} نفر"""
            self.send_message(chat_id, stats_text)
        except Exception as e:
            logger.error(f"Error in statistics from quran student panel: {e}")

    def validate_callback_structure(self, callback: Dict) -> bool:
        """اعتبارسنجی ساختار callback"""
        required_keys = ["message", "from", "data", "id"]
        for key in required_keys:
            if key not in callback:
                logger.error(f"Missing required key in callback: {key}")
                return False
        
        message_keys = ["chat", "message_id"]
        for key in message_keys:
            if key not in callback["message"]:
                logger.error(f"Missing required key in callback message: {key}")
                return False
                
        return True

    def handle_callback(self, callback: Dict):
        """مدیریت callback query ها با اعتبارسنجی بهتر"""
        try:
            # اعتبارسنجی ساختار
            if not self.validate_callback_structure(callback):
                return

            chat_id = callback["message"]["chat"]["id"]
            message_id = callback["message"]["message_id"]
            user_id = callback["from"]["id"]
            data = callback["data"]
            callback_query_id = callback["id"]
            
            logger.info(f"Processing callback from user {user_id}: {data}")

            # بررسی مجوز
            if not self.is_user_authorized(user_id):
                self.answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
                return

            # مسیریابی callback ها
            self._route_callback(chat_id, message_id, user_id, data, callback_query_id)

        except Exception as e:
            logger.error(f"Error handling callback: {e}")

    def _route_callback(self, chat_id: int, message_id: int, user_id: int, data: str, callback_query_id: str):
        """مسیریابی callback query ها"""
        try:
            if data == "main_menu":
                self._handle_main_menu_callback(chat_id, message_id, user_id, callback_query_id)
            elif data == "view_attendance":
                self._handle_view_attendance_callback(chat_id, message_id, callback_query_id)
            elif data == "quick_attendance":
                self._handle_quick_attendance_callback(chat_id, message_id, callback_query_id)
            elif data.startswith("select_user_"):
                self._handle_select_user_callback(chat_id, message_id, data, callback_query_id)
            elif data.startswith("set_status_"):
                self._handle_set_status_callback(chat_id, message_id, data, callback_query_id)
            elif data == "all_present":
                self._handle_all_present_callback(chat_id, message_id, callback_query_id)
            elif data == "all_absent":
                self._handle_all_absent_callback(chat_id, message_id, callback_query_id)
            elif data == "clear_all":
                self._handle_clear_all_callback(chat_id, message_id, callback_query_id)
            elif data == "statistics":
                self._handle_statistics_callback(chat_id, message_id, callback_query_id)
            else:
                logger.warning(f"Unknown callback data: {data}")
                self.answer_callback_query(callback_query_id, "❌ دستور نامعلوم!")
        except Exception as e:
            logger.error(f"Error routing callback {data}: {e}")
            self.answer_callback_query(callback_query_id, "❌ خطا در پردازش!")

    def _handle_main_menu_callback(self, chat_id: int, message_id: int, user_id: int, callback_query_id: str):
        """مدیریت callback منوی اصلی"""
        self.edit_message(
            chat_id, message_id, 
            "🏠 **منوی اصلی**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", 
            self.get_main_menu(user_id)
        )
        self.answer_callback_query(callback_query_id)

    def _handle_view_attendance_callback(self, chat_id: int, message_id: int, callback_query_id: str):
        """مدیریت callback مشاهده لیست حضور و غیاب"""
        if not self.users:
            self.edit_message(
                chat_id, message_id,
                "❌ هیچ گروهی انتخاب نشده است.\nابتدا از منوی گروه‌ها یک گروه انتخاب کنید.",
                {"inline_keyboard": [[{"text": "👥 مدیریت گروه‌ها", "callback_data": "group_menu"}]]}
            )
            self.answer_callback_query(callback_query_id, "ابتدا گروه انتخاب کنید")
            return
            
        text = self.get_attendance_list()
        keyboard = {"inline_keyboard": [
            [{"text": "🔄 بروزرسانی", "callback_data": "view_attendance"}],
            [{"text": "✏️ ثبت سریع", "callback_data": "quick_attendance"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]}
        self.edit_message(chat_id, message_id, text, keyboard)
        self.answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")

    def _handle_quick_attendance_callback(self, chat_id: int, message_id: int, callback_query_id: str):
        """مدیریت callback ثبت سریع حضور و غیاب"""
        if not self.users:
            self.edit_message(
                chat_id, message_id,
                "❌ هیچ گروهی انتخاب نشده است.\nابتدا از منوی گروه‌ها یک گروه انتخاب کنید.",
                {"inline_keyboard": [[{"text": "👥 مدیریت گروه‌ها", "callback_data": "group_menu"}]]}
            )
            self.answer_callback_query(callback_query_id, "ابتدا گروه انتخاب کنید")
            return
            
        self.edit_message(
            chat_id, message_id, 
            "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:", 
            self.get_quick_attendance_keyboard()
        )
        self.answer_callback_query(callback_query_id)

    def _handle_select_user_callback(self, chat_id: int, message_id: int, data: str, callback_query_id: str):
        """مدیریت callback انتخاب کاربر"""
        try:
            user_index = int(data.split("_")[-1])
            if not (0 <= user_index < len(self.users)):
                self.answer_callback_query(callback_query_id, "❌ کاربر یافت نشد!")
                return
                
            user = self.users[user_index]
            user_name = self.get_user_name(user)
            current_status = self.attendance_data.get(user, "در انتظار")
            
            self.edit_message(
                chat_id, message_id, 
                f"👤 **{user_name}**\nوضعیت فعلی: {current_status}\n\nوضعیت جدید را انتخاب کنید:", 
                self.get_status_keyboard(user_index)
            )
            self.answer_callback_query(callback_query_id, f"انتخاب {user_name}")
        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing user index: {e}")
            self.answer_callback_query(callback_query_id, "❌ خطا در انتخاب کاربر!")

    def _handle_set_status_callback(self, chat_id: int, message_id: int, data: str, callback_query_id: str):
        """مدیریت callback تنظیم وضعیت کاربر"""
        try:
            parts = data.split("_", 3)
            if len(parts) < 4:
                self.answer_callback_query(callback_query_id, "❌ خطا در پردازش!")
                return
                
            user_index = int(parts[2])
            status = parts[3]
            
            # اعتبارسنجی
            if not (0 <= user_index < len(self.users)):
                self.answer_callback_query(callback_query_id, "❌ کاربر یافت نشد!")
                return
                
            if status not in self.valid_statuses:
                logger.error(f"Invalid status: {status}")
                self.answer_callback_query(callback_query_id, "❌ وضعیت نامعتبر!")
                return
                
            user = self.users[user_index]
            user_name = self.get_user_name(user)
            self.attendance_data[user] = status
            
            self.edit_message(
                chat_id, message_id, 
                "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:", 
                self.get_quick_attendance_keyboard()
            )
            self.answer_callback_query(callback_query_id, f"✅ {user_name} - {status}")
            
        except (ValueError, IndexError) as e:
            logger.error(f"Error setting status: {e}")
            self.answer_callback_query(callback_query_id, "❌ خطا در تنظیم وضعیت!")

    def _handle_all_present_callback(self, chat_id: int, message_id: int, callback_query_id: str):
        """مدیریت callback همه حاضر"""
        if not self.users:
            self.answer_callback_query(callback_query_id, "❌ لیست کاربران خالی است!")
            return
            
        for user in self.users:
            self.attendance_data[user] = "حاضر"
            
        self.edit_message(
            chat_id, message_id, 
            "✅ **همه کاربران حاضر علامت گذاری شدند**", 
            {"inline_keyboard": [
                [{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}], 
                [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
            ]}
        )
        self.answer_callback_query(callback_query_id, "✅ همه حاضر شدند")

    def _handle_all_absent_callback(self, chat_id: int, message_id: int, callback_query_id: str):
        """مدیریت callback همه غایب"""
        if not self.users:
            self.answer_callback_query(callback_query_id, "❌ لیست کاربران خالی است!")
            return
            
        for user in self.users:
            self.attendance_data[user] = "غایب"
            
        self.edit_message(
            chat_id, message_id, 
            "❌ **همه کاربران غایب علامت گذاری شدند**", 
            {"inline_keyboard": [
                [{"text": "📊 مشاهده لیست", "callback_data": "view_attendance"}], 
                [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
            ]}
        )
        self.answer_callback_query(callback_query_id, "❌ همه غایب شدند")

    def _handle_clear_all_callback(self, chat_id: int, message_id: int, callback_query_id: str):
        """مدیریت callback پاک کردن همه داده‌ها"""
        self.attendance_data.clear()
        logger.info("Attendance data cleared")
        
        self.edit_message(
            chat_id, message_id, 
            "🗑️ **داده‌های حضور و غیاب پاک شدند**", 
            {"inline_keyboard": [[{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]]}
        )
        self.answer_callback_query(callback_query_id, "🗑️ داده‌ها پاک شدند")

    def _handle_statistics_callback(self, chat_id: int, message_id: int, callback_query_id: str):
        """مدیریت callback آمار"""
        if not self.users:
            self.edit_message(
                chat_id, message_id,
                "❌ هیچ گروهی انتخاب نشده است.\nابتدا از منوی گروه‌ها یک گروه انتخاب کنید.",
                {"inline_keyboard": [[{"text": "👥 مدیریت گروه‌ها", "callback_data": "group_menu"}]]}
            )
            self.answer_callback_query(callback_query_id, "ابتدا گروه انتخاب کنید")
            return
            
        try:
            stats = self._calculate_attendance_stats()
            group_name = self.get_group_name(self.current_group_id) if self.current_group_id else "کلاس"
            
            # محافظت از تقسیم بر صفر
            total = stats['total'] if stats['total'] > 0 else 1
            
            stats_text = f"""📈 **آمار کلی حضور و غیاب - {group_name}**

👥 کل کاربران: {stats['total']}
✅ حاضر: {stats['present']} ({stats['present']/total*100:.1f}%)
⏰ حضور با تاخیر: {stats['late']} ({stats['late']/total*100:.1f}%)
❌ غایب: {stats['absent']} ({stats['absent']/total*100:.1f}%)
📄 غیبت(موجه): {stats['justified']} ({stats['justified']/total*100:.1f}%)
⏳ در انتظار: {stats['pending']} ({stats['pending']/total*100:.1f}%)

🕐 زمان آخرین بروزرسانی: {self.get_persian_date()} - {datetime.now().strftime("%H:%M")}"""

            self.edit_message(
                chat_id, message_id, stats_text, 
                {"inline_keyboard": [
                    [{"text": "🔄 بروزرسانی آمار", "callback_data": "statistics"}], 
                    [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
                ]}
            )
            self.answer_callback_query(callback_query_id, "📊 آمار بروزرسانی شد")
            
        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
            self.edit_message(
                chat_id, message_id, 
                "❌ خطا در تولید آمار!", 
                {"inline_keyboard": [[{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]]}
            )
            self.answer_callback_query(callback_query_id, "❌ خطا در آمار!")

    def set_users(self, users: List[int], group_id: Optional[int] = None):
        """تنظیم لیست کاربران با اعتبارسنجی"""
        try:
            # اعتبارسنجی ورودی
            if not isinstance(users, list):
                logger.error(f"Invalid users type: {type(users)}")
                return False
                
            # فیلتر کردن user_id های معتبر
            valid_users = []
            for user in users:
                if isinstance(user, int) and user > 0:
                    valid_users.append(user)
                else:
                    logger.warning(f"Invalid user_id filtered out: {user}")
            
            self.users = valid_users
            self.current_group_id = group_id
            
            # پاک کردن داده‌های قدیمی حضور و غیاب برای کاربران غیرمعتبر
            invalid_attendance_users = [user for user in self.attendance_data.keys() if user not in valid_users]
            for user in invalid_attendance_users:
                del self.attendance_data[user]
                logger.info(f"Removed attendance data for invalid user: {user}")
            
            logger.info(f"Users set successfully: {len(valid_users)} users for group {group_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting users: {e}")
            return False

    def add_user(self, user_id: int) -> bool:
        """اضافه کردن کاربر جدید با اعتبارسنجی"""
        try:
            if not isinstance(user_id, int) or user_id <= 0:
                logger.error(f"Invalid user_id: {user_id}")
                return False
                
            if user_id not in self.users:
                self.users.append(user_id)
                logger.info(f"User {user_id} added successfully")
                return True
            else:
                logger.debug(f"User {user_id} already exists")
                return False
                
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False

    def remove_user(self, user_id: int) -> bool:
        """حذف کاربر با اعتبارسنجی"""
        try:
            if not isinstance(user_id, int):
                logger.error(f"Invalid user_id type: {type(user_id)}")
                return False
                
            if user_id in self.users:
                self.users.remove(user_id)
                # حذف داده‌های حضور و غیاب کاربر
                if user_id in self.attendance_data:
                    del self.attendance_data[user_id]
                # حذف از کش نام‌ها
                if user_id in self.user_names_cache:
                    del self.user_names_cache[user_id]
                    
                logger.info(f"User {user_id} removed successfully")
                return True
            else:
                logger.debug(f"User {user_id} not found for removal")
                return False
                
        except Exception as e:
            logger.error(f"Error removing user {user_id}: {e}")
            return False

    def clear_cache(self):
        """پاک کردن کش‌ها"""
        try:
            self.user_names_cache.clear()
            self.group_names_cache.clear()
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def get_user_status(self, user_id: int) -> Optional[str]:
        """دریافت وضعیت کاربر"""
        if not isinstance(user_id, int):
            logger.error(f"Invalid user_id type: {type(user_id)}")
            return None
            
        return self.attendance_data.get(user_id, "در انتظار")

    def set_user_status(self, user_id: int, status: str) -> bool:
        """تنظیم وضعیت کاربر"""
        try:
            if not isinstance(user_id, int):
                logger.error(f"Invalid user_id type: {type(user_id)}")
                return False
                
            if status not in self.valid_statuses:
                logger.error(f"Invalid status: {status}")
                return False
                
            if user_id not in self.users:
                logger.warning(f"User {user_id} not in users list")
                return False
                
            self.attendance_data[user_id] = status
            logger.info(f"Status set for user {user_id}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting status for user {user_id}: {e}")
            return False

    def export_attendance_data(self) -> Dict[str, Any]:
        """صادرات داده‌های حضور و غیاب"""
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "persian_date": self.get_persian_date(),
                "group_id": self.current_group_id,
                "group_name": self.get_group_name(self.current_group_id) if self.current_group_id else None,
                "users_count": len(self.users),
                "attendance_data": {},
                "statistics": self._calculate_attendance_stats()
            }
            
            # تبدیل داده‌های حضور و غیاب به فرمت قابل خواندن
            for user_id, status in self.attendance_data.items():
                user_name = self.get_user_name(user_id)
                export_data["attendance_data"][str(user_id)] = {
                    "name": user_name,
                    "status": status
                }
            
            logger.info("Attendance data exported successfully")
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting attendance data: {e}")
            return {}