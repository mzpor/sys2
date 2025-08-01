# main.py
import requests
import json
from config import BASE_URL, BOT_TOKEN
from attendance_module import AttendanceModule
from group_management_module import GroupManagementModule
from kargah_module import KargahModule
from payment_module import PaymentModule
from registration_module import RegistrationModule

class AttendanceBot:
    def __init__(self):
        self.kargah_module = KargahModule()
        self.attendance_module = AttendanceModule(self.kargah_module)
        self.group_module = GroupManagementModule(self.attendance_module)
        self.payment_module = PaymentModule(self.kargah_module)
        self.registration_module = RegistrationModule(self.kargah_module)
        self.last_update_id = 0
        print("AttendanceBot initialized")

    def get_updates(self, offset=None):
        """دریافت آپدیت‌های جدید"""
        url = f"{BASE_URL}/getUpdates"
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting updates: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error in get_updates: {e}")
            return None

    def process_update(self, update):
        """پردازش هر آپدیت"""
        print(f"Processing update: {update}")
        
        try:
            if "message" in update:
                message = update["message"]
                
                # بررسی اعضای جدید گروه
                if "new_chat_members" in message:
                    self.group_module.handle_new_chat_member(message)
                    return
                
                # بررسی پرداخت موفق
                if "successful_payment" in message:
                    print(f"🔄 Processing successful payment for user {message['from']['id']}")
                    self.payment_module.handle_successful_payment(message)
                    return
                
                # پردازش پیام‌های متنی و contact
                user_id = message["from"]["id"]
                text = message.get("text", "")
                contact = message.get("contact")
                
                # ابتدا بررسی می‌کنیم که آیا کاربر در وضعیت registration هست
                if hasattr(self.registration_module, 'user_states') and str(user_id) in self.registration_module.user_states:
                    self.registration_module.handle_message(message)
                # سپس بررسی می‌کنیم که آیا کاربر در وضعیت payment هست
                elif hasattr(self.payment_module, 'user_states') and user_id in self.payment_module.user_states:
                    self.payment_module.handle_message(message)
                # سپس بررسی می‌کنیم که آیا کاربر در وضعیت kargah هست
                elif hasattr(self.kargah_module, 'user_states') and user_id in self.kargah_module.user_states:
                    self.kargah_module.handle_message(message)
                # سپس بررسی دستورات خاص
                elif text == "/kargah":
                    self.kargah_module.handle_message(message)
                elif text in ["/عضو", "/group"]:
                    self.group_module.handle_message(message)
                elif text == "/start":
                    # برای کاربران غیر مدیر/مربی/کمک مربی، ابتدا registration_module را بررسی کن
                    if not self.registration_module.is_admin_or_teacher(user_id):
                        self.registration_module.handle_message(message)
                    else:
                        self.payment_module.handle_message(message)
                else:
                    # برای سایر پیام‌ها، ابتدا بررسی کنیم که آیا کاربر مجاز است
                    if self.registration_module.is_admin_or_teacher(user_id):
                        # کاربر مجاز - به attendance_module بفرست
                        self.attendance_module.handle_message(message)
                    else:
                        # کاربر غیر مجاز - به registration_module بفرست
                        self.registration_module.handle_message(message)
            
            elif "callback_query" in update:
                callback = update["callback_query"]
                data = callback["data"]
                
                # تشخیص اینکه callback متعلق به کدام ماژول است
                registration_callbacks = [
                    "start_registration", "edit_name", "edit_national_id", 
                    "edit_phone", "edit_info", "final_confirm", "quran_student_panel",
                    "complete_registration"
                ]
                
                payment_callbacks = [
                    "pay_workshop_"
                ]
                
                kargah_callbacks = [
                    "kargah_list", "kargah_add", "kargah_edit", "kargah_back",
                    "kargah_view_", "kargah_edit_instructor_", "kargah_edit_cost_",
                    "kargah_edit_link_", "kargah_delete_",
                    "student_select_workshop_", "student_pay_workshop_", 
                    "student_back_to_workshops", "student_back_to_menu"
                ]
                
                group_callbacks = [
                    "group_menu", "admin_view_teachers", "admin_view_teacher_", 
                    "teacher_view_group_", "admin_view_group_", "view_attendance_group_",
                    "quick_attendance_group_", "statistics_group_", "clear_group_"
                ]
                
                is_registration_callback = any(data == cb for cb in registration_callbacks)
                is_payment_callback = any(data.startswith(cb) for cb in payment_callbacks)
                is_kargah_callback = any(data.startswith(cb) for cb in kargah_callbacks)
                is_group_callback = any(data.startswith(cb) for cb in group_callbacks)
                
                if is_registration_callback:
                    self.registration_module.handle_callback(callback)
                elif is_payment_callback:
                    self.payment_module.handle_callback(callback)
                elif is_kargah_callback:
                    self.kargah_module.handle_callback(callback)
                elif is_group_callback:
                    self.group_module.handle_callback(callback)
                else:
                    # برای سایر callback ها، ابتدا بررسی کنیم که آیا کاربر مجاز است
                    user_id = callback["from"]["id"]
                    if self.registration_module.is_admin_or_teacher(user_id):
                        # کاربر مجاز - به attendance_module بفرست
                        self.attendance_module.handle_callback(callback)
                    else:
                        # کاربر غیر مجاز - به registration_module بفرست
                        self.registration_module.handle_callback(callback)
            
            elif "pre_checkout_query" in update:
                print(f"🔄 Processing pre_checkout_query")
                self.payment_module.handle_pre_checkout_query(update["pre_checkout_query"])
        
        except Exception as e:
            print(f"Error processing update: {e}")
            import traceback
            traceback.print_exc()

    def run(self):
        """اجرای اصلی ربات"""
        print("🤖 Bot started successfully!")
        print("Waiting for messages...")
        
        while True:
            try:
                # دریافت آپدیت‌ها
                result = self.get_updates(self.last_update_id + 1)
                
                if result and result.get("ok"):
                    updates = result.get("result", [])
                    
                    for update in updates:
                        self.process_update(update)
                        self.last_update_id = update["update_id"]
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                continue

# اجرای ربات
if __name__ == "__main__":
    bot = AttendanceBot()
    bot.run()