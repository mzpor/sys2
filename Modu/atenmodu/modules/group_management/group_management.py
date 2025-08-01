import requests
from config import BASE_URL, AUTHORIZED_USER_IDS, ADMIN_USER_ID, GROUP_TEACHERS, GROUP_MEMBERS

class GroupManagementModule:
    def __init__(self, attendance_module):
        # مقداردهی اولیه
        self.attendance_module = attendance_module
        self.groups = {}  # {chat_id: [user_id1, user_id2, ...]}
        self.user_names = {}  # {user_id: name} - برای ذخیره نام‌های کاربران
        self.group_names = {}  # {chat_id: name} - برای ذخیره نام‌های گروه‌ها
        print("GroupManagementModule initialized")

    def get_user_name(self, user_id):
        """دریافت نام کاربر از API بله"""
        if user_id in self.user_names:
            return self.user_names[user_id]
        
        url = f"{BASE_URL}/getChatMember"
        payload = {"chat_id": user_id, "user_id": user_id}
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200 and response.json().get("ok"):
                user_info = response.json().get("result", {}).get("user", {})
                first_name = user_info.get("first_name", "")
                last_name = user_info.get("last_name", "")
                username = user_info.get("username", "")
                
                # ترکیب نام و نام خانوادگی
                if first_name and last_name:
                    name = f"{first_name} {last_name}"
                elif first_name:
                    name = first_name
                elif username:
                    name = f"@{username}"
                else:
                    name = f"کاربر {user_id}"
                
                self.user_names[user_id] = name
                return name
            else:
                # اگر نتوانستیم نام را دریافت کنیم، از ID استفاده می‌کنیم
                name = f"کاربر {user_id}"
                self.user_names[user_id] = name
                return name
        except Exception as e:
            print(f"Error getting user name for {user_id}: {e}")
            name = f"کاربر {user_id}"
            self.user_names[user_id] = name
            return name

    def get_group_name(self, chat_id):
        """دریافت نام گروه از API بله"""
        if chat_id in self.group_names:
            return self.group_names[chat_id]
        
        url = f"{BASE_URL}/getChat"
        payload = {"chat_id": chat_id}
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200 and response.json().get("ok"):
                chat_info = response.json().get("result", {})
                title = chat_info.get("title", "")
                username = chat_info.get("username", "")
                
                if title:
                    name = title
                elif username:
                    name = f"@{username}"
                else:
                    name = f"گروه {chat_id}"
                
                self.group_names[chat_id] = name
                return name
            else:
                name = f"گروه {chat_id}"
                self.group_names[chat_id] = name
                return name
        except Exception as e:
            print(f"Error getting group name for {chat_id}: {e}")
            name = f"گروه {chat_id}"
            self.group_names[chat_id] = name
            return name

    def send_message(self, chat_id, text, reply_markup=None):
        # ارسال پیام به کاربر یا گروه
        url = f"{BASE_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "reply_markup": reply_markup, "parse_mode": "Markdown"}
        try:
            response = requests.post(url, json=payload)
            print(f"send_message: {response.status_code}, {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error in send_message: {e}")
            return False

    def get_group_members(self, chat_id):
        # دریافت اعضای گروه از API بله
        url = f"{BASE_URL}/getChatAdministrators"
        payload = {"chat_id": chat_id}
        try:
            response = requests.post(url, json=payload)
            print(f"get_chat_admins: {response.status_code}, {response.json()}")
            if response.status_code == 200 and response.json().get("ok"):
                admins = [member["user"]["id"] for member in response.json()["result"]]
                GROUP_TEACHERS[chat_id] = [uid for uid in admins if uid in AUTHORIZED_USER_IDS or uid == ADMIN_USER_ID]
                # برای تست، فرض می‌کنیم فقط ادمین‌ها و چند کاربر نمونه داریم
                # بعداً باید API واقعی برای گرفتن همه اعضا اضافه بشه
                GROUP_MEMBERS[chat_id] = GROUP_MEMBERS.get(chat_id, [])
                self.groups[chat_id] = GROUP_MEMBERS[chat_id]
                print(f"Group members for {chat_id}: {self.groups[chat_id]}")
                print(f"Updated GROUP_TEACHERS: {GROUP_TEACHERS}")
                return self.groups[chat_id]
            else:
                print(f"Error fetching members for {chat_id}")
                return []
        except Exception as e:
            print(f"Error in get_group_members: {e}")
            return []

    def get_group_invite_link(self, chat_id):
        # دریافت لینک دعوت گروه
        url = f"{BASE_URL}/getChat"
        payload = {"chat_id": chat_id}
        try:
            response = requests.post(url, json=payload)
            print(f"get_chat: {response.status_code}, {response.json()}")
            if response.status_code == 200 and response.json().get("ok"):
                chat_info = response.json().get("result", {})
                invite_link = chat_info.get("invite_link", "لینک دعوت در دسترس نیست")
                print(f"get_group_invite_link: {invite_link}")
                return invite_link
            return "لینک دعوت در دسترس نیست"
        except Exception as e:
            print(f"Error in get_group_invite_link: {e}")
            return "لینک دعوت در دسترس نیست"

    def is_user_teacher(self, user_id, chat_id):
        # بررسی اینکه کاربر مربی گروه است یا نه
        return chat_id in GROUP_TEACHERS and user_id in GROUP_TEACHERS[chat_id]

    def is_user_admin(self, user_id):
        # بررسی اینکه کاربر مدیر است یا نه
        return user_id == ADMIN_USER_ID

    def get_group_list_keyboard(self, user_id):
        # کیبورد گروه‌ها برای مربی یا مدیر
        keyboard = []
        if self.is_user_admin(user_id):
            for teacher_id in AUTHORIZED_USER_IDS:
                teacher_name = self.get_user_name(teacher_id)
                keyboard.append([{"text": f"👨‍🏫 {teacher_name}", "callback_data": f"admin_view_teacher_{teacher_id}"}])
        else:
            for chat_id in GROUP_TEACHERS:
                if user_id in GROUP_TEACHERS[chat_id]:
                    group_name = self.get_group_name(chat_id)
                    keyboard.append([{"text": f"👥 {group_name}", "callback_data": f"teacher_view_group_{chat_id}"}])
        if not keyboard:
            keyboard.append([{"text": "❌ گروهی ثبت نشده", "callback_data": "main_menu"}])
        else:
            keyboard.append([{"text": "🏠 بازگشت به منوی اصلی", "callback_data": "main_menu"}])
        return {"inline_keyboard": keyboard}

    def get_teacher_groups_keyboard(self, teacher_id):
        # کیبورد گروه‌های مربی برای مدیر
        keyboard = []
        for chat_id in GROUP_TEACHERS:
            if teacher_id in GROUP_TEACHERS[chat_id]:
                group_name = self.get_group_name(chat_id)
                keyboard.append([{"text": f"👥 {group_name}", "callback_data": f"admin_view_group_{chat_id}"}])
        if not keyboard:
            keyboard.append([{"text": "❌ گروهی برای این مربی ثبت نشده", "callback_data": "admin_view_teachers"}])
        else:
            keyboard.append([{"text": "🔙 بازگشت", "callback_data": "admin_view_teachers"}])
        return {"inline_keyboard": keyboard}

    def handle_message(self, message):
        # پردازش پیام‌های متنی
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        print(f"Received message: user_id={user_id}, chat_id={chat_id}, text={text}")

        if message["chat"]["type"] in ["group", "supergroup"]:
            if text == "/عضو":
                if self.is_user_teacher(user_id, chat_id) or self.is_user_admin(user_id):
                    self.send_message(chat_id, "⚠️ این دستور فقط برای اعضای غیرادمین است!")
                    return
                # ثبت کاربر معمولی
                if user_id not in GROUP_MEMBERS.get(chat_id, []):
                    GROUP_MEMBERS[chat_id] = GROUP_MEMBERS.get(chat_id, []) + [user_id]
                    self.groups[chat_id] = GROUP_MEMBERS[chat_id]
                    user_name = self.get_user_name(user_id)
                    self.send_message(chat_id, f"✅ {user_name} ثبت شد.")
                # نمایش لیست اعضا
                members = self.get_group_members(chat_id)
                if not members:
                    self.send_message(chat_id, "❌ لیست اعضای گروه خالی است!")
                    return
                group_name = self.get_group_name(chat_id)
                text = f"📋 **لیست اعضای {group_name}**\n\n"
                for i, member_id in enumerate(members, 1):
                    member_name = self.get_user_name(member_id)
                    text += f"{i}. {member_name}\n"
                self.send_message(chat_id, text)
        elif message["chat"]["type"] == "private":
            if text == "/group":
                if not self.is_user_authorized(user_id):
                    self.send_message(chat_id, "❌ شما اجازه دسترسی ندارید!")
                    return
                text = "📋 **لیست گروه‌ها**\nلطفاً گروه یا مربی را انتخاب کنید:"
                self.send_message(chat_id, text, self.get_group_list_keyboard(user_id))

    def handle_callback(self, callback):
        # پردازش درخواست‌های callback
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        user_id = callback["from"]["id"]
        data = callback["data"]
        callback_query_id = callback["id"]
        print(f"Received callback: user_id={user_id}, data={data}")

        if not self.is_user_authorized(user_id):
            self.attendance_module.answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
            return

        if data == "group_menu":
            text = "📋 **لیست گروه‌ها**\nلطفاً گروه یا مربی را انتخاب کنید:"
            self.attendance_module.edit_message(chat_id, message_id, text, self.get_group_list_keyboard(user_id))
            self.attendance_module.answer_callback_query(callback_query_id)
        elif data == "admin_view_teachers":
            text = "📋 **لیست مربی‌ها**\nلطفاً مربی را انتخاب کنید:"
            self.attendance_module.edit_message(chat_id, message_id, text, self.get_group_list_keyboard(user_id))
            self.attendance_module.answer_callback_query(callback_query_id)
        elif data.startswith("admin_view_teacher_"):
            teacher_id = int(data.split("_")[-1])
            teacher_name = self.get_user_name(teacher_id)
            text = f"📋 **گروه‌های {teacher_name}**\nلطفاً گروه را انتخاب کنید:"
            self.attendance_module.edit_message(chat_id, message_id, text, self.get_teacher_groups_keyboard(teacher_id))
            self.attendance_module.answer_callback_query(callback_query_id)
        elif data.startswith("teacher_view_group_") or data.startswith("admin_view_group_"):
            group_chat_id = data.split("_")[-1]
            self.attendance_module.users = self.groups.get(group_chat_id, [])
            text = self.attendance_module.get_attendance_list()
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": f"view_attendance_{group_chat_id}"}],
                [{"text": "✏️ ثبت سریع", "callback_data": f"quick_attendance_{group_chat_id}"}],
                [{"text": "🏠 بازگشت به گروه‌ها", "callback_data": "admin_view_teachers" if self.is_user_admin(user_id) else "group_menu"}]
            ]}
            self.attendance_module.edit_message(chat_id, message_id, text, keyboard)
            self.attendance_module.answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
        elif data.startswith("view_attendance_"):
            group_chat_id = data.split("_")[-1]
            self.attendance_module.users = self.groups.get(group_chat_id, [])
            text = self.attendance_module.get_attendance_list()
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": f"view_attendance_{group_chat_id}"}],
                [{"text": "✏️ ثبت سریع", "callback_data": f"quick_attendance_{group_chat_id}"}],
                [{"text": "🏠 بازگشت به گروه‌ها", "callback_data": "admin_view_teachers" if self.is_user_admin(user_id) else "group_menu"}]
            ]}
            self.attendance_module.edit_message(chat_id, message_id, text, keyboard)
            self.attendance_module.answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
        elif data.startswith("quick_attendance_"):
            group_chat_id = data.split("_")[-1]
            self.attendance_module.users = self.groups.get(group_chat_id, [])
            text = "✏️ **ثبت سریع حضور و غیاب**\nروی نام هر کاربر کلیک کنید:"
            self.attendance_module.edit_message(chat_id, message_id, text, self.attendance_module.get_quick_attendance_keyboard())
            self.attendance_module.answer_callback_query(callback_query_id)

    def handle_new_chat_member(self, message):
        # وقتی ربات به گروه اضافه می‌شه
        chat_id = message["chat"]["id"]
        chat_title = message["chat"].get("title", "بدون عنوان")
        invite_link = self.get_group_invite_link(chat_id)
        new_members = message.get("new_chat_members", [])
        for member in new_members:
            if member["id"] == 1778171143:  # user_id ربات
                print(f"Bot added to group: chat_id={chat_id}, title={chat_title}, invite_link={invite_link}")
                self.send_message(chat_id, "🎉 ربات به گروه اضافه شد! برای دیدن لیست اعضا از /عضو استفاده کنید.")
                self.get_group_members(chat_id)