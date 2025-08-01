import json
import requests
from config import BOT_TOKEN, BASE_URL, AUTHORIZED_USER_IDS, ADMIN_USER_ID
import jdatetime

class TeacherManagementModule:
    def __init__(self, bot):
        self.bot = bot
        self.teachers = {}
        self.current_page = 1
        self.items_per_page = 5
        self.add_teacher_state = {}
        self.edit_teacher_state = {}
        
    def send_message(self, chat_id, text, reply_markup=None):
        # ارسال پیام به کاربر
        params = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
            
        return self.bot.sendMessage(params)
    
    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        # ویرایش پیام
        params = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
            
        return self.bot.editMessageText(params)
    
    def answer_callback_query(self, callback_query_id, text=None, show_alert=False):
        # پاسخ به callback query
        params = {
            "callback_query_id": callback_query_id,
            "show_alert": show_alert
        }
        
        if text:
            params["text"] = text
            
        return self.bot.answerCallbackQuery(params)
    
    def is_admin(self, user_id):
        # بررسی اینکه آیا کاربر مدیر است یا خیر
        return user_id == ADMIN_USER_ID
    
    def is_authorized(self, user_id):
        # بررسی اینکه آیا کاربر مجاز است یا خیر (مدیر یا مربی)
        return self.is_admin(user_id) or user_id in AUTHORIZED_USER_IDS
    
    def get_persian_date(self):
        # دریافت تاریخ شمسی
        now = jdatetime.datetime.now()
        return now.strftime("%Y/%m/%d")
    
    def add_teacher(self, teacher_id, name, subject, cost, group_link):
        # اضافه کردن مربی جدید
        self.teachers[teacher_id] = {
            "name": name,
            "subject": subject,
            "cost": cost,
            "group_link": group_link,
            "created_at": self.get_persian_date()
        }
        
        # اضافه کردن مربی به لیست مربیان مجاز
        if teacher_id not in AUTHORIZED_USER_IDS:
            AUTHORIZED_USER_IDS.append(teacher_id)
        
        return True
    
    def delete_teacher(self, teacher_id):
        # حذف مربی
        if teacher_id in self.teachers:
            del self.teachers[teacher_id]
            
            # حذف مربی از لیست مربیان مجاز
            if teacher_id in AUTHORIZED_USER_IDS:
                AUTHORIZED_USER_IDS.remove(teacher_id)
            
            return True
        return False
    
    def get_teachers(self):
        # دریافت لیست مربیان
        return self.teachers
    
    def get_teacher(self, teacher_id):
        # دریافت اطلاعات یک مربی خاص
        return self.teachers.get(teacher_id)
    
    def get_teachers_keyboard(self, page=1):
        # ایجاد کیبورد لیست مربیان با قابلیت صفحه‌بندی
        keyboard = []
        
        # دریافت لیست مربیان
        teachers = self.get_teachers()
        
        # تعداد کل مربیان
        total_teachers = len(teachers)
        
        # تعداد کل صفحات
        total_pages = (total_teachers + self.items_per_page - 1) // self.items_per_page
        
        # اگر صفحه درخواستی بیشتر از تعداد کل صفحات باشد، صفحه آخر را نمایش می‌دهیم
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        # اگر صفحه درخواستی کمتر از 1 باشد، صفحه اول را نمایش می‌دهیم
        if page < 1:
            page = 1
        
        # ذخیره صفحه فعلی
        self.current_page = page
        
        # محاسبه شاخص شروع و پایان
        start_index = (page - 1) * self.items_per_page
        end_index = min(start_index + self.items_per_page, total_teachers)
        
        # تبدیل دیکشنری به لیست
        teachers_list = list(teachers.items())
        
        # نمایش مربیان صفحه فعلی
        for i in range(start_index, end_index):
            teacher_id, teacher_data = teachers_list[i]
            name = teacher_data.get("name", "")
            subject = teacher_data.get("subject", "")
            button_text = f"👨‍🏫 {name} - {subject}"
            keyboard.append([{"text": button_text, "callback_data": f"view_teacher_{teacher_id}"}])
        
        # دکمه‌های ناوبری صفحات
        navigation = []
        
        if total_pages > 1:
            # دکمه صفحه قبل
            if page > 1:
                navigation.append({"text": "⬅️ صفحه قبل", "callback_data": f"teachers_page_{page - 1}"})
            
            # شماره صفحه فعلی
            navigation.append({"text": f"📄 {page}/{total_pages}", "callback_data": "noop"})
            
            # دکمه صفحه بعد
            if page < total_pages:
                navigation.append({"text": "➡️ صفحه بعد", "callback_data": f"teachers_page_{page + 1}"})
            
            keyboard.append(navigation)
        
        # دکمه‌های اضافه کردن مربی جدید و بازگشت به منوی اصلی
        keyboard.append([{"text": "➕ افزودن مربی جدید", "callback_data": "add_teacher"}])
        keyboard.append([{"text": "🏠 بازگشت به منوی اصلی", "callback_data": "main_menu"}])
        
        return {"inline_keyboard": keyboard}
    
    def get_teacher_details_keyboard(self, teacher_id):
        # ایجاد کیبورد جزئیات مربی
        keyboard = [
            [{"text": "✏️ ویرایش اطلاعات", "callback_data": f"edit_teacher_{teacher_id}"}],
            [{"text": "❌ حذف مربی", "callback_data": f"delete_teacher_{teacher_id}"}],
            [{"text": "👥 مشاهده گروه‌ها", "callback_data": f"view_teacher_groups_{teacher_id}"}],
            [{"text": "⬅️ بازگشت به لیست مربیان", "callback_data": "teachers_menu"}],
            [{"text": "🏠 بازگشت به منوی اصلی", "callback_data": "main_menu"}]
        ]
        
        return {"inline_keyboard": keyboard}
    
    def get_teacher_edit_keyboard(self, teacher_id):
        # ایجاد کیبورد ویرایش مربی
        keyboard = [
            [{"text": "✏️ ویرایش نام", "callback_data": f"edit_teacher_{teacher_id}_name"}],
            [{"text": "✏️ ویرایش موضوع", "callback_data": f"edit_teacher_{teacher_id}_subject"}],
            [{"text": "✏️ ویرایش هزینه", "callback_data": f"edit_teacher_{teacher_id}_cost"}],
            [{"text": "✏️ ویرایش لینک گروه", "callback_data": f"edit_teacher_{teacher_id}_group_link"}],
            [{"text": "⬅️ بازگشت به جزئیات مربی", "callback_data": f"view_teacher_{teacher_id}"}]
        ]
        
        return {"inline_keyboard": keyboard}
    
    def get_confirm_delete_keyboard(self, teacher_id):
        # ایجاد کیبورد تأیید حذف مربی
        keyboard = [
            [{"text": "✅ بله، حذف شود", "callback_data": f"confirm_delete_teacher_{teacher_id}"}],
            [{"text": "❌ خیر، انصراف", "callback_data": f"view_teacher_{teacher_id}"}]
        ]
        
        return {"inline_keyboard": keyboard}
    
    def format_teacher_details(self, teacher_id, teacher_data):
        # فرمت‌بندی اطلاعات مربی
        name = teacher_data.get("name", "")
        subject = teacher_data.get("subject", "")
        cost = teacher_data.get("cost", "")
        group_link = teacher_data.get("group_link", "")
        created_at = teacher_data.get("created_at", "")
        
        text = f"👨‍🏫 **اطلاعات مربی**\n\n"
        text += f"🆔 شناسه: `{teacher_id}`\n"
        text += f"👤 نام: {name}\n"
        text += f"📚 موضوع: {subject}\n"
        text += f"💰 هزینه: {cost}\n"
        text += f"🔗 لینک گروه: {group_link}\n"
        text += f"📅 تاریخ ثبت: {created_at}\n"
        
        return text

    def handle_message(self, message):
        # پردازش پیام‌های متنی
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        
        # بررسی وضعیت اضافه کردن مربی جدید
        if user_id in self.add_teacher_state:
            state = self.add_teacher_state[user_id]
            
            if state["step"] == "name":
                # دریافت نام مربی
                state["name"] = text
                state["step"] = "subject"
                
                self.send_message(chat_id, "📚 لطفاً موضوع تدریس مربی را وارد کنید:")
                return True
            elif state["step"] == "subject":
                # دریافت موضوع تدریس
                state["subject"] = text
                state["step"] = "cost"
                
                self.send_message(chat_id, "💰 لطفاً هزینه کلاس را وارد کنید:")
                return True
            elif state["step"] == "cost":
                # دریافت هزینه کلاس
                state["cost"] = text
                state["step"] = "group_link"
                
                self.send_message(chat_id, "🔗 لطفاً لینک گروه را وارد کنید:")
                return True
            elif state["step"] == "group_link":
                # دریافت لینک گروه
                state["group_link"] = text
                
                # اضافه کردن مربی جدید
                teacher_id = state["teacher_id"]
                name = state["name"]
                subject = state["subject"]
                cost = state["cost"]
                group_link = state["group_link"]
                
                self.add_teacher(teacher_id, name, subject, cost, group_link)
                
                # پاک کردن وضعیت
                del self.add_teacher_state[user_id]
                
                # ارسال پیام موفقیت
                success_text = f"✅ مربی جدید با موفقیت اضافه شد:\n\n"
                success_text += f"👤 نام: {name}\n"
                success_text += f"📚 موضوع: {subject}\n"
                success_text += f"💰 هزینه: {cost}\n"
                success_text += f"🔗 لینک گروه: {group_link}\n"
                
                self.send_message(chat_id, success_text, self.get_teachers_keyboard())
                return True
        
        # بررسی وضعیت ویرایش مربی
        if user_id in self.edit_teacher_state:
            state = self.edit_teacher_state[user_id]
            
            # دریافت اطلاعات مربی
            teacher_id = state["teacher_id"]
            field = state["field"]
            teacher_data = self.get_teacher(teacher_id)
            
            if teacher_data:
                # بروزرسانی فیلد مورد نظر
                teacher_data[field] = text
                
                # پاک کردن وضعیت
                del self.edit_teacher_state[user_id]
                
                # ارسال پیام موفقیت
                field_name = {
                    "name": "نام",
                    "subject": "موضوع",
                    "cost": "هزینه",
                    "group_link": "لینک گروه"
                }.get(field, field)
                
                success_text = f"✅ {field_name} مربی با موفقیت بروزرسانی شد.\n\n"
                success_text += self.format_teacher_details(teacher_id, teacher_data)
                
                self.send_message(chat_id, success_text, self.get_teacher_details_keyboard(teacher_id))
                return True
        
        # پردازش دستورات
        if text == "/teachers" or text == "مربیان":
            # فقط مدیر می‌تواند به این بخش دسترسی داشته باشد
            if not self.is_admin(user_id):
                self.send_message(chat_id, "❌ شما اجازه دسترسی به این بخش را ندارید!")
                return True
            
            # ارسال منوی مربیان
            text = "👨‍🏫 **مدیریت مربیان**\n\nلطفاً یکی از مربیان را انتخاب کنید یا مربی جدیدی اضافه کنید:"
            self.send_message(chat_id, text, self.get_teachers_keyboard())
            return True
        
        return False

    def handle_callback(self, callback):
        # پردازش درخواست‌های callback
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        user_id = callback["from"]["id"]
        data = callback["data"]
        callback_query_id = callback["id"]
        
        # فقط مدیر می‌تواند به این بخش دسترسی داشته باشد
        if not self.is_admin(user_id):
            self.answer_callback_query(callback_query_id, "❌ شما اجازه دسترسی به این بخش را ندارید!")
            return False
        
        if data == "teachers_menu" or data.startswith("teachers_page_"):
            # نمایش لیست مربیان
            page = 1
            if data.startswith("teachers_page_"):
                try:
                    page = int(data.split("_")[-1])
                except:
                    page = 1
            
            text = "👨‍🏫 **مدیریت مربیان**\n\nلطفاً یکی از مربیان را انتخاب کنید یا مربی جدیدی اضافه کنید:"
            self.edit_message(chat_id, message_id, text, self.get_teachers_keyboard(page))
            self.answer_callback_query(callback_query_id)
            return True
        elif data.startswith("view_teacher_"):
            # نمایش اطلاعات مربی
            teacher_id = int(data.split("_")[-1])
            teacher_data = self.get_teacher(teacher_id)
            
            if teacher_data:
                text = self.format_teacher_details(teacher_id, teacher_data)
                self.edit_message(chat_id, message_id, text, self.get_teacher_details_keyboard(teacher_id))
                self.answer_callback_query(callback_query_id)
                return True
            else:
                self.answer_callback_query(callback_query_id, "❌ مربی مورد نظر یافت نشد!")
                return True
        elif data.startswith("edit_teacher_"):
            # ویرایش اطلاعات مربی
            parts = data.split("_")
            teacher_id = int(parts[2])
            teacher_data = self.get_teacher(teacher_id)
            
            if not teacher_data:
                self.answer_callback_query(callback_query_id, "❌ مربی مورد نظر یافت نشد!")
                return True
            
            if len(parts) == 3:
                # نمایش منوی ویرایش
                text = f"✏️ **ویرایش اطلاعات مربی**\n\n"
                text += self.format_teacher_details(teacher_id, teacher_data)
                text += "\nلطفاً فیلد مورد نظر برای ویرایش را انتخاب کنید:"
                
                self.edit_message(chat_id, message_id, text, self.get_teacher_edit_keyboard(teacher_id))
                self.answer_callback_query(callback_query_id)
                return True
            elif len(parts) == 4:
                # ویرایش فیلد خاص
                field = parts[3]
                
                if field in ["name", "subject", "cost", "group_link"]:
                    # ذخیره وضعیت ویرایش
                    self.edit_teacher_state[user_id] = {
                        "teacher_id": teacher_id,
                        "field": field
                    }
                    
                    # درخواست مقدار جدید
                    field_name = {
                        "name": "نام",
                        "subject": "موضوع",
                        "cost": "هزینه",
                        "group_link": "لینک گروه"
                    }.get(field, field)
                    
                    current_value = teacher_data.get(field, "")
                    text = f"✏️ **ویرایش {field_name} مربی**\n\n"
                    text += f"مقدار فعلی: {current_value}\n\n"
                    text += f"لطفاً مقدار جدید برای {field_name} را وارد کنید:"
                    
                    self.edit_message(chat_id, message_id, text)
                    self.answer_callback_query(callback_query_id)
                    return True
                else:
                    self.answer_callback_query(callback_query_id, "❌ فیلد نامعتبر!")
                    return True
        elif data.startswith("delete_teacher_"):
            # حذف مربی
            teacher_id = int(data.split("_")[-1])
            teacher_data = self.get_teacher(teacher_id)
            
            if teacher_data:
                name = teacher_data.get("name", "")
                text = f"❌ **حذف مربی**\n\n"
                text += f"آیا از حذف مربی «{name}» اطمینان دارید؟\n"
                text += "این عملیات غیرقابل بازگشت است!\n"
                
                self.edit_message(chat_id, message_id, text, self.get_confirm_delete_keyboard(teacher_id))
                self.answer_callback_query(callback_query_id)
                return True
            else:
                self.answer_callback_query(callback_query_id, "❌ مربی مورد نظر یافت نشد!")
                return True
        elif data.startswith("confirm_delete_teacher_"):
            # تأیید حذف مربی
            teacher_id = int(data.split("_")[-1])
            teacher_data = self.get_teacher(teacher_id)
            
            if teacher_data:
                name = teacher_data.get("name", "")
                
                # حذف مربی
                self.delete_teacher(teacher_id)
                
                text = f"✅ مربی «{name}» با موفقیت حذف شد.\n\n"
                text += "👨‍🏫 **مدیریت مربیان**\n\nلطفاً یکی از مربیان را انتخاب کنید یا مربی جدیدی اضافه کنید:"
                
                self.edit_message(chat_id, message_id, text, self.get_teachers_keyboard())
                self.answer_callback_query(callback_query_id, f"✅ مربی «{name}» حذف شد")
                return True
            else:
                self.answer_callback_query(callback_query_id, "❌ مربی مورد نظر یافت نشد!")
                return True
        elif data == "add_teacher":
            # اضافه کردن مربی جدید
            text = "👨‍🏫 **افزودن مربی جدید**\n\n"
            text += "لطفاً به ترتیب اطلاعات زیر را وارد کنید:\n"
            text += "1. نام مربی\n"
            text += "2. موضوع تدریس\n"
            text += "3. هزینه کلاس\n"
            text += "4. لینک گروه\n\n"
            text += "👤 لطفاً نام مربی را وارد کنید:"
            
            # ذخیره وضعیت اضافه کردن مربی
            self.add_teacher_state[user_id] = {
                "step": "name",
                "teacher_id": user_id  # فعلاً از آیدی کاربر استفاده می‌کنیم
            }
            
            self.edit_message(chat_id, message_id, text)
            self.answer_callback_query(callback_query_id)
            return True
        elif data.startswith("view_teacher_groups_"):
            # نمایش گروه‌های مربی
            teacher_id = int(data.split("_")[-1])
            teacher_data = self.get_teacher(teacher_id)
            
            if teacher_data:
                name = teacher_data.get("name", "")
                group_link = teacher_data.get("group_link", "")
                
                text = f"👥 **گروه‌های مربی {name}**\n\n"
                
                if group_link:
                    text += f"🔗 لینک گروه: {group_link}\n"
                else:
                    text += "❌ هیچ گروهی برای این مربی ثبت نشده است.\n"
                
                self.edit_message(chat_id, message_id, text, self.get_teacher_details_keyboard(teacher_id))
                self.answer_callback_query(callback_query_id)
                return True
            else:
                self.answer_callback_query(callback_query_id, "❌ مربی مورد نظر یافت نشد!")
                return True
        elif data == "noop":
            # بدون عملیات
            self.answer_callback_query(callback_query_id)
            return True
        elif data == "main_menu":
            # بازگشت به منوی اصلی
            # این callback در ماژول group_management پردازش خواهد شد
            return False
        
        return False