import requests
from config import BASE_URL, AUTHORIZED_USER_IDS, ADMIN_USER_ID, GROUP_TEACHERS, GROUP_MEMBERS

class GroupManagementModule:
    def __init__(self, attendance_module):
        # مقداردهی اولیه
        self.attendance_module = attendance_module
        self.groups = {}  # {chat_id: [user_id1, user_id2, ...]}
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
        # ابتدا تلاش می‌کنیم از API getChatMembers استفاده کنیم (اگر موجود باشد)
        url = f"{BASE_URL}/getChatMembers"
        payload = {"chat_id": chat_id}
        try:
            response = requests.post(url, json=payload)
            print(f"get_chat_members: {response.status_code}, {response.json() if response.status_code == 200 else 'Error'}")
            if response.status_code == 200 and response.json().get("ok"):
                chat_members = response.json().get("result", [])
                members = [member["user"]["id"] for member in chat_members]
                
                # بروزرسانی لیست اعضای گروه
                if chat_id not in GROUP_MEMBERS:
                    GROUP_MEMBERS[chat_id] = []
                GROUP_MEMBERS[chat_id] = list(set(GROUP_MEMBERS[chat_id] + members))
                
                # بروزرسانی لیست مربیان گروه
                if chat_id not in GROUP_TEACHERS:
                    GROUP_TEACHERS[chat_id] = []
                
                # فقط کاربران مجاز را به لیست مربیان اضافه می‌کنیم
                for member_id in members:
                    if member_id in AUTHORIZED_USER_IDS or member_id == ADMIN_USER_ID:
                        if member_id not in GROUP_TEACHERS[chat_id]:
                            GROUP_TEACHERS[chat_id].append(member_id)
                
                self.groups[chat_id] = GROUP_MEMBERS[chat_id]
                print(f"Group members for {chat_id}: {self.groups[chat_id]}")
                print(f"Updated GROUP_TEACHERS: {GROUP_TEACHERS}")
                return self.groups[chat_id]
        except Exception as e:
            print(f"Error in get_chat_members API: {e}")
            # اگر API getChatMembers موجود نباشد یا خطا دهد، از روش جایگزین استفاده می‌کنیم
        
        # دریافت ادمین‌ها به عنوان روش جایگزین
        url = f"{BASE_URL}/getChatAdministrators"
        payload = {"chat_id": chat_id}
        try:
            response = requests.post(url, json=payload)
            print(f"get_chat_admins: {response.status_code}, {response.json()}")
            if response.status_code == 200 and response.json().get("ok"):
                admins = [member["user"]["id"] for member in response.json()["result"]]
                GROUP_TEACHERS[chat_id] = [uid for uid in admins if uid in AUTHORIZED_USER_IDS or uid == ADMIN_USER_ID]
                
                # اطمینان از وجود لیست اعضا
                if chat_id not in GROUP_MEMBERS:
                    GROUP_MEMBERS[chat_id] = []
                
                # ترکیب ادمین‌ها و اعضای عادی
                all_members = GROUP_MEMBERS[chat_id].copy()
                
                # اضافه کردن ادمین‌ها به لیست کامل اعضا اگر در لیست نیستند
                for admin_id in admins:
                    if admin_id not in all_members:
                        all_members.append(admin_id)
                
                self.groups[chat_id] = all_members
                print(f"Group members for {chat_id}: {self.groups[chat_id]}")
                print(f"Updated GROUP_TEACHERS: {GROUP_TEACHERS}")
                return self.groups[chat_id]
            else:
                print(f"Error fetching members for {chat_id}")
                return GROUP_MEMBERS.get(chat_id, [])
        except Exception as e:
            print(f"Error in get_group_members: {e}")
            return GROUP_MEMBERS.get(chat_id, [])

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
            
    def get_user_info(self, user_id):
        # دریافت اطلاعات کاربر
        url = f"{BASE_URL}/getChat"
        payload = {"chat_id": user_id}
        try:
            response = requests.post(url, json=payload)
            print(f"get_user_info: {response.status_code}, {response.json()}")
            if response.status_code == 200 and response.json().get("ok"):
                user_info = response.json().get("result", {})
                return user_info
            return None
        except Exception as e:
            print(f"Error in get_user_info: {e}")
            return None

    def is_user_authorized(self, user_id):
        # بررسی اینکه کاربر مجاز است یا نه
        return user_id in AUTHORIZED_USER_IDS or user_id == ADMIN_USER_ID

    def is_user_admin(self, user_id):
        # بررسی اینکه کاربر مدیر است یا نه
        return user_id == ADMIN_USER_ID
        
    def is_user_teacher(self, user_id, chat_id):
        # بررسی اینکه کاربر مربی گروه است یا نه
        return chat_id in GROUP_TEACHERS and user_id in GROUP_TEACHERS[chat_id]

    def get_group_list_keyboard(self, user_id):
        # کیبورد گروه‌ها برای مربی یا مدیر
        keyboard = []
        if self.is_user_admin(user_id):
            for teacher_id in AUTHORIZED_USER_IDS:
                keyboard.append([{"text": f"مربی {teacher_id}", "callback_data": f"admin_view_teacher_{teacher_id}"}])
        else:
            for chat_id in GROUP_TEACHERS:
                if user_id in GROUP_TEACHERS[chat_id]:
                    # تلاش برای دریافت اطلاعات گروه
                    group_info = self.get_user_info(chat_id)
                    group_name = f"گروه {chat_id}"
                    
                    if group_info and "title" in group_info:
                        group_name = group_info.get("title", group_name)
                    
                    # تعداد اعضای گروه
                    member_count = len(self.groups.get(chat_id, []))
                    button_text = f"{group_name} ({member_count} عضو)"
                    
                    keyboard.append([{"text": button_text, "callback_data": f"teacher_view_group_{chat_id}"}])
        if not keyboard:
            keyboard.append([{"text": "❌ گروهی ثبت نشده", "callback_data": "main_menu"}])
        else:
            keyboard.append([{"text": "🏠 بازگشت به منوی اصلی", "callback_data": "main_menu"}])
            keyboard.append([{"text": "📚 راهنمای استفاده", "callback_data": "help"}])
        return {"inline_keyboard": keyboard}

    def get_teacher_groups_keyboard(self, teacher_id):
        # کیبورد گروه‌های مربی برای مدیر
        keyboard = []
        for chat_id in GROUP_TEACHERS:
            if teacher_id in GROUP_TEACHERS[chat_id]:
                # تلاش برای دریافت اطلاعات گروه
                group_info = self.get_user_info(chat_id)
                group_name = f"گروه {chat_id}"
                
                if group_info and "title" in group_info:
                    group_name = group_info.get("title", group_name)
                
                # تعداد اعضای گروه
                member_count = len(self.groups.get(chat_id, []))
                button_text = f"{group_name} ({member_count} عضو)"
                
                keyboard.append([{"text": button_text, "callback_data": f"admin_view_group_{chat_id}"}])
        if not keyboard:
            keyboard.append([{"text": "❌ گروهی برای این مربی ثبت نشده", "callback_data": "admin_view_teachers"}])
        else:
            keyboard.append([{"text": "🔙 بازگشت", "callback_data": "admin_view_teachers"}])
            keyboard.append([{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}])
            keyboard.append([{"text": "📚 راهنمای استفاده", "callback_data": "help"}])
        return {"inline_keyboard": keyboard}
        
    def get_admin_groups_keyboard(self):
        # کیبورد همه گروه‌ها برای مدیر
        keyboard = []
        for chat_id in GROUP_TEACHERS:
            # تلاش برای دریافت اطلاعات گروه
            group_info = self.get_user_info(chat_id)
            group_name = f"گروه {chat_id}"
            
            if group_info and "title" in group_info:
                group_name = group_info.get("title", group_name)
            
            # بروزرسانی لیست اعضای گروه قبل از نمایش
            self.get_group_members(chat_id)
            
            # تعداد اعضای گروه
            member_count = len(self.groups.get(chat_id, []))
            button_text = f"{group_name} ({member_count} عضو)"
            
            keyboard.append([{"text": button_text, "callback_data": f"admin_view_group_{chat_id}"}])
        if not keyboard:
            keyboard.append([{"text": "❌ هیچ گروهی ثبت نشده", "callback_data": "main_menu"}])
        else:
            keyboard.append([{"text": "👨‍🏫 مشاهده مربیان", "callback_data": "admin_view_teachers"}])
            keyboard.append([{"text": "👨‍🏫 مدیریت مربیان", "callback_data": "teachers_menu"}])
            keyboard.append([{"text": "🔄 بروزرسانی لیست", "callback_data": "group_menu"}])
            keyboard.append([{"text": "🏠 بازگشت به منوی اصلی", "callback_data": "main_menu"}])
            keyboard.append([{"text": "📚 راهنمای استفاده", "callback_data": "help"}])
        return {"inline_keyboard": keyboard}

    def handle_message(self, message):
        # پردازش پیام‌های متنی
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        print(f"Received message: user_id={user_id}, chat_id={chat_id}, text={text}")

        if message["chat"]["type"] in ["group", "supergroup"]:
            if text == "/help" or text == "/راهنما":
                # ارسال راهنمای استفاده از ربات
                self.send_help_message(chat_id)
                return
                
            elif text == "/عضو":
                # ثبت کاربر معمولی اگر مدیر یا مربی نیست
                if not self.is_user_teacher(user_id, chat_id) and not self.is_user_admin(user_id):
                    if user_id not in GROUP_MEMBERS.get(chat_id, []):
                        GROUP_MEMBERS[chat_id] = GROUP_MEMBERS.get(chat_id, []) + [user_id]
                        self.groups[chat_id] = GROUP_MEMBERS[chat_id]
                        self.send_message(chat_id, f"✅ کاربر با آیدی {user_id} ثبت شد.")
                
                # نمایش لیست اعضا برای همه
                members = self.get_group_members(chat_id)
                if not members:
                    self.send_message(chat_id, "❌ لیست اعضای گروه خالی است!")
                    return
                text = f"📋 **لیست اعضای گروه {chat_id}**\n\n"
                for i, member_id in enumerate(members, 1):
                    # تلاش برای دریافت اطلاعات کاربر
                    user_info = self.get_user_info(member_id)
                    if user_info and "first_name" in user_info:
                        name = user_info.get("first_name", "")
                        last_name = user_info.get("last_name", "")
                        username = user_info.get("username", "")
                        full_name = f"{name} {last_name}".strip()
                        user_text = f"{full_name}"
                        if username:
                            user_text += f" (@{username})"
                        text += f"{i}. {user_text} - ID: {member_id}\n"
                    else:
                        text += f"{i}. کاربر {member_id}\n"
                self.send_message(chat_id, text)
        elif message["chat"]["type"] == "private":
            if text == "/start":
                # دریافت اطلاعات کاربر
                user_info = self.get_user_info(user_id)
                user_name = ""
                if user_info and "first_name" in user_info:
                    name = user_info.get("first_name", "")
                    last_name = user_info.get("last_name", "")
                    user_name = f"{name} {last_name}".strip()
                
                # پیام خوش‌آمدگویی
                if self.is_user_authorized(user_id):
                    if self.is_user_admin(user_id):
                        welcome_text = f"👋 **سلام مدیر {user_name}! به ربات مدیریت گروه و حضور و غیاب خوش آمدید.**\n\n"
                        welcome_text += "🔹 **راهنمای استفاده:**\n"
                        welcome_text += "1️⃣ با دستور /عضو یا /group می‌توانید لیست گروه‌ها را مشاهده کنید.\n"
                        welcome_text += "2️⃣ با دستور /help یا /راهنما می‌توانید راهنمای کامل استفاده از ربات را مشاهده کنید.\n\n"
                        welcome_text += "✅ شما به عنوان مدیر شناخته شده‌اید و می‌توانید از تمامی امکانات ربات استفاده کنید.\n"
                        self.send_message(chat_id, welcome_text, self.get_admin_groups_keyboard())
                    else:
                        welcome_text = f"👋 **سلام مربی {user_name}! به ربات مدیریت گروه و حضور و غیاب خوش آمدید.**\n\n"
                        welcome_text += "🔹 **راهنمای استفاده:**\n"
                        welcome_text += "1️⃣ با دستور /عضو یا /group می‌توانید لیست گروه‌های خود را مشاهده کنید.\n"
                        welcome_text += "2️⃣ با دستور /help یا /راهنما می‌توانید راهنمای کامل استفاده از ربات را مشاهده کنید.\n\n"
                        welcome_text += "✅ شما به عنوان مربی شناخته شده‌اید و می‌توانید از امکانات ربات استفاده کنید.\n"
                        self.send_message(chat_id, welcome_text, self.get_group_list_keyboard(user_id))
                else:
                    welcome_text = f"👋 **سلام {user_name}! به ربات مدیریت گروه و حضور و غیاب خوش آمدید.**\n\n"
                    welcome_text += "🔹 **راهنمای استفاده:**\n"
                    welcome_text += "1️⃣ با دستور /help یا /راهنما می‌توانید راهنمای کامل استفاده از ربات را مشاهده کنید.\n\n"
                    welcome_text += "⚠️ شما به عنوان قرآن‌آموز شناخته شده‌اید و دسترسی محدودی به امکانات ربات دارید.\n"
                    self.send_message(chat_id, welcome_text)
                return
                
            elif text == "/help" or text == "/راهنما":
                # ارسال راهنمای استفاده از ربات در چت خصوصی
                self.send_help_message(chat_id, is_private=True)
                return
                
            elif text == "/group" or text == "/عضو":
                if not self.is_user_authorized(user_id):
                    self.send_message(chat_id, "❌ شما اجازه دسترسی ندارید!\n\nفقط مدیران و مربیان می‌توانند از این دستور استفاده کنند.")
                    return
                
                # دریافت اطلاعات کاربر
                user_info = self.get_user_info(user_id)
                user_name = ""
                if user_info and "first_name" in user_info:
                    name = user_info.get("first_name", "")
                    last_name = user_info.get("last_name", "")
                    user_name = f"{name} {last_name}".strip()
                
                # پیام متفاوت برای مدیر و مربی
                if self.is_user_admin(user_id):
                    greeting = f"👋 سلام مدیر {user_name}\n"
                    text = f"{greeting}📋 **لیست گروه‌ها**\nلطفاً گروه را انتخاب کنید:"
                    self.send_message(chat_id, text, self.get_admin_groups_keyboard())
                else:
                    greeting = f"👋 سلام مربی {user_name}\n"
                    text = f"{greeting}📋 **لیست گروه‌های شما**\nلطفاً گروه را انتخاب کنید:"
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
            # پاک کردن گروه فعلی در ماژول attendance
            self.attendance_module.current_group_id = None
            
            text = "📋 **لیست گروه‌ها**\nلطفاً گروه یا مربی را انتخاب کنید:"
            if self.is_user_admin(user_id):
                self.attendance_module.edit_message(chat_id, message_id, text, self.get_admin_groups_keyboard())
                self.attendance_module.answer_callback_query(callback_query_id, "✅ لیست گروه‌ها برای مدیر نمایش داده شد")
            else:
                self.attendance_module.edit_message(chat_id, message_id, text, self.get_group_list_keyboard(user_id))
                self.attendance_module.answer_callback_query(callback_query_id, "✅ لیست گروه‌ها نمایش داده شد")
        elif data == "admin_view_teachers":
            # پاک کردن گروه فعلی در ماژول attendance
            self.attendance_module.current_group_id = None
            
            text = "📋 **لیست مربی‌ها**\nلطفاً مربی را انتخاب کنید:"
            self.attendance_module.edit_message(chat_id, message_id, text, self.get_group_list_keyboard(user_id))
            self.attendance_module.answer_callback_query(callback_query_id)
        elif data == "teachers_menu":
            # پاک کردن گروه فعلی در ماژول attendance
            self.attendance_module.current_group_id = None
            
            # ارسال درخواست به ماژول مدیریت مربیان
            # این callback در ماژول teacher_management پردازش خواهد شد
            return False
        elif data.startswith("admin_view_teacher_"):
            # پاک کردن گروه فعلی در ماژول attendance
            self.attendance_module.current_group_id = None
            
            teacher_id = int(data.split("_")[-1])
            text = f"📋 **گروه‌های مربی {teacher_id}**\nلطفاً گروه را انتخاب کنید:"
            self.attendance_module.edit_message(chat_id, message_id, text, self.get_teacher_groups_keyboard(teacher_id))
            self.attendance_module.answer_callback_query(callback_query_id)
        elif data.startswith("teacher_view_group_") or data.startswith("admin_view_group_"):
            group_chat_id = int(data.split("_")[-1])
            # بروزرسانی لیست اعضای گروه
            members = self.get_group_members(group_chat_id)
            self.attendance_module.users = members
            
            # نمایش منوی گروه
            group_name = f"گروه {group_chat_id}"
            text = f"📋 **منوی {group_name}**\n\n"
            text += f"تعداد اعضا: {len(members)}\n\n"
            text += "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
            
            keyboard = {"inline_keyboard": [
                [{"text": "👥 مشاهده اعضا", "callback_data": f"view_members_{group_chat_id}"}],
                [{"text": "📊 مشاهده حضور و غیاب", "callback_data": f"view_attendance_{group_chat_id}"}],
                [{"text": "⚡ حضور و غیاب سریع", "callback_data": f"quick_attendance_{group_chat_id}"}],
                [{"text": "🏠 بازگشت به گروه‌ها", "callback_data": "admin_view_teachers" if self.is_user_admin(user_id) else "group_menu"}]
            ]}
            self.attendance_module.edit_message(chat_id, message_id, text, keyboard)
            self.attendance_module.answer_callback_query(callback_query_id, "✅ منوی گروه بروزرسانی شد")
        elif data.startswith("view_members_"):
            group_chat_id = int(data.split("_")[-1])
            # بروزرسانی لیست اعضای گروه
            members = self.get_group_members(group_chat_id)
            
            # دریافت نام گروه
            group_name = f"گروه {group_chat_id}"
            
            # دریافت تاریخ شمسی
            persian_date = self.attendance_module.get_persian_date()
            
            # نمایش لیست اعضا با اطلاعات بیشتر
            text = f"📋 **لیست اعضای گروه {group_name}**\n"
            text += f"📅 تاریخ: {persian_date}\n"
            text += f"🆔 شناسه گروه: {group_chat_id}\n\n"
            text += f"تعداد کل اعضا: {len(members)}\n\n"
            
            # تفکیک مدیران و مربیان از سایر اعضا
            admins = []
            teachers = []
            regular_members = []
            
            for member_id in members:
                if member_id == ADMIN_USER_ID:
                    admins.append(member_id)
                elif member_id in AUTHORIZED_USER_IDS:
                    teachers.append(member_id)
                else:
                    regular_members.append(member_id)
            
            # نمایش مدیران (فقط برای ادمین‌ها در چت خصوصی)
            is_private_chat = chat_id > 0
            is_admin = self.is_user_admin(user_id)
            
            if admins and is_admin and is_private_chat:
                text += "👑 **مدیران:**\n"
                for i, member_id in enumerate(admins, 1):
                    user_info = self.get_user_info(member_id)
                    if user_info and "first_name" in user_info:
                        name = user_info.get("first_name", "")
                        last_name = user_info.get("last_name", "")
                        username = user_info.get("username", "")
                        full_name = f"{name} {last_name}".strip()
                        user_text = f"{full_name}"
                        if username:
                            user_text += f" (@{username})"
                        text += f"{i}. {user_text}\n"
                        # اطلاعات ID فقط در لاگ نمایش داده می‌شود
                        print(f"Admin: {user_text} - ID: {member_id}")
                    else:
                        text += f"{i}. قرآن‌آموز {member_id}\n"
                text += "\n"
            
            # نمایش مربیان
            if teachers:
                text += "👨‍🏫 **مربیان:**\n"
                for i, member_id in enumerate(teachers, 1):
                    user_info = self.get_user_info(member_id)
                    if user_info and "first_name" in user_info:
                        name = user_info.get("first_name", "")
                        last_name = user_info.get("last_name", "")
                        username = user_info.get("username", "")
                        full_name = f"{name} {last_name}".strip()
                        user_text = f"{full_name}"
                        if username:
                            user_text += f" (@{username})"
                        text += f"{i}. {user_text}\n"
                        # اطلاعات ID فقط در لاگ نمایش داده می‌شود
                        print(f"Teacher: {user_text} - ID: {member_id}")
                    else:
                        text += f"{i}. قرآن‌آموز {member_id}\n"
                text += "\n"
            
            # نمایش سایر اعضا (قرآن‌آموزان)
            if regular_members:
                text += "👤 **قرآن‌آموزان:**\n"
                for i, member_id in enumerate(regular_members, 1):
                    user_info = self.get_user_info(member_id)
                    if user_info and "first_name" in user_info:
                        name = user_info.get("first_name", "")
                        last_name = user_info.get("last_name", "")
                        username = user_info.get("username", "")
                        full_name = f"{name} {last_name}".strip()
                        user_text = f"{full_name}"
                        if username:
                            user_text += f" (@{username})"
                        text += f"{i}. {user_text}\n"
                        # اطلاعات ID فقط در لاگ نمایش داده می‌شود
                        print(f"Student: {user_text} - ID: {member_id}")
                    else:
                        text += f"{i}. قرآن‌آموز {member_id}\n"
            
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": f"view_members_{group_chat_id}"}],
                [{"text": "📊 مشاهده حضور و غیاب", "callback_data": f"view_attendance_{group_chat_id}"}],
                [{"text": "⚡ حضور و غیاب سریع", "callback_data": f"quick_attendance_{group_chat_id}"}],
                [{"text": "🏠 بازگشت به گروه‌ها", "callback_data": "admin_view_teachers" if self.is_user_admin(user_id) else "group_menu"}]
            ]}
            self.attendance_module.edit_message(chat_id, message_id, text, keyboard)
            self.attendance_module.answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
        elif data.startswith("view_attendance_"):
            group_chat_id = int(data.split("_")[-1])
            # بروزرسانی لیست اعضای گروه
            members = self.get_group_members(group_chat_id)
            self.attendance_module.users = members
            
            # تنظیم گروه فعلی در ماژول attendance
            self.attendance_module.current_group_id = group_chat_id
            
            # دریافت نام گروه
            group_name = f"گروه {group_chat_id}"
            
            # نمایش لیست حضور و غیاب با نام گروه و تاریخ شمسی
            text = self.attendance_module.get_attendance_list(group_id=group_chat_id)
            
            # اضافه کردن شناسه گروه به لاگ
            print(f"Viewing attendance for group: {group_name} (ID: {group_chat_id})")
            
            keyboard = {"inline_keyboard": [
                [{"text": "🔄 بروزرسانی", "callback_data": f"view_attendance_{group_chat_id}"}],
                [{"text": "✏️ ثبت سریع", "callback_data": f"quick_attendance_{group_chat_id}"}],
                [{"text": "👥 مشاهده لیست اعضا", "callback_data": f"view_members_{group_chat_id}"}],
                [{"text": "🏠 بازگشت به گروه‌ها", "callback_data": "admin_view_teachers" if self.is_user_admin(user_id) else "group_menu"}]
            ]}
            self.attendance_module.edit_message(chat_id, message_id, text, keyboard)
            self.attendance_module.answer_callback_query(callback_query_id, "✅ لیست بروزرسانی شد")
        elif data.startswith("quick_attendance_"):
            group_chat_id = int(data.split("_")[-1])
            # بروزرسانی لیست اعضای گروه
            members = self.get_group_members(group_chat_id)
            self.attendance_module.users = members
            
            # تنظیم گروه فعلی در ماژول attendance
            self.attendance_module.current_group_id = group_chat_id
            
            # دریافت نام گروه
            group_name = f"گروه {group_chat_id}"
            
            # دریافت تاریخ شمسی
            persian_date = self.attendance_module.get_persian_date()
            
            # نمایش فرم ثبت سریع حضور و غیاب با نام گروه و تاریخ
            text = f"✏️ **ثبت سریع حضور و غیاب {group_name}**\n"
            text += f"📅 تاریخ: {persian_date}\n"
            text += "روی نام هر قرآن‌آموز کلیک کنید:"
            
            # اضافه کردن شناسه گروه به لاگ
            print(f"Quick attendance for group: {group_name} (ID: {group_chat_id})")
            
            self.attendance_module.edit_message(chat_id, message_id, text, self.attendance_module.get_quick_attendance_keyboard())
            self.attendance_module.answer_callback_query(callback_query_id, f"✅ فرم حضور و غیاب {group_name} باز شد")
        elif data == "help":
            # ارسال راهنمای استفاده از ربات در چت خصوصی
            self.send_help_message(chat_id, is_private=True)
            self.attendance_module.answer_callback_query(callback_query_id, "✅ راهنما نمایش داده شد")
        elif data == "main_menu":
            # دریافت اطلاعات کاربر
            user_info = self.get_user_info(user_id)
            user_name = ""
            if user_info and "first_name" in user_info:
                name = user_info.get("first_name", "")
                last_name = user_info.get("last_name", "")
                user_name = f"{name} {last_name}".strip()
            
            # پاک کردن گروه فعلی در ماژول attendance
            self.attendance_module.current_group_id = None
            
            # بازگشت به منوی اصلی با پیام مناسب
            if self.is_user_admin(user_id):
                welcome_text = f"👋 **سلام مدیر {user_name}! به ربات مدیریت گروه و حضور و غیاب خوش آمدید.**\n\n"
                welcome_text += "🔹 **راهنمای استفاده:**\n"
                welcome_text += "1️⃣ با دستور /عضو یا /group می‌توانید لیست گروه‌ها را مشاهده کنید.\n"
                welcome_text += "2️⃣ با دستور /help یا /راهنما می‌توانید راهنمای کامل استفاده از ربات را مشاهده کنید.\n\n"
                welcome_text += "✅ شما به عنوان مدیر شناخته شده‌اید و می‌توانید از تمامی امکانات ربات استفاده کنید.\n"
                self.attendance_module.edit_message(chat_id, message_id, welcome_text, self.get_admin_groups_keyboard())
            else:
                welcome_text = f"👋 **سلام مربی {user_name}! به ربات مدیریت گروه و حضور و غیاب خوش آمدید.**\n\n"
                welcome_text += "🔹 **راهنمای استفاده:**\n"
                welcome_text += "1️⃣ با دستور /عضو یا /group می‌توانید لیست گروه‌های خود را مشاهده کنید.\n"
                welcome_text += "2️⃣ با دستور /help یا /راهنما می‌توانید راهنمای کامل استفاده از ربات را مشاهده کنید.\n\n"
                welcome_text += "✅ شما به عنوان مربی شناخته شده‌اید و می‌توانید از امکانات ربات استفاده کنید.\n"
                self.attendance_module.edit_message(chat_id, message_id, welcome_text, self.get_group_list_keyboard(user_id))
            self.attendance_module.answer_callback_query(callback_query_id, "✅ بازگشت به منوی اصلی")

    def send_help_message(self, chat_id, is_private=False):
        # ارسال پیام راهنما
        help_text = "🔰 **راهنمای استفاده از ربات مدیریت گروه و حضور و غیاب**\n\n"
        
        if is_private:
            # راهنمای چت خصوصی
            help_text += "**🔹 دستورات قابل استفاده در چت خصوصی:**\n\n"
            help_text += "1️⃣ **/عضو** یا **/group**: نمایش لیست گروه‌هایی که ربات در آن‌ها عضو است\n"
            help_text += "2️⃣ پس از انتخاب گروه، می‌توانید:\n"
            help_text += "   • **مشاهده اعضا**: لیست اعضای گروه را ببینید\n"
            help_text += "   • **مشاهده حضور و غیاب**: وضعیت حضور و غیاب اعضا را ببینید\n"
            help_text += "   • **حضور و غیاب سریع**: به سرعت وضعیت حضور اعضا را تغییر دهید\n\n"
            help_text += "⚠️ توجه: فقط مدیران و مربیان مجاز به استفاده از این امکانات هستند.\n"
        else:
            # راهنمای گروه
            help_text += "**🔹 دستورات قابل استفاده در گروه:**\n\n"
            help_text += "1️⃣ **/عضو**: نمایش لیست اعضای گروه و ثبت کاربر جدید\n"
            help_text += "2️⃣ **/help** یا **/راهنما**: نمایش این راهنما\n\n"
            help_text += "**🔸 نکات مهم:**\n"
            help_text += "• برای استفاده کامل از امکانات ربات، لطفاً آن را به عنوان ادمین گروه تنظیم کنید.\n"
            help_text += "• مدیران و مربیان می‌توانند در چت خصوصی با ربات، امکانات بیشتری را مشاهده کنند.\n"
        
        self.send_message(chat_id, help_text)
    
    def handle_new_chat_member(self, message):
        # وقتی ربات به گروه اضافه می‌شه
        chat_id = message["chat"]["id"]
        chat_title = message["chat"].get("title", "بدون عنوان")
        invite_link = self.get_group_invite_link(chat_id)
        new_members = message.get("new_chat_members", [])
        for member in new_members:
            if member["id"] == 1778171143:  # user_id ربات
                print(f"Bot added to group: chat_id={chat_id}, title={chat_title}, invite_link={invite_link}")
                welcome_text = """🎉 **ربات مدیریت گروه و حضور و غیاب فعال شد!**

📋 **راهنمای استفاده:**
• برای ثبت نام و مشاهده لیست اعضا از دستور /عضو استفاده کنید.
• مدیران و مربیان می‌توانند با ارسال /عضو یا /group در چت خصوصی با ربات، لیست گروه‌ها و اعضا را مشاهده کنند.
• امکان حضور و غیاب سریع برای مدیران و مربیان فراهم شده است.
• لطفاً مرا به عنوان ادمین گروه تنظیم کنید تا بتوانم به تمام امکانات دسترسی داشته باشم.

🔰 برای شروع، لطفاً دستور /عضو را در گروه ارسال کنید.
🔸 برای دریافت راهنمایی بیشتر، دستور /help را ارسال کنید."""
                self.send_message(chat_id, welcome_text)
                # دریافت و ذخیره اطلاعات اعضای گروه
                members = self.get_group_members(chat_id)
                
                # ارسال پیام تأیید دریافت اعضا
                if members:
                    confirm_text = f"✅ اطلاعات {len(members)} عضو گروه با موفقیت ثبت شد."
                    self.send_message(chat_id, confirm_text)