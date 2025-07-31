#کلاو پیشرفته 
import jdatetime  # برای کار با تاریخ شمسی
import requests  # برای ارتباط با API بله
import json      # برای کار با داده‌های JSON
import time     # برای کار با زمان
import re       # برای کار با عبارات منظم
import logging  # برای ثبت گزارش‌ها
import os  # برای بررسی وجود فایل
import sys

# تنظیمات اصلی
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
API_URL = f'https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates'
SEND_URL = f'https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage'
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"


# توکن‌های ربات و پرداخت

    
#BOT_TOKEN = "811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1"# morabibot


PAYMENT_TOKEN = "WALLET-LIiCzxGZnCd58Obr" #برای دیباگ با توکن  شروع کنید
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
GROUP_LINK = "ble.ir/join/Gah9cS9LzQ"  #روم تست  ربات 

# اطلاعات پرداخت
WALLET_TOKEN = "WALLET-CUoV4RarlAACmThc"
GROUP_LINK = "ble.ir/join/Gah9cS9LzQ"

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# متغیرهای سراسری برای ذخیره اطلاعات
admin_id = None
users_data = {}  # اطلاعات کاربران
classes_data = {}  # اطلاعات کلاس‌ها
trainers_data = {}  # اطلاعات مربیان
offset = 0

class UserState:
    """کلاس برای مدیریت وضعیت کاربران"""
    NONE = "none"
    ADMIN_SETUP = "admin_setup"
    ADMIN_NAME = "admin_name"
    ADMIN_NATIONAL_ID = "admin_national_id"
    TRAINER_REGISTER = "trainer_register"
    TRAINER_NAME = "trainer_name"
    TRAINER_PHONE = "trainer_phone"
    STUDENT_REGISTER = "student_register"
    STUDENT_NAME = "student_name"
    STUDENT_NATIONAL_ID = "student_national_id"
    CLASS_SELECTION = "class_selection"
    PAYMENT = "payment"

