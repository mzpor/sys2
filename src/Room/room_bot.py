import json
import os
import requests
import logging
import time
import datetime
import jdatetime

"""

{
  "bot_token": "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3",
  "admin_id": "1114227010",
  "teacher_ids": ["574330749", "1775811194"],
  "data_file": "1.json",
  "attendance_days": ["Thursday"],
  "welcome_message": "🎉 به ربات مدیریت روم خوش آمدید!\n\nدستورات:\n👥 /عضو - ثبت در گروه\n📋 /لیست - مشاهده لیست اعضا"
}
"""
# تنظیم لاگینگ
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# کلاس کانفیگ
class Config:
    def __init__(self, config_file='config.json'):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                self.BOT_TOKEN = config_data.get('bot_token', '')
                self.BASE_URL = f"https://tapi.bale.ai/bot{self.BOT_TOKEN}"
                self.DATA_FILE = config_data.get('data_file', 'room_data.json')
                self.ADMIN_ID = config_data.get('admin_id', '')
                self.TEACHER_IDS = config_data.get('teacher_ids', [])
                self.ATTENDANCE_DAYS = config_data.get('attendance_days', ['Thursday'])
                self.WELCOME_MESSAGE = config_data.get('welcome_message', '🎉 به ربات مدیریت روم خوش آمدید!')
                logging.info("کانفیگ با موفقیت بارگذاری شد.")
        except Exception as e:
            logging.error(f"خطا در بارگذاری کانفیگ: {e}")
            # مقادیر پیش‌فرض
            self.BOT_TOKEN = '1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3'
            self.BASE_URL = f"https://tapi.bale.ai/bot{self.BOT_TOKEN}"
            self.DATA_FILE = 'room_data.json'
            self.ADMIN_ID = '1114227010'
            self.TEACHER_IDS = ['574330749', '1775811194']
            self.ATTENDANCE_DAYS = ['Thursday']
            self.WELCOME_MESSAGE = '🎉 به ربات مدیریت روم خوش آمدید!'
            logging.warning("از مقادیر پیش‌فرض برای کانفیگ استفاده می‌شود.")

