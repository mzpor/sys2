import json
import os
import jdatetime
from typing import Dict, List, Tuple, Optional, Any

class TeacherManagementModule:
    def __init__(self, bot, admin_id: int, authorized_users: List[int]):
        """
        Initialize the TeacherManagementModule.
        
        Args:
            bot: The bot instance
            admin_id: The admin user ID
            authorized_users: List of authorized user IDs (teachers)
        """
        self.bot = bot
        self.admin_id = admin_id
        self.authorized_users = authorized_users
        self.teachers_data_file = "teachers_data.json"
        self.teachers = self._load_teachers()
        
    def _load_teachers(self) -> Dict[str, Dict[str, Any]]:
        """
        Load teachers data from JSON file or create empty dict if file doesn't exist.
        
        Returns:
            Dict containing teachers data
        """
        if os.path.exists(self.teachers_data_file):
            try:
                with open(self.teachers_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_teachers(self) -> None:
        """
        Save teachers data to JSON file.
        """
        with open(self.teachers_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.teachers, f, ensure_ascii=False, indent=4)
    
    def send_message(self, chat_id: int, text: str, reply_markup=None) -> Dict:
        """
        Send a message to a chat.
        
        Args:
            chat_id: The chat ID to send the message to
            text: The text of the message
            reply_markup: Optional reply markup for the message
            
        Returns:
            The response from the bot API
        """
        params = {
            "chat_id": chat_id,
            "text": text
        }
        
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
            
        return self.bot.sendMessage(params)
    
    def edit_message_text(self, chat_id: int, message_id: int, text: str, reply_markup=None) -> Dict:
        """
        Edit a message's text.
        
        Args:
            chat_id: The chat ID of the message
            message_id: The message ID to edit
            text: The new text of the message
            reply_markup: Optional new reply markup for the message
            
        Returns:
            The response from the bot API
        """
        params = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
        
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
            
        return self.bot.editMessageText(params)
    
    def answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = False) -> Dict:
        """
        Answer a callback query.
        
        Args:
            callback_query_id: The callback query ID to answer
            text: Optional text to show to the user
            show_alert: Whether to show the text as an alert
            
        Returns:
            The response from the bot API
        """
        params = {
            "callback_query_id": callback_query_id
        }
        
        if text:
            params["text"] = text
            
        if show_alert:
            params["show_alert"] = show_alert
            
        return self.bot.answerCallbackQuery(params)
    
    def is_admin(self, user_id: int) -> bool:
        """
        Check if a user is an admin.
        
        Args:
            user_id: The user ID to check
            
        Returns:
            True if the user is an admin, False otherwise
        """
        return user_id == self.admin_id
    
    def is_authorized(self, user_id: int) -> bool:
        """
        Check if a user is authorized (admin or teacher).
        
        Args:
            user_id: The user ID to check
            
        Returns:
            True if the user is authorized, False otherwise
        """
        return user_id == self.admin_id or user_id in self.authorized_users
    
    def get_persian_date(self) -> str:
        """
        Get the current Persian date.
        
        Returns:
            String representation of the current Persian date
        """
        now = jdatetime.datetime.now()
        return now.strftime("%Y/%m/%d")
    
    def add_teacher(self, teacher_id: str, name: str, subject: str, cost: str, group_link: str) -> bool:
        """
        Add a new teacher or update an existing one.
        
        Args:
            teacher_id: Unique ID for the teacher
            name: Teacher's name
            subject: Subject taught by the teacher
            cost: Cost of the teacher's lessons
            group_link: Link to the teacher's group
            
        Returns:
            True if the teacher was added/updated successfully, False otherwise
        """
        try:
            self.teachers[teacher_id] = {
                "name": name,
                "subject": subject,
                "cost": cost,
                "group_link": group_link,
                "added_date": self.get_persian_date()
            }
            self._save_teachers()
            return True
        except Exception:
            return False
    
    def delete_teacher(self, teacher_id: str) -> bool:
        """
        Delete a teacher.
        
        Args:
            teacher_id: ID of the teacher to delete
            
        Returns:
            True if the teacher was deleted successfully, False otherwise
        """
        try:
            if teacher_id in self.teachers:
                del self.teachers[teacher_id]
                self._save_teachers()
                return True
            return False
        except Exception:
            return False
    
    def get_teacher(self, teacher_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a teacher's data.
        
        Args:
            teacher_id: ID of the teacher to get
            
        Returns:
            Dict containing the teacher's data or None if the teacher doesn't exist
        """
        return self.teachers.get(teacher_id)
    
    def get_all_teachers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all teachers' data.
        
        Returns:
            Dict containing all teachers' data
        """
        return self.teachers
    
    def get_teachers_keyboard(self, page: int = 0, page_size: int = 5) -> Dict:
        """
        Get a keyboard with buttons for all teachers.
        
        Args:
            page: The page number (0-indexed)
            page_size: Number of teachers per page
            
        Returns:
            Dict containing the inline keyboard markup
        """
        keyboard = []
        teachers_list = list(self.teachers.items())
        total_pages = (len(teachers_list) + page_size - 1) // page_size
        
        start_idx = page * page_size
        end_idx = min(start_idx + page_size, len(teachers_list))
        
        for teacher_id, teacher_data in teachers_list[start_idx:end_idx]:
            keyboard.append([{
                "text": f"👨‍🏫 {teacher_data['name']} - {teacher_data['subject']}",
                "callback_data": f"view_teacher_{teacher_id}"
            }])
        
        navigation = []
        if page > 0:
            navigation.append({
                "text": "« صفحه قبل",
                "callback_data": f"teachers_page_{page-1}"
            })
            
        navigation.append({
            "text": f"📄 {page+1}/{total_pages or 1}",
            "callback_data": "noop"
        })
        
        if page < total_pages - 1:
            navigation.append({
                "text": "صفحه بعد »",
                "callback_data": f"teachers_page_{page+1}"
            })
            
        keyboard.append(navigation)
        
        keyboard.append([{
            "text": "➕ افزودن مربی جدید",
            "callback_data": "add_teacher"
        }])
        
        keyboard.append([{
            "text": "🏠 بازگشت به منوی اصلی",
            "callback_data": "main_menu"
        }])
        
        return {"inline_keyboard": keyboard}
    
    def get_teacher_details_keyboard(self, teacher_id: str) -> Dict:
        """
        Get a keyboard with options for a specific teacher.
        
        Args:
            teacher_id: ID of the teacher
            
        Returns:
            Dict containing the inline keyboard markup
        """
        keyboard = [
            [{
                "text": "✏️ ویرایش اطلاعات",
                "callback_data": f"edit_teacher_{teacher_id}"
            }],
            [{
                "text": "❌ حذف مربی",
                "callback_data": f"delete_teacher_{teacher_id}"
            }],
            [{
                "text": "👥 مشاهده گروه‌ها",
                "callback_data": f"view_teacher_groups_{teacher_id}"
            }],
            [{
                "text": "⬅️ بازگشت به لیست مربیان",
                "callback_data": "teachers_menu"
            }],
            [{
                "text": "🏠 بازگشت به منوی اصلی",
                "callback_data": "main_menu"
            }]
        ]
        
        return {"inline_keyboard": keyboard}
    
    def get_teacher_edit_keyboard(self, teacher_id: str) -> Dict:
        """
        Get a keyboard for editing a teacher's information.
        
        Args:
            teacher_id: ID of the teacher
            
        Returns:
            Dict containing the inline keyboard markup
        """
        keyboard = [
            [{
                "text": "✏️ ویرایش نام",
                "callback_data": f"edit_teacher_name_{teacher_id}"
            }],
            [{
                "text": "✏️ ویرایش درس",
                "callback_data": f"edit_teacher_subject_{teacher_id}"
            }],
            [{
                "text": "✏️ ویرایش هزینه",
                "callback_data": f"edit_teacher_cost_{teacher_id}"
            }],
            [{
                "text": "✏️ ویرایش لینک گروه",
                "callback_data": f"edit_teacher_link_{teacher_id}"
            }],
            [{
                "text": "⬅️ بازگشت به جزئیات مربی",
                "callback_data": f"view_teacher_{teacher_id}"
            }]
        ]
        
        return {"inline_keyboard": keyboard}
    
    def get_confirm_delete_keyboard(self, teacher_id: str) -> Dict:
        """
        Get a keyboard for confirming teacher deletion.
        
        Args:
            teacher_id: ID of the teacher
            
        Returns:
            Dict containing the inline keyboard markup
        """
        keyboard = [
            [{
                "text": "✅ بله، حذف شود",
                "callback_data": f"confirm_delete_teacher_{teacher_id}"
            }],
            [{
                "text": "❌ خیر، انصراف",
                "callback_data": f"view_teacher_{teacher_id}"
            }]
        ]
        
        return {"inline_keyboard": keyboard}
    
    def format_teacher_details(self, teacher_id: str, teacher_data: Dict[str, Any]) -> str:
        """
        Format a teacher's details for display.
        
        Args:
            teacher_id: ID of the teacher
            teacher_data: Dict containing the teacher's data
            
        Returns:
            Formatted string with the teacher's details
        """
        return f"🧑‍🏫 *اطلاعات مربی*\n\n" \
               f"🆔 شناسه: `{teacher_id}`\n" \
               f"👤 نام: *{teacher_data['name']}*\n" \
               f"📚 درس: *{teacher_data['subject']}*\n" \
               f"💰 هزینه: *{teacher_data['cost']}*\n" \
               f"🔗 لینک گروه: {teacher_data['group_link']}\n" \
               f"📅 تاریخ ثبت: *{teacher_data.get('added_date', 'نامشخص')}*"
    
    def handle_message(self, message: Dict) -> None:
        """
        Handle incoming messages.
        
        Args:
            message: The message to handle
        """
        chat_id = message.get("chat", {}).get("id")
        user_id = message.get("from", {}).get("id")
        text = message.get("text", "")
        
        # Only admin can access teacher management through messages
        if not self.is_admin(user_id):
            return
        
        if text == "/teachers" or text == "مربیان":
            self.send_teachers_menu(chat_id)
    
    def send_teachers_menu(self, chat_id: int) -> None:
        """
        Send the teachers menu.
        
        Args:
            chat_id: The chat ID to send the menu to
        """
        keyboard = self.get_teachers_keyboard()
        text = "👨‍🏫 *مدیریت مربیان*\n\n" \
               "از منوی زیر می‌توانید مربیان را مدیریت کنید.\n" \
               "برای مشاهده جزئیات هر مربی، روی نام آن کلیک کنید.\n" \
               "برای افزودن مربی جدید، روی دکمه «افزودن مربی جدید» کلیک کنید."
        
        self.send_message(chat_id, text, keyboard)
    
    def handle_callback(self, callback_query: Dict) -> None:
        """
        Handle callback queries.
        
        Args:
            callback_query: The callback query to handle
        """
        callback_data = callback_query.get("data", "")
        user_id = callback_query.get("from", {}).get("id")
        message = callback_query.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        message_id = message.get("message_id")
        callback_id = callback_query.get("id")
        
        # Only admin can access teacher management
        if not self.is_admin(user_id):
            self.answer_callback_query(callback_id, "شما دسترسی به این بخش را ندارید.", True)
            return
        
        # Handle different callback data
        if callback_data == "teachers_menu":
            keyboard = self.get_teachers_keyboard()
            text = "👨‍🏫 *مدیریت مربیان*\n\n" \
                   "از منوی زیر می‌توانید مربیان را مدیریت کنید.\n" \
                   "برای مشاهده جزئیات هر مربی، روی نام آن کلیک کنید.\n" \
                   "برای افزودن مربی جدید، روی دکمه «افزودن مربی جدید» کلیک کنید."
            
            self.edit_message_text(chat_id, message_id, text, keyboard)
            self.answer_callback_query(callback_id)
            
        elif callback_data.startswith("teachers_page_"):
            page = int(callback_data.split("_")[-1])
            keyboard = self.get_teachers_keyboard(page)
            text = "👨‍🏫 *مدیریت مربیان*\n\n" \
                   "از منوی زیر می‌توانید مربیان را مدیریت کنید.\n" \
                   "برای مشاهده جزئیات هر مربی، روی نام آن کلیک کنید.\n" \
                   "برای افزودن مربی جدید، روی دکمه «افزودن مربی جدید» کلیک کنید."
            
            self.edit_message_text(chat_id, message_id, text, keyboard)
            self.answer_callback_query(callback_id)
            
        elif callback_data.startswith("view_teacher_"):
            teacher_id = callback_data.split("_")[-1]
            teacher_data = self.get_teacher(teacher_id)
            
            if teacher_data:
                text = self.format_teacher_details(teacher_id, teacher_data)
                keyboard = self.get_teacher_details_keyboard(teacher_id)
                
                self.edit_message_text(chat_id, message_id, text, keyboard)
                self.answer_callback_query(callback_id)
            else:
                self.answer_callback_query(callback_id, "مربی مورد نظر یافت نشد.", True)
                
        elif callback_data.startswith("edit_teacher_"):
            if callback_data.startswith("edit_teacher_name_") or \
               callback_data.startswith("edit_teacher_subject_") or \
               callback_data.startswith("edit_teacher_cost_") or \
               callback_data.startswith("edit_teacher_link_"):
                # Handle specific field edit
                parts = callback_data.split("_")
                field = parts[2]
                teacher_id = parts[3]
                
                teacher_data = self.get_teacher(teacher_id)
                if not teacher_data:
                    self.answer_callback_query(callback_id, "مربی مورد نظر یافت نشد.", True)
                    return
                
                field_names = {
                    "name": "نام",
                    "subject": "درس",
                    "cost": "هزینه",
                    "link": "لینک گروه"
                }
                
                # Store the current edit state in user data (would need to be implemented)
                # For now, just show a message asking for the new value
                text = f"لطفاً {field_names[field]} جدید را وارد کنید:\n\n" \
                       f"مقدار فعلی: {teacher_data.get(field if field != 'link' else 'group_link', 'نامشخص')}"
                
                keyboard = {
                    "inline_keyboard": [
                        [{
                            "text": "⬅️ انصراف و بازگشت",
                            "callback_data": f"view_teacher_{teacher_id}"
                        }]
                    ]
                }
                
                self.edit_message_text(chat_id, message_id, text, keyboard)
                self.answer_callback_query(callback_id)
                
                # In a real implementation, you would now wait for the user's text input
                # and update the teacher's data when received
                
            else:
                # General edit menu
                teacher_id = callback_data.split("_")[-1]
                teacher_data = self.get_teacher(teacher_id)
                
                if teacher_data:
                    text = f"✏️ *ویرایش اطلاعات مربی*\n\n" \
                           f"👤 نام: *{teacher_data['name']}*\n" \
                           f"📚 درس: *{teacher_data['subject']}*\n" \
                           f"💰 هزینه: *{teacher_data['cost']}*\n" \
                           f"🔗 لینک گروه: {teacher_data['group_link']}\n\n" \
                           f"لطفاً فیلد مورد نظر برای ویرایش را انتخاب کنید:"
                    
                    keyboard = self.get_teacher_edit_keyboard(teacher_id)
                    
                    self.edit_message_text(chat_id, message_id, text, keyboard)
                    self.answer_callback_query(callback_id)
                else:
                    self.answer_callback_query(callback_id, "مربی مورد نظر یافت نشد.", True)
                    
        elif callback_data.startswith("delete_teacher_"):
            teacher_id = callback_data.split("_")[-1]
            teacher_data = self.get_teacher(teacher_id)
            
            if teacher_data:
                text = f"❌ *حذف مربی*\n\n" \
                       f"آیا از حذف مربی زیر اطمینان دارید؟\n\n" \
                       f"👤 نام: *{teacher_data['name']}*\n" \
                       f"📚 درس: *{teacher_data['subject']}*"
                
                keyboard = self.get_confirm_delete_keyboard(teacher_id)
                
                self.edit_message_text(chat_id, message_id, text, keyboard)
                self.answer_callback_query(callback_id)
            else:
                self.answer_callback_query(callback_id, "مربی مورد نظر یافت نشد.", True)
                
        elif callback_data.startswith("confirm_delete_teacher_"):
            teacher_id = callback_data.split("_")[-1]
            
            if self.delete_teacher(teacher_id):
                self.answer_callback_query(callback_id, "مربی با موفقیت حذف شد.", True)
                
                # Return to teachers menu
                keyboard = self.get_teachers_keyboard()
                text = "👨‍🏫 *مدیریت مربیان*\n\n" \
                       "از منوی زیر می‌توانید مربیان را مدیریت کنید.\n" \
                       "برای مشاهده جزئیات هر مربی، روی نام آن کلیک کنید.\n" \
                       "برای افزودن مربی جدید، روی دکمه «افزودن مربی جدید» کلیک کنید."
                
                self.edit_message_text(chat_id, message_id, text, keyboard)
            else:
                self.answer_callback_query(callback_id, "خطا در حذف مربی.", True)
                
        elif callback_data == "add_teacher":
            # In a real implementation, you would start a conversation to collect teacher info
            text = "➕ *افزودن مربی جدید*\n\n" \
                   "لطفاً اطلاعات مربی جدید را به ترتیب زیر وارد کنید:\n\n" \
                   "1️⃣ نام مربی\n" \
                   "2️⃣ نام درس\n" \
                   "3️⃣ هزینه درس\n" \
                   "4️⃣ لینک گروه\n\n" \
                   "لطفاً نام مربی را وارد کنید:"
            
            keyboard = {
                "inline_keyboard": [
                    [{
                        "text": "⬅️ انصراف و بازگشت",
                        "callback_data": "teachers_menu"
                    }]
                ]
            }
            
            self.edit_message_text(chat_id, message_id, text, keyboard)
            self.answer_callback_query(callback_id)
            
            # In a real implementation, you would now wait for the user's text input
            # and collect all the required information before adding the teacher
            
        elif callback_data.startswith("view_teacher_groups_"):
            teacher_id = callback_data.split("_")[-1]
            teacher_data = self.get_teacher(teacher_id)
            
            if teacher_data:
                # In a real implementation, you would fetch the teacher's groups
                text = f"👥 *گروه‌های مربی {teacher_data['name']}*\n\n" \
                       f"لینک گروه: {teacher_data['group_link']}"
                
                keyboard = {
                    "inline_keyboard": [
                        [{
                            "text": "⬅️ بازگشت به جزئیات مربی",
                            "callback_data": f"view_teacher_{teacher_id}"
                        }]
                    ]
                }
                
                self.edit_message_text(chat_id, message_id, text, keyboard)
                self.answer_callback_query(callback_id)
            else:
                self.answer_callback_query(callback_id, "مربی مورد نظر یافت نشد.", True)
                
        elif callback_data == "noop":
            # No operation, just answer the callback query
            self.answer_callback_query(callback_id)
            
        elif callback_data == "main_menu":
            # This should be handled by the main bot to return to the main menu
            self.answer_callback_query(callback_id)
            # The main bot should handle the main_menu callback