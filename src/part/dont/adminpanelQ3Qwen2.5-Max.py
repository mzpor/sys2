import os
import sys
import json
import time
import re
import logging
import requests
from jdatetime import datetime

# Configuration
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
API_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates"
SEND_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
DATA_FILE = "1.json"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump({"managers": {}, "classes": {}, "coaches": {}}, file)

def load_data():
    """Load data from the JSON file."""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return {"managers": {}, "classes": {}, "coaches": {}}

def save_data(data):
    """Save data to the JSON file."""
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        logging.error(f"Error saving data: {e}")

def send_message(chat_id, text, reply_markup=None):
    """Send a message to the user."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": json.dumps(reply_markup) if reply_markup else None
    }
    response = requests.post(SEND_URL, data=payload)
    if response.status_code != 200:
        logging.error(f"Failed to send message: {response.text}")

def handle_start(chat_id, data):
    """Handle the start command."""
    managers = data["managers"]
    if str(chat_id) in managers:
        # Manager already registered
        send_message(chat_id, "اکنون می‌توانید ربات را به گروه اضافه کنید.")
        show_admin_panel(chat_id)
    else:
        # New manager registration
        send_message(chat_id, "لطفاً نام و فامیل خود را وارد کنید.")

def handle_registration(message, chat_id, data):
    """Handle manager registration."""
    if "full_name" not in data["managers"].get(str(chat_id), {}):
        full_name = message.strip()
        if not full_name or len(full_name.split()) < 2:
            send_message(chat_id, "لطفاً نام و فامیل خود را به درستی وارد کنید.")
            return
        data["managers"][str(chat_id)] = {"full_name": full_name}
        save_data(data)
        send_message(chat_id, f"نام شما ({full_name}) ثبت شد. حالا کد ملی خود را وارد کنید.")
    elif "national_code" not in data["managers"][str(chat_id)]:
        national_code = message.strip()
        if not re.match(r"^\d{10}$", national_code):
            send_message(chat_id, "کد ملی باید ۱۰ رقمی باشد. لطفاً دوباره امتحان کنید.")
            return
        data["managers"][str(chat_id)]["national_code"] = national_code
        save_data(data)
        send_message(chat_id, f"ثبت‌نام شما تکمیل شد. این پنل کاربری شماست.")
        show_admin_panel(chat_id)

def show_admin_panel(chat_id):
    """Show the admin panel."""
    keyboard = {
        "inline_keyboard": [
            [{"text": "مدیریت کلاس‌ها", "callback_data": "manage_classes"}],
            [{"text": "مدیریت مربی‌ها", "callback_data": "manage_coaches"}],
            [{"text": "تنظیمات", "callback_data": "settings"}]
        ]
    }
    send_message(chat_id, "پنل مدیریتی:", reply_markup=keyboard)

def handle_callback_query(callback_query, data):
    """Handle callback queries."""
    chat_id = callback_query["message"]["chat"]["id"]
    callback_data = callback_query["data"]

    if callback_data == "manage_classes":
        manage_classes(chat_id, data)
    elif callback_data == "manage_coaches":
        manage_coaches(chat_id, data)
    elif callback_data == "settings":
        send_message(chat_id, "در حال حاضر تنظیمات موجود نیست.")

def manage_classes(chat_id, data):
    """Manage classes."""
    classes = data["classes"]
    if not classes:
        send_message(chat_id, "هیچ کلاسی ثبت نشده است.")
        return

    keyboard = {
        "inline_keyboard": [
            [{"text": name, "callback_data": f"class_{class_id}"}]
            for class_id, name in classes.items()
        ] + [[{"text": "افزودن کلاس جدید", "callback_data": "add_class"}]]
    }
    send_message(chat_id, "لیست کلاس‌ها:", reply_markup=keyboard)

def manage_coaches(chat_id, data):
    """Manage coaches."""
    coaches = data["coaches"]
    if not coaches:
        send_message(chat_id, "هیچ مربی‌ای ثبت نشده است.")
        return

    keyboard = {
        "inline_keyboard": [
            [{"text": name, "callback_data": f"coach_{coach_id}"}]
            for coach_id, name in coaches.items()
        ] + [[{"text": "افزودن مربی جدید", "callback_data": "add_coach"}]]
    }
    send_message(chat_id, "لیست مربی‌ها:", reply_markup=keyboard)

def main():
    """Main function to handle bot updates."""
    offset = 0
    while True:
        try:
            response = requests.get(API_URL, params={"offset": offset})
            if response.status_code != 200:
                logging.error(f"Failed to fetch updates: {response.text}")
                time.sleep(5)
                continue

            updates = response.json().get("result", [])
            if not updates:
                time.sleep(1)
                continue

            data = load_data()

            for update in updates:
                offset = update["update_id"] + 1
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "").strip()

                    if text == "/start":
                        handle_start(chat_id, data)
                    elif str(chat_id) in data["managers"]:
                        handle_registration(text, chat_id, data)
                elif "callback_query" in update:
                    handle_callback_query(update["callback_query"], data)

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

    ####  در زدن اسم گیر کرد. 