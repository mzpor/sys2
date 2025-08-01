import requests
from config import BASE_URL, AUTHORIZED_USER_IDS, ADMIN_USER_ID, GROUP_TEACHERS

class GroupManagementModule:
    def __init__(self, attendance_module):
        # مقداردهی اولیه
        self.attendance_module = attendance_module  # ارجاع به ماژول حضور و غیاب
        self.groups = {}  # دیکشنری برای ذخیره اعضای گروه‌ها: {chat_id: [user_id1, user_id2, ...]}
        print("GroupManagementModule initialized")

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
                # فرض می‌کنیم غیرادمین‌ها دانش‌آموزن
                url = f"{BASE_URL}/getChatMembersCount"
                count_response = requests.post(url, json={"chat_id": chat_id})
                total_members = count_response.json().get("result", 0)
                non_admins = [f"دانش‌آموز{i+1}" for i in range(total_members - len(admins))]
                self.groups[chat_id] = non_admins
                print(f"Group members for {chat_id}: {non_admins}")
                # به‌روزرسانی GROUP_TEACHERS
                GROUP_TEACHERS[chat_id] = [uid for uid in admins if uid in AUTHORIZED_USER_IDS]
                print(f"Updated GROUP_TEACHERS: {GROUP_TEACHERS}")
                return non_admins
            else:
                print(f"Error fetching members for {chat_id}")
                return []
        except Exception as e:
            print(f"Error in get_group_members: {e}")
            return []

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
            # مدیر: نمایش لیست مربی‌ها
            for teacher_id in AUTHORIZED_USER_IDS:
                keyboard.append([{"text": f"مربی {teacher_id}", "callback_data": f"admin_view_teacher_{teacher_id}"}])
        else:
            # مربی: نمایش گروه‌هایی که مربی توشونه
            for chat_id in GROUP_TEACHERS:
                if user_id in GROUP_TEACHERS[chat_id]:
                    keyboard.append([{"text": f"گروه {chat_id}", "callback_data": f"teacher_view_group_{chat_id}"}])
        keyboard.append([{"text": "🏠 بازگشت به منوی اصلی", "callback_data": "main_menu"}])
        return {"inline_keyboard": keyboard}

    def get_teacher_groups_keyboard(self, teacher_id):
        # کیبورد گروه‌های مربی برای مدیر
        keyboard = []
        for chat_id in GROUP_TEACHERS:
            if teacher_id in GROUP_TEACHERS[chat_id]:
                keyboard.append([{"text": f"گروه {chat_id}", "callback_data": f"admin_view_group_{chat_id}"}])
        keyboard.append([{"text": "🔙 بازگشت", "callback_data": "admin_view_teachers"}])
        return {"inline_keyboard": keyboard}

    def handle_message(self, message):
        # پردازش پیام‌های متنی
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        print(f"Received message: user_id={user_id}, chat_id={chat_id}, text={text}")

        if message["chat"]["type"] == "group" or message["chat"]["type"] == "supergroup":
            # پیام توی گروه
            if text == "/عضو":
                members = self.get_group_members(chat_id)
                if not members:
                    self.send_message(chat_id, "❌ خطا در دریافت اعضای گروه!")
                    return
                text = f"📋 **لیست اعضای گروه {chat_id}**\n\n"
                for i, member in enumerate(members, 1):
                    text += f"{i}. {member}\n"
                self.send_message(chat_id, text)
        elif message["chat"]["type"] == "private":
            # پیام توی چت خصوصی
            if text == "/groups":
                if user_id not in AUTHORIZED_USER_IDS and user_id != ADMIN_USER_ID:
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

        if user_id not in AUTHORIZED_USER_IDS and user_id != ADMIN_USER_ID:
            self.attendance_module.answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی ندارید!")
            return

        if data == "admin_view_teachers":
            text = "📋 **لیست مربی‌ها**\nلطفاً مربی را انتخاب کنید:"
            self.attendance_module.edit_message(chat_id, message_id, text, self.get_group_list_keyboard(user_id))
            self.attendance_module.answer_callback_query(callback_query_id)
        elif data.startswith("admin_view_teacher_"):
            teacher_id = int(data.split("_")[-1])
            text = f"📋 **گروه‌های مربی {teacher_id}**\nلطفاً گروه را انتخاب کنید:"
            self.attendance_module.edit_message(chat_id, message_id, text, self.get_teacher_groups_keyboard(teacher_id))
            self.attendance_module.answer_callback_query(callback_query_id)
        elif data.startswith("teacher_view_group_") or data.startswith("admin_view_group_"):
            group_chat_id = data.split("_")[-1]
            # به‌روزرسانی لیست کاربران ماژول حضور و غیاب
            self.attendance_module.users = self.groups.get(group_chat_id, [])
            text = self.attendance_module.get_attendance_list()
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": f"view_attendance_{group_chat_id}"}],
                [{"text": "✏️ ثبت سریع", "callback_data": f"quick_attendance_{group_chat_id}"}],
                [{"text": "🏠 بازگشت به گروه‌ها", "callback_data": "admin_view_teachers" if self.is_user_admin(user_id) else "teacher_view_groups"}]
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
                [{"text": "🏠 بازگشت به گروه‌ها", "callback_data": "admin_view_teachers" if self.is_user_admin(user_id) else "teacher_view_groups"}]
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
        new_members = message.get("new_chat_members", [])
        for member in new_members:
            if member["id"] == 1778171143:  # user_id ربات
                self.send_message(chat_id, "🎉 ربات به گروه اضافه شد! برای دیدن لیست اعضا از /عضو استفاده کنید.")
                self.get_group_members(chat_id)