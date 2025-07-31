import requests
import time
from modules.attendance.attendance import AttendanceModule
from modules.config import BASE_URL

class SchoolBot:
    def __init__(self):
        self.attendance = AttendanceModule()

    def get_updates(self, offset=None):
        url = f"{BASE_URL}/getUpdates"
        params = {"offset": offset, "timeout": 30} if offset else {"timeout": 30}
        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"خطا در دریافت آپدیت‌ها: {e}")
        return None

    def handle_update(self, update):
        try:
            if "message" in update:
                self.attendance.handle_message(update["message"])
            elif "callback_query" in update:
                self.attendance.handle_callback({"callback_query": update["callback_query"]})
        except Exception as e:
            print(f"خطا در پردازش آپدیت: {e}")

    def run(self):
        offset = 0
        print("🤖 ربات حضور و غیاب شروع شد...")
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
                print("\n⛔ بات متوقف شد.")
                break
            except Exception as e:
                print(f"خطای غیرمنتظره: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = SchoolBot()
    bot.run()