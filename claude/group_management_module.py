# group_management_module.py
import requests
import json
from datetime import datetime
from config import BASE_URL, AUTHORIZED_USER_IDS, ADMIN_USER_IDS, HELPER_COACH_USER_IDS, GROUP_TEACHERS, GROUP_MEMBERS

class GroupManagementModule:
    def __init__(self, attendance_module):
        self.attendance_module = attendance_module
        self.groups = {}
        self.user_names_cache = {}  # کش برای نام‌های کاربران
        self.group_names_cache = {}  # کش برای نام‌های گروه‌ها
        print("GroupManagementModule initialized")

    def send_message(self, chat_id, text, reply_markup=None):
        url = f"{BASE_URL}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": text, 
            "reply_markup": reply_markup, 
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload)
            print(f"send_message: {response.status_code}, {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error in send_message: {e}")
            return False

    def get_user_name(self, user_id, user_info=None):
        """دریافت نام کاربر از API تلگرام"""
        if user_id in self.user_names_cache:
            return self.user_names_cache[user_id]
        
        # اگر user_info داده شده باشد، از آن استفاده می‌کنیم
        if user_info:
            name = user_info.get("first_name", "")
            last_name = user_info.get("last_name", "")
            username = user_info.get("username", "")
            
            if last_name:
                full_name = f"{name} {last_name}"
            elif username:
                full_name = f"{name} (@{username})"
            else:
                full_name = name or f"کاربر {user_id}"
            
            self.user_names_cache[user_id] = full_name
            return full_name
        
        # تلاش برای دریافت نام کاربر از طریق getChatMember
        # این کار در گروه‌ها کار می‌کند
        for group_id in GROUP_TEACHERS.keys():
            member_info = self.get_chat_member(group_id, user_id)
            if member_info and "user" in member_info:
                user_info = member_info["user"]
                name = user_info.get("first_name", "")
                last_name = user_info.get("last_name", "")
                username = user_info.get("username", "")
                
                if last_name:
                    full_name = f"{name} {last_name}"
                elif username:
                    full_name = f"{name} (@{username})"
                else:
                    full_name = name or f"کاربر {user_id}"
                
                self.user_names_cache[user_id] = full_name
                return full_name
        
        # اگر نتوانستیم نام را پیدا کنیم
        default_name = f"کاربر {user_id}"
        self.user_names_cache[user_id] = default_name
        return default_name

    def get_group_name(self, chat_id):
        """دریافت نام گروه از API تلگرام"""
        if chat_id in self.group_names_cache:
            return self.group_names_cache[chat_id]
        
        url = f"{BASE_URL}/getChat"
        payload = {"chat_id": chat_id}
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200 and response.json().get("ok"):
                chat_info = response.json().get("result", {})
                group_name = chat_info.get("title", f"گروه {chat_id}")
                self.group_names_cache[chat_id] = group_name
                return group_name
            else:
                default_name = f"گروه {chat_id}"
                self.group_names_cache[chat_id] = default_name
                return default_name
        except Exception as e:
            print(f"Error getting group name for {chat_id}: {e}")
            default_name = f"گروه {chat_id}"
            self.group_names_cache[chat_id] = default_name
            return default_name

    def get_chat_member(self, chat_id, user_id):
        """دریافت اطلاعات عضو گروه"""
        url = f"{BASE_URL}/getChatMember"
        payload = {"chat_id": chat_id, "user_id": user_id}
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200 and response.json().get("ok"):
                return response.json()["result"]
            return None
        except Exception as e:
            print(f"Error in get_chat_member: {e}")
            return None

    def get_group_members(self, chat_id):
        """دریافت اعضای گروه - فقط غیرادمین‌ها"""
        # ابتدا ادمین‌ها را دریافت می‌کنیم
        url = f"{BASE_URL}/getChatAdministrators"
        payload = {"chat_id": chat_id}
        try:
            response = requests.post(url, json=payload)
            print(f"get_chat_admins: {response.status_code}, {response.json()}")
            
            if response.status_code == 200 and response.json().get("ok"):
                admins_data = response.json()["result"]
                admin_ids = [admin["user"]["id"] for admin in admins_data]
                
                # مربیان این گروه را تشخیص می‌دهیم
                group_teachers = [uid for uid in admin_ids 
                               if uid in AUTHORIZED_USER_IDS or uid in ADMIN_USER_IDS or uid in HELPER_COACH_USER_IDS]
                GROUP_TEACHERS[chat_id] = group_teachers
                
                # اعضای غیرادمین را از GROUP_MEMBERS می‌گیریم یا خالی می‌کنیم
                non_admin_members = GROUP_MEMBERS.get(chat_id, [])
                
                # فقط اعضای غیرادمین را برمی‌گردانیم
                self.groups[chat_id] = non_admin_members
                
                print(f"Group {chat_id} - Teachers: {group_teachers}")
                print(f"Group {chat_id} - Members: {non_admin_members}")
                
                return non_admin_members
            else:
                print(f"Error fetching admins for {chat_id}")
                return []
        except Exception as e:
            print(f"Error in get_group_members: {e}")
            return []

    def add_member_to_group(self, chat_id, user_id, user_info=None):
        """اضافه کردن عضو به گروه"""
        if chat_id not in GROUP_MEMBERS:
            GROUP_MEMBERS[chat_id] = []
        
        if user_id not in GROUP_MEMBERS[chat_id]:
            GROUP_MEMBERS[chat_id].append(user_id)
            self.groups[chat_id] = GROUP_MEMBERS[chat_id]
            return True
        return False

    def get_group_invite_link(self, chat_id):
        """دریافت لینک دعوت گروه"""
        url = f"{BASE_URL}/getChat"
        payload = {"chat_id": chat_id}
        try:
            response = requests.post(url, json=payload)
            print(f"get_chat: {response.status_code}, {response.json()}")
            if response.status_code == 200 and response.json().get("ok"):
                chat_info = response.json().get("result", {})
                invite_link = chat_info.get("invite_link", "لینک دعوت در دسترس نیست")
                return invite_link
            return "لینک دعوت در دسترس نیست"
        except Exception as e:
            print(f"Error in get_group_invite_link: {e}")
            return "لینک دعوت در دسترس نیست"

    def is_user_teacher(self, user_id, chat_id=None):
        """بررسی اینکه کاربر مربی است یا نه"""
        if chat_id:
            return chat_id in GROUP_TEACHERS and user_id in GROUP_TEACHERS[chat_id]
        # اگر chat_id نداشته باشیم، در کل گروه‌ها چک می‌کنیم
        for group_id, teachers in GROUP_TEACHERS.items():
            if user_id in teachers:
                return True
        return False

    def is_user_admin(self, user_id):
        """بررسی اینکه کاربر مدیر است یا نه"""
        return user_id in ADMIN_USER_IDS

    def is_user_coach(self, user_id):
        """بررسی اینکه کاربر مربی است یا نه"""
        return user_id in AUTHORIZED_USER_IDS

    def is_user_helper_coach(self, user_id):
        """بررسی اینکه کاربر کمک مربی است یا نه"""
        return user_id in HELPER_COACH_USER_IDS

    def is_user_authorized(self, user_id):
        """بررسی مجوز کاربر"""
        return user_id in AUTHORIZED_USER_IDS or user_id in ADMIN_USER_IDS or user_id in HELPER_COACH_USER_IDS

    def get_group_list_keyboard(self, user_id):
        """کیبورد لیست گروه‌ها"""
        keyboard = []
        
        if self.is_user_admin(user_id):
            # مدیر همه گروه‌ها را می‌بیند
            for chat_id in GROUP_TEACHERS:
                group_name = self.get_group_name(chat_id)
                keyboard.append([{"text": group_name, "callback_data": f"admin_view_group_{chat_id}"}])
        else:
            # مربی فقط گروه‌های خودش را می‌بیند
            for chat_id, teachers in GROUP_TEACHERS.items():
                if user_id in teachers:
                    group_name = self.get_group_name(chat_id)
                    keyboard.append([{"text": group_name, "callback_data": f"teacher_view_group_{chat_id}"}])
        
        if not keyboard:
            keyboard.append([{"text": "❌ هیچ گروهی ثبت نشده", "callback_data": "main_menu"}])
        else:
            keyboard.append([{"text": "🏠 بازگشت به منوی اصلی", "callback_data": "main_menu"}])
        
        return {"inline_keyboard": keyboard}

    def handle_message(self, message):
        """پردازش پیام‌های متنی"""
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        chat_type = message["chat"]["type"]
        
        print(f"GroupManagement - Received message: user_id={user_id}, chat_id={chat_id}, text={text}, type={chat_type}")

        # پیام‌های گروهی
        if chat_type in ["group", "supergroup"]:
            if text == "/عضو":
                # بررسی اینکه کاربر ادمین یا مربی نیست
                member_info = self.get_chat_member(chat_id, user_id)
                if member_info and member_info["status"] in ["administrator", "creator"]:
                    self.send_message(chat_id, "⚠️ این دستور فقط برای اعضای عادی است!")
                    return
                
                # ثبت کاربر عادی
                user_info = message["from"]
                if self.add_member_to_group(chat_id, user_id):
                    user_name = self.get_user_name(user_id, user_info)
                    self.send_message(chat_id, f"✅ {user_name} در لیست ثبت شد.")
                else:
                    user_name = self.get_user_name(user_id, user_info)
                    self.send_message(chat_id, f"✅ {user_name} عضو گروه شد.")
                
                # نمایش لیست اعضا (فقط برای مربیان و مدیر)
                if self.is_user_teacher(user_id, chat_id) or self.is_user_admin(user_id):
                    members = self.get_group_members(chat_id)
                    if not members:
                        self.send_message(chat_id, "❌ لیست اعضای گروه خالی است!")
                        return
                    
                    group_name = self.get_group_name(chat_id)
                    text = f"📋 **لیست اعضای {group_name}**\n\n"
                    for i, member in enumerate(members, 1):
                        text += f"{i}. {self.get_user_name(member)}\n"
                    text += f"\n👥 تعداد کل: {len(members)} نفر"
                    self.send_message(chat_id, text)
                else:
                    # برای قرآن‌آموزان عادی لیست اعضا نمایش داده می‌شود
                    members = self.get_group_members(chat_id)
                    if not members:
                        self.send_message(chat_id, "❌ لیست اعضای گروه خالی است!")
                        return
                    
                    group_name = self.get_group_name(chat_id)
                    text = f"📋 **لیست اعضای {group_name}**\n\n"
                    for i, member in enumerate(members, 1):
                        text += f"{i}. {self.get_user_name(member)}\n"
                    text += f"\n👥 تعداد کل: {len(members)} نفر"
                    self.send_message(chat_id, text)

        # پیام‌های خصوصی
        elif chat_type == "private":
            if text == "/group":
                if not self.is_user_authorized(user_id):
                    self.send_message(chat_id, "❌ شما اجازه دسترسی ندارید!")
                    return
                
                text = "📋 **مدیریت گروه‌ها**\nلطفاً گروه مورد نظر را انتخاب کنید:"
                self.send_message(chat_id, text, self.get_group_list_keyboard(user_id))

    def handle_callback(self, callback):
        """پردازش درخواست‌های callback"""
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        user_id = callback["from"]["id"]
        data = callback["data"]
        callback_query_id = callback["id"]
        
        print(f"GroupManagement - Received callback: user_id={user_id}, data={data}")

        if not self.is_user_authorized(user_id):
            self.attendance_module.answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
            return

        if data == "group_menu":
            text = "📋 **مدیریت گروه‌ها**\nلطفاً گروه مورد نظر را انتخاب کنید:"
            self.attendance_module.edit_message(chat_id, message_id, text, self.get_group_list_keyboard(user_id))
            self.attendance_module.answer_callback_query(callback_query_id)
            
        elif data.startswith("teacher_view_group_") or data.startswith("admin_view_group_"):
            group_chat_id = int(data.split("_")[-1])
            
            # بروزرسانی اعضای گروه
            members = self.get_group_members(group_chat_id)
            
            # تنظیم گروه فعلی در ماژول حضور و غیاب
            self.attendance_module.users = members
            self.attendance_module.current_group_id = group_chat_id
            
            if not members:
                group_name = self.get_group_name(group_chat_id)
                text = f"❌ **{group_name}**\n\nهیچ عضوی در این گروه ثبت نشده است.\n\nاعضا باید از دستور `/عضو` در گروه استفاده کنند."
                keyboard = {"inline_keyboard": [
                    [{"text": "🔄 بروزرسانی", "callback_data": f"{'admin' if self.is_user_admin(user_id) else 'teacher'}_view_group_{group_chat_id}"}],
                    [{"text": "🏠 بازگشت به گروه‌ها", "callback_data": "group_menu"}]
                ]}
            else:
                text = self.attendance_module.get_attendance_list()
                keyboard = {"inline_keyboard": [
                    [{"text": "🔄 بروزرسانی", "callback_data": f"view_attendance_group_{group_chat_id}"}],
                    [{"text": "✏️ ثبت سریع", "callback_data": f"quick_attendance_group_{group_chat_id}"}],
                    [{"text": "📈 آمار", "callback_data": f"statistics_group_{group_chat_id}"}],
                    [{"text": "🗑️ پاک کردن داده‌ها", "callback_data": f"clear_group_{group_chat_id}"}],
                    [{"text": "🏠 بازگشت به گروه‌ها", "callback_data": "group_menu"}]
                ]}
            
            self.attendance_module.edit_message(chat_id, message_id, text, keyboard)
            self.attendance_module.answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
            
        elif data.startswith("view_attendance_group_"):
            group_chat_id = int(data.split("_")[-1])
            members = self.get_group_members(group_chat_id)
            self.attendance_module.users = members
            self.attendance_module.current_group_id = group_chat_id
            
            text = self.attendance_module.get_attendance_list()
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": f"view_attendance_group_{group_chat_id}"}],
                [{"text": "✏️ ثبت سریع", "callback_data": f"quick_attendance_group_{group_chat_id}"}],
                [{"text": "📈 آمار", "callback_data": f"statistics_group_{group_chat_id}"}],
                [{"text": "🏠 بازگشت به گروه‌ها", "callback_data": "group_menu"}]
            ]}
            self.attendance_module.edit_message(chat_id, message_id, text, keyboard)
            self.attendance_module.answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
            
        elif data.startswith("quick_attendance_group_"):
            group_chat_id = int(data.split("_")[-1])
            members = self.get_group_members(group_chat_id)
            self.attendance_module.users = members
            self.attendance_module.current_group_id = group_chat_id
            
            text = "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:"
            keyboard = self.attendance_module.get_quick_attendance_keyboard()
            
            # اضافه کردن دکمه بازگشت به گروه
            if keyboard and "inline_keyboard" in keyboard:
                keyboard["inline_keyboard"][-1] = [{"text": "🏠 بازگشت به گروه", "callback_data": f"{'admin' if self.is_user_admin(user_id) else 'teacher'}_view_group_{group_chat_id}"}]
            
            self.attendance_module.edit_message(chat_id, message_id, text, keyboard)
            self.attendance_module.answer_callback_query(callback_query_id)
            
        elif data.startswith("statistics_group_"):
            group_chat_id = int(data.split("_")[-1])
            members = self.get_group_members(group_chat_id)
            self.attendance_module.users = members
            self.attendance_module.current_group_id = group_chat_id
            
            if not members:
                group_name = self.get_group_name(group_chat_id)
                text = f"❌ **آمار {group_name}**\n\nهیچ عضوی در این گروه ثبت نشده است."
                keyboard = {"inline_keyboard": [[{"text": "🏠 بازگشت به گروه‌ها", "callback_data": "group_menu"}]]}
            else:
                total = len(members)
                present = sum(1 for status in self.attendance_module.attendance_data.values() if status == "حاضر")
                late = sum(1 for status in self.attendance_module.attendance_data.values() if status == "حضور با تاخیر")
                absent = sum(1 for status in self.attendance_module.attendance_data.values() if status == "غایب")
                justified = sum(1 for status in self.attendance_module.attendance_data.values() if status == "غیبت(موجه)")
                pending = total - len(self.attendance_module.attendance_data)
                
                group_name = self.get_group_name(group_chat_id)
                text = f"""📈 **آمار کلی حضور و غیاب - {group_name}**

👥 کل قرآن‌آموزان: {total}
✅ حاضر: {present} ({present/total*100:.1f}%)
⏰ حضور با تاخیر: {late} ({late/total*100:.1f}%)
❌ غایب: {absent} ({absent/total*100:.1f}%)
📄 غیبت(موجه): {justified} ({justified/total*100:.1f}%)
⏳ در انتظار: {pending} ({pending/total*100:.1f}%)

🕐 زمان: {self.attendance_module.get_persian_date()} - {datetime.now().strftime("%H:%M")}"""

                keyboard = {"inline_keyboard": [
                    [{"text": "🔄 بروزرسانی آمار", "callback_data": f"statistics_group_{group_chat_id}"}],
                    [{"text": "🏠 بازگشت به گروه", "callback_data": f"{'admin' if self.is_user_admin(user_id) else 'teacher'}_view_group_{group_chat_id}"}]
                ]}
            
            self.attendance_module.edit_message(chat_id, message_id, text, keyboard)
            self.attendance_module.answer_callback_query(callback_query_id, "📊 آمار بروزرسانی شد")
            
        elif data.startswith("clear_group_"):
            group_chat_id = int(data.split("_")[-1])
            members = self.get_group_members(group_chat_id)
            self.attendance_module.users = members
            self.attendance_module.current_group_id = group_chat_id
            
            # پاک کردن داده‌های حضور و غیاب این گروه
            for member in members:
                if member in self.attendance_module.attendance_data:
                    del self.attendance_module.attendance_data[member]
            
            group_name = self.get_group_name(group_chat_id)
            text = f"🗑️ **داده‌های حضور و غیاب {group_name} پاک شدند**"
            keyboard = {"inline_keyboard": [
                [{"text": "🏠 بازگشت به گروه", "callback_data": f"{'admin' if self.is_user_admin(user_id) else 'teacher'}_view_group_{group_chat_id}"}]
            ]}
            
            self.attendance_module.edit_message(chat_id, message_id, text, keyboard)
            self.attendance_module.answer_callback_query(callback_query_id, "🗑️ داده‌های گروه پاک شدند")

    def handle_new_chat_member(self, message):
        """وقتی ربات به گروه اضافه می‌شود"""
        chat_id = message["chat"]["id"]
        chat_title = message["chat"].get("title", "بدون عنوان")
        new_members = message.get("new_chat_members", [])
        
        for member in new_members:
            if member["id"] == 1778171143:  # ID ربات
                print(f"Bot added to group: chat_id={chat_id}, title={chat_title}")
                
                welcome_text = f"""🎉 **ربات حضور و غیاب به گروه اضافه شد!**

👋 سلام به همه قرآن‌آموزان عزیز!

📋 **برای ثبت نام در سیستم حضور و غیاب:**
از دستور `/عضو` استفاده کنید

🔹 **توضیحات:**
- مربیان می‌توانند از بخش خصوصی ربات حضور و غیاب شما را مدیریت کنند
- شما فقط لیست حضور و غیاب را مشاهده خواهید کرد
- برای مشاهده لیست، مجدداً از `/عضو` استفاده کنید"""

                self.send_message(chat_id, welcome_text)
                
                # دریافت اطلاعات اولیه گروه
                self.get_group_members(chat_id)