# کلاس اصلی ربات
class RoomBot:
    def __init__(self, config):
        self.config = config
        self.data = self.load_data()
        logging.info("ربات مدیریت روم راه‌اندازی شد.")
    
    def load_data(self):
        """بارگذاری داده‌ها از فایل"""
        if os.path.exists(self.config.DATA_FILE):
            try:
                with open(self.config.DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"خطا در بارگذاری داده‌ها: {e}")
                return self.initialize_data()
        else:
            return self.initialize_data()
    
    def initialize_data(self):
        """مقداردهی اولیه داده‌ها"""
        return {
            "members": {},
            "attendance": {}
        }
    
    def save_data(self):
        """ذخیره داده‌ها در فایل"""
        try:
            with open(self.config.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"خطا در ذخیره داده‌ها: {e}")
    
    def send_message(self, chat_id, text, reply_markup=None):
        """ارسال پیام به کاربر"""
        url = f"{self.config.BASE_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        
        try:
            response = requests.post(url, json=payload)
            return response.json()
        except Exception as e:
            logging.error(f"خطا در ارسال پیام: {e}")
            return None
    
    def get_jalali_date(self):
        """دریافت تاریخ جلالی"""
        now = datetime.datetime.now()
        j_date = jdatetime.date.fromgregorian(date=now.date())
        return j_date.strftime("%Y/%m/%d")
    
    def get_week_day(self):
        """دریافت روز هفته"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[datetime.datetime.now().weekday()]
    
    def is_attendance_day(self):
        """بررسی روز حضور و غیاب"""
        return self.get_week_day() in self.config.ATTENDANCE_DAYS
    
    def get_user_name(self, user):
        """دریافت نام کاربر"""
        if user.get('first_name') and user.get('last_name'):
            return f"{user['first_name']} {user['last_name']}"
        elif user.get('first_name'):
            return user['first_name']
        elif user.get('username'):
            return user['username']
        else:
            return "کاربر ناشناس"
    
    def is_admin(self, user_id):
        """بررسی ادمین بودن کاربر"""
        return str(user_id) == self.config.ADMIN_ID
    
    def is_teacher(self, user_id):
        """بررسی مربی بودن کاربر"""
        return str(user_id) in self.config.TEACHER_IDS
    
    def register_member(self, chat_id, user):
        """ثبت عضو جدید"""
        user_id = str(user['id'])
        user_name = self.get_user_name(user)
        
        if "members" not in self.data:
            self.data["members"] = {}
            
        if chat_id not in self.data["members"]:
            self.data["members"][chat_id] = {}
        
        if user_id not in self.data["members"][chat_id]:
            self.data["members"][chat_id][user_id] = {
                "name": user_name,
                "join_date": self.get_jalali_date(),
                "is_admin": self.is_admin(user_id)
            }
            self.save_data()
            return True
        return False
    
    def get_members_list(self, chat_id):
        """دریافت لیست اعضا"""
        if "members" not in self.data or chat_id not in self.data["members"]:
            return "📋 لیست اعضا\n\n👥 هیچ عضوی ثبت نشده است."
        
        members = self.data["members"].get(chat_id, {})
        admins = []
        regular_members = []
        
        for user_id, info in members.items():
            if info.get("is_admin", False):
                admins.append(f"• {info['name']}")
            else:
                regular_members.append(f"{len(regular_members) + 1}. {info['name']}")
        
        message = f"📋 لیست اعضا\n📅 {self.get_jalali_date()}\n\n"
        
        if admins:
            message += "👑 ادمین‌ها:\n" + "\n".join(admins) + "\n\n"
        
        if regular_members:
            message += "👥 اعضا:\n" + "\n".join(regular_members) + "\n\n"
        else:
            message += "👥 هیچ عضوی ثبت نشده است.\n\n"
        
        message += f"📊 آمار:\n👑 ادمین‌ها: {len(admins)}\n👥 اعضا: {len(regular_members)}"
        
        return message
    
    def create_attendance_keyboard(self, chat_id):
        """ایجاد کیبورد حضور و غیاب"""
        if "members" not in self.data or chat_id not in self.data["members"]:
            return None
        
        members = self.data["members"].get(chat_id, {})
        keyboard = []
        
        for user_id, info in members.items():
            if not info.get("is_admin", False):
                row = [
                    {"text": f"✅ حاضر", "callback_data": f"attendance:{user_id}:present:{chat_id}"},
                    {"text": f"⏱ تاخیر", "callback_data": f"attendance:{user_id}:late:{chat_id}"},
                    {"text": f"❌ غایب", "callback_data": f"attendance:{user_id}:absent:{chat_id}"},
                    {"text": f"📝 موجه", "callback_data": f"attendance:{user_id}:excused:{chat_id}"}
                ]
                keyboard.append([{"text": f"👤 {info['name']}", "callback_data": f"info:{user_id}"}])
                keyboard.append(row)
                keyboard.append([{"text": "➖➖➖➖➖➖➖➖➖➖", "callback_data": "separator"}])
        
        return {"inline_keyboard": keyboard}
    
    def record_attendance(self, chat_id, user_id, status, group_id):
        """ثبت حضور و غیاب"""
        today = self.get_jalali_date()
        
        if "attendance" not in self.data:
            self.data["attendance"] = {}
        
        if group_id not in self.data["attendance"]:
            self.data["attendance"][group_id] = {}
        
        if today not in self.data["attendance"][group_id]:
            self.data["attendance"][group_id][today] = {}
        
        user_name = self.data["members"][group_id][user_id]["name"]
        self.data["attendance"][group_id][today][user_id] = status
        self.save_data()
        
        status_text = {
            "present": "حاضر",
            "late": "با تاخیر",
            "absent": "غایب",
            "excused": "غیبت موجه"
        }.get(status, status)
        
        return f"📋 حضور و غیاب: {user_name} - {status_text}\n📅 {today}"
    
    def handle_message(self, message):
        """پردازش پیام‌های دریافتی"""
        if "message" not in message:
            return
        
        msg = message["message"]
        chat_id = str(msg["chat"]["id"])
        user = msg.get("from", {})
        user_id = str(user.get("id", ""))
        text = msg.get("text", "")
        
        # پردازش دستورات
        if text == "/start":
            welcome_message = self.config.WELCOME_MESSAGE
            if self.is_teacher(user_id) and msg["chat"]["type"] == "private":
                welcome_message += "\n📊 /حضورغیاب - شروع فرآیند ثبت حضور و غیاب"
            self.send_message(chat_id, welcome_message)
        
        elif text == "/عضو":
            if self.register_member(chat_id, user):
                self.send_message(chat_id, f"✅ {self.get_user_name(user)} عزیز، شما با موفقیت در گروه ثبت شدید!")
                self.send_message(chat_id, self.get_members_list(chat_id))
            else:
                self.send_message(chat_id, f"ℹ️ {self.get_user_name(user)} عزیز، شما قبلاً در گروه ثبت شده‌اید.")
        
        elif text == "/لیست":
            self.send_message(chat_id, self.get_members_list(chat_id))
        
        elif text == "/حضورغیاب":
            # بررسی اینکه آیا کاربر مربی است
            if self.is_teacher(user_id):
                # بررسی اینکه آیا این یک چت خصوصی است
                if msg["chat"]["type"] == "private":
                    # درخواست شناسه گروه از مربی
                    keyboard = {"inline_keyboard": []}
                    for group_id in self.data.get("members", {}):
                        if group_id != chat_id:  # فقط گروه‌ها را نشان بده (نه چت خصوصی)
                            keyboard["inline_keyboard"].append([{"text": f"گروه {group_id}", "callback_data": f"select_group:{group_id}"}])
                    
                    if keyboard["inline_keyboard"]:
                        self.send_message(chat_id, "لطفاً گروه مورد نظر برای ثبت حضور و غیاب را انتخاب کنید:", keyboard)
                    else:
                        self.send_message(chat_id, "⚠️ هیچ گروهی یافت نشد. ابتدا باید ربات در یک گروه فعال شود.")
                else:
                    self.send_message(chat_id, "⚠️ دستور حضور و غیاب فقط در چت خصوصی با ربات قابل استفاده است.")
            else:
                self.send_message(chat_id, "⚠️ فقط مربیان مجاز به استفاده از این دستور هستند.")
        
        # پردازش اعضای جدید گروه
        if "new_chat_members" in msg:
            for new_user in msg["new_chat_members"]:
                if str(new_user["id"]) != self.config.BOT_TOKEN.split(":")[0]:  # اگر خود ربات نیست
                    if self.register_member(chat_id, new_user):
                        self.send_message(chat_id, f"🎉 {self.get_user_name(new_user)}، به گروه خوش آمدید!\nلطفاً برای ثبت در لیست، /عضو شوید.")
    
    def handle_callback(self, callback):
        """پردازش کال‌بک‌های دریافتی"""
        if "callback_query" not in callback:
            return
        
        query = callback["callback_query"]
        user_id = str(query["from"]["id"])
        chat_id = str(query["message"]["chat"]["id"])
        message_id = query["message"]["message_id"]
        data = query["data"]
        
        # بررسی اینکه آیا کاربر مربی است
        if not self.is_teacher(user_id):
            self.send_message(chat_id, "⚠️ فقط مربیان مجاز به انجام این عملیات هستند.")
            return
        
        if data.startswith("select_group:"):
            group_id = data.split(":")[1]
            keyboard = self.create_attendance_keyboard(group_id)
            
            if keyboard:
                self.send_message(
                    chat_id,
                    f"📋 لیست حضور و غیاب\n📅 {self.get_jalali_date()}\n\nلطفاً وضعیت حضور هر عضو را مشخص کنید:",
                    keyboard
                )
            else:
                self.send_message(chat_id, "⚠️ هیچ عضوی در این گروه ثبت نشده است.")
        
        elif data.startswith("attendance:"):
            parts = data.split(":")
            member_id = parts[1]
            status = parts[2]
            group_id = parts[3] if len(parts) > 3 else chat_id
            
            result = self.record_attendance(chat_id, member_id, status, group_id)
            self.send_message(chat_id, result)
        
        elif data == "separator" or data.startswith("info:"):
            # این کال‌بک‌ها فقط برای نمایش هستند و نیازی به پردازش ندارند
            pass
    
    def run(self):
        """اجرای ربات"""
        last_update_id = 0
        
        while True:
            try:
                url = f"{self.config.BASE_URL}/getUpdates"
                params = {"timeout": 100, "offset": last_update_id + 1}
                response = requests.get(url, params=params)
                updates = response.json()
                
                if updates.get("ok") and updates.get("result"):
                    for update in updates["result"]:
                        last_update_id = update["update_id"]
                        
                        if "message" in update:
                            self.handle_message(update)
                        elif "callback_query" in update:
                            self.handle_callback(update)
            
            except Exception as e:
                logging.error(f"خطا در دریافت آپدیت‌ها: {e}")
                time.sleep(10)  # انتظار قبل از تلاش مجدد

# اجرای ربات
if __name__ == "__main__":
    config = Config()
    bot = RoomBot(config)
    bot.run()