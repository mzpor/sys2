import requests
import time
from modules.attendance.attendance import AttendanceModule
from modules.group_management.group_management import GroupManagementModule
from config import BASE_URL

class SchoolBot:
    def __init__(self):
        # مقداردهی اولیه ماژول‌ها
        self.attendance = AttendanceModule()
        self.group_management = GroupManagementModule(self.attendance)
        # اتصال ماژول‌ها به یکدیگر
        self.attendance.set_group_management(self.group_management)
        # اتصال ماژول‌ها به یکدیگر
        self.attendance.set_group_management(self.group_management)

    def get_updates(self, offset=None):
        # دریافت آپدیت‌ها از API بله
        url = f"{BASE_URL}/getUpdates"
        params = {"offset": offset, "timeout": 30} if offset else {"timeout": 30}
        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching updates: {e}")
        return None

    def handle_update(self, update):
        # پردازش آپدیت‌های دریافتی
        try:
            if "message" in update:
                print(f"Processing message update: {update['message']}")
                if "new_chat_members" in update["message"]:
                    self.group_management.handle_new_chat_member(update["message"])
                else:
                    self.group_management.handle_message(update["message"])
                    self.attendance.handle_message(update["message"])
            elif "callback_query" in update:
                print(f"Processing callback update: {update['callback_query']}")
                if update["callback_query"]["data"].startswith(("admin_view_", "teacher_view_", "view_attendance_", "quick_attendance_", "group_menu")):
                    self.group_management.handle_callback(update["callback_query"])
                else:
                    self.attendance.handle_callback(update["callback_query"])
            else:
                print(f"Unknown update type: {update}")
        except Exception as e:
            print(f"Error processing update: {e}")

    def run(self):
        # حلقه اصلی بات
        offset = 0
        print("Bot started...")
        while True:
            try:
                updates = self.get_updates(offset)
                if updates and updates.get("ok") and updates.get("result"):
                    for update in updates["result"]:
                        offset = update["update_id"] + 1
                        self.handle_update(update)
                else:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Bot stopped.")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = SchoolBot()
    bot.run()