def send_message(chat_id, text, reply_markup=None):
    """تابع ارسال پیام"""
    data = {
        'chat_id': chat_id,
        'text': text
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(SEND_URL, json=data)
        logging.info(f"Message sent to {chat_id}: {text[:50]}...")
        return response.json()
    except Exception as e:
        logging.error(f"Failed to send message to {chat_id}: {str(e)}")
        return None

def get_updates():
    """دریافت آپدیت‌ها از API"""
    global offset
    try:
        params = {'offset': offset, 'timeout': 30}
        response = requests.get(API_URL, params=params)
        data = response.json()
        
        if data.get('ok') and data.get('result'):
            logging.info(f"Received {len(data['result'])} updates")
            return data['result']
        return []
    except Exception as e:
        logging.error(f"Failed to get updates: {str(e)}")
        return []

def create_keyboard(buttons):
    """ایجاد کیبورد شیشه‌ای"""
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for button in row:
            keyboard_row.append({
                "text": button,
                "request_contact": button == "📱 ارسال شماره تماس"
            })
        keyboard.append(keyboard_row)
    
    return {
        "keyboard": keyboard,
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def handle_admin_setup(user_id, text):
    """مدیریت تنظیمات مدیر"""
    global admin_id
    
    if not admin_id:
        admin_id = user_id
        users_data[user_id] = {"state": UserState.ADMIN_NAME, "role": "admin"}
        
        keyboard = create_keyboard([
            ["📱 ارسال شماره تماس"]
        ])
        
        send_message(user_id, 
                    "🎉 شما به عنوان مدیر ربات ثبت شدید!\n\n"
                    "لطفاً نام و نام خانوادگی خود را وارد کنید:",
                    keyboard)
        logging.info(f"Admin registered: {user_id}")
        return True
    return False

def handle_trainer_registration(user_id, text):
    """مدیریت ثبت‌نام مربیان"""
    user_state = users_data.get(user_id, {}).get("state", UserState.NONE)
    
    if user_state == UserState.TRAINER_REGISTER:
        # انتخاب نوع مربی
        if text in ["مربی", "کمک مربی", "قرآن آموز"]:
            if text == "قرآن آموز":
                users_data[user_id]["state"] = UserState.STUDENT_REGISTER
                send_message(user_id, "لطفاً نام و نام خانوادگی خود را وارد کنید:")
            else:
                users_data[user_id]["role"] = text
                users_data[user_id]["state"] = UserState.TRAINER_NAME
                send_message(user_id, f"شما به عنوان {text} انتخاب شدید.\n\nلطفاً نام و نام خانوادگی خود را وارد کنید:")
            return True
    
    elif user_state == UserState.TRAINER_NAME:
        users_data[user_id]["name"] = text
        users_data[user_id]["state"] = UserState.TRAINER_PHONE
        
        keyboard = create_keyboard([
            ["📱 ارسال شماره تماس"]
        ])
        
        send_message(user_id, "نام شما ثبت شد.\n\nلطفاً شماره تماس خود را ارسال کنید:", keyboard)
        return True
    
    return False

def handle_group_message(chat_id, user_id, text):
    """مدیریت پیام‌های گروه"""
    if text == "/start":
        # اعلام نیاز به ادمین شدن
        send_message(chat_id, 
                    "سلام! 👋\n\n"
                    "برای استفاده از امکانات من، لطفاً مرا مدیر گروه کنید.\n\n"
                    "با تشکر 🙏")
        logging.info(f"Bot added to group: {chat_id}")
        return
    
    if text == "/عضو":
        # نمایش لیست قرآن آموزان و به‌روزرسانی
        current_date = jdatetime.datetime.now().strftime("%A %d %B")
        
        # لیست قرآن آموزان
        students_list = "📋 لیست قرآن آموزان:\n\n"
        student_count = 1
        for uid, data in users_data.items():
            if data.get("role") == "قرآن آموز" and data.get("verified"):
                students_list += f"{student_count}. {data.get('name', 'نامشخص')}\n"
                student_count += 1
        
        if student_count == 1:
            students_list += "هنوز قرآن آموزی ثبت نشده است."
        
        send_message(chat_id, f"📅 {current_date}\n\n{students_list}")
        logging.info(f"Student list displayed in group: {chat_id}")

def handle_private_message(user_id, text, contact=None):
    """مدیریت پیام‌های خصوصی"""
    # بررسی اینکه آیا کاربر مدیر است یا خیر
    if user_id not in users_data:
        users_data[user_id] = {"state": UserState.NONE}
    
    user_state = users_data[user_id].get("state", UserState.NONE)
    
    if text == "/start":
        if handle_admin_setup(user_id, text):
            return
        
        # نمایش منوی اصلی برای کاربران جدید
        keyboard = create_keyboard([
            ["مربی", "کمک مربی"],
            ["قرآن آموز"]
        ])
        
        users_data[user_id]["state"] = UserState.TRAINER_REGISTER
        send_message(user_id, 
                    "به ربات مدیریت گروه خوش آمدید! 🎉\n\n"
                    "لطفاً نقش خود را انتخاب کنید:", 
                    keyboard)
        return
    
    # مدیریت ثبت‌نام مربیان
    if handle_trainer_registration(user_id, text):
        return
    
    # مدیریت دریافت شماره تماس
    if contact and user_state == UserState.TRAINER_PHONE:
        phone_number = contact.get("phone_number", "")
        users_data[user_id]["phone"] = phone_number
        users_data[user_id]["verified"] = True
        
        role = users_data[user_id].get("role", "")
        name = users_data[user_id].get("name", "")
        
        if role in ["مربی", "کمک مربی"]:
            # ارسال اطلاعات گروه به مربی
            send_message(user_id, 
                        f"✅ ثبت‌نام شما تکمیل شد!\n\n"
                        f"👤 نام: {name}\n"
                        f"📞 شماره: {phone_number}\n"
                        f"👔 نقش: {role}\n\n"
                        f"🔗 لینک گروه: {GROUP_LINK}\n\n"
                        f"📝 توضیحات:\n"
                        f"- شما می‌توانید بدون پرداخت وارد گروه شوید\n"
                        f"- مدیر شما را ادمین خواهد کرد\n"
                        f"- هر روز لیست حضور و غیاب دریافت خواهید کرد")
            
            # اطلاع به مدیر
            if admin_id:
                send_message(admin_id, 
                            f"🆕 {role} جدید ثبت‌نام کرد:\n\n"
                            f"👤 نام: {name}\n"
                            f"📞 شماره: {phone_number}\n"
                            f"🆔 ID: {user_id}")
        
        users_data[user_id]["state"] = UserState.NONE
        logging.info(f"User registration completed: {user_id}, Role: {role}")

def main():
    """تابع اصلی ربات"""
    global offset
    
    print("🤖 Starting Bale Group Management Bot...")
    logging.info("Bot started successfully")
    
    while True:
        try:
            updates = get_updates()
            
            for update in updates:
                offset = update['update_id'] + 1
                
                if 'message' in update:
                    message = update['message']
                    chat_id = message['chat']['id']
                    user_id = message['from']['id']
                    text = message.get('text', '')
                    contact = message.get('contact')
                    
                    logging.info(f"Received message from {user_id} in {chat_id}: {text}")
                    
                    # تشخیص نوع چت (گروه یا خصوصی)
                    if message['chat']['type'] == 'private':
                        handle_private_message(user_id, text, contact)
                    else:
                        handle_group_message(chat_id, user_id, text)
        
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            print("\n🛑 Bot stopped!")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            time.sleep(5)  # صبر 5 ثانیه قبل از ادامه

if __name__ == "__main__":
    main()