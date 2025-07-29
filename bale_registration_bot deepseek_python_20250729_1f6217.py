#افضاح 

import json
import logging
import os
import re
import sys
from datetime import datetime
import jdatetime
import requests
from typing import Dict, Optional, Union

# تنظیمات پایه
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
API_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates"
SEND_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
DATA_FILE = "1.json"

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('registration_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ساختارهای داده
USER_DATA: Dict[str, Dict] = {}
USER_STATES: Dict[str, Dict] = {}

def load_data() -> None:
    """بارگذاری داده‌های ذخیره شده از فایل"""
    global USER_DATA
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                USER_DATA = json.load(f)
            logger.info("User data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
            USER_DATA = {}

def save_data() -> None:
    """ذخیره داده‌ها در فایل"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(USER_DATA, f, ensure_ascii=False, indent=4)
        logger.info("User data saved successfully")
    except Exception as e:
        logger.error(f"Error saving user data: {e}")

def send_message(
    chat_id: Union[int, str],
    text: str,
    reply_markup: Optional[Dict] = None,
    parse_mode: str = "HTML"
) -> Optional[Dict]:
    """ارسال پیام به کاربر"""
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(SEND_URL, json=payload)
        logger.info(f"Sent message to {chat_id}: {text}")
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

def get_updates(offset: Optional[int] = None) -> list:
    """دریافت آپدیت‌های جدید از سرور"""
    params = {'timeout': 30}
    if offset:
        params['offset'] = offset
    
    try:
        response = requests.get(API_URL, params=params)
        return response.json().get('result', [])
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        return []

def validate_national_id(national_id: str) -> bool:
    """اعتبارسنجی کد ملی"""
    if not national_id.isdigit() or len(national_id) != 10:
        return False
    
    # الگوریتم بررسی کد ملی
    check = int(national_id[9])
    s = sum(int(national_id[i]) * (10 - i) for i in range(9)) % 11
    return (s < 2 and check == s) or (s >= 2 and check + s == 11)

def get_start_keyboard() -> Dict:
    """کیبورد شروع"""
    return {
        'keyboard': [
            [{'text': 'شروع مجدد'}, {'text': 'معرفی آموزشگاه'}],
            [{'text': 'خروج'}]
        ],
        'resize_keyboard': True
    }

def get_inline_start_keyboard() -> Dict:
    """کیبورد اینلاین شروع"""
    return {
        'inline_keyboard': [
            [{'text': '📝 شروع ثبت‌نام', 'callback_data': 'start_registration'}]
        ]
    }

def get_edit_name_keyboard() -> Dict:
    """کیبورد تصحیح نام"""
    return {
        'inline_keyboard': [
            [{'text': '✏️ تصحیح نام', 'callback_data': 'edit_name'}]
        ]
    }

def get_national_id_keyboard() -> Dict:
    """کیبورد کد ملی"""
    return {
        'keyboard': [
            [{'text': 'شروع مجدد'}, {'text': 'خروج'}],
            [{'text': 'برگشت به قبل'}]
        ],
        'resize_keyboard': True
    }

def get_edit_national_id_keyboard() -> Dict:
    """کیبورد تصحیح کد ملی"""
    return {
        'inline_keyboard': [
            [{'text': '✏️ تصحیح کد ملی', 'callback_data': 'edit_national_id'}],
            [{'text': '📱 ارسال شماره تلفن', 'request_contact': True}]
        ]
    }

def get_final_confirmation_keyboard() -> Dict:
    """کیبورد تأیید نهایی"""
    return {
        'inline_keyboard': [
            [{'text': '✅ تأیید نهایی', 'callback_data': 'final_confirm'}],
            [{'text': '✏️ تصحیح اطلاعات', 'callback_data': 'edit_info'}]
        ]
    }

def handle_start(chat_id: int, user_id: int, first_name: str) -> None:
    """مدیریت دستور /start"""
    # پیام خوش‌آمدگویی
    welcome_msg = (
        f"🌟 {first_name} عزیز! به ربات ثبت‌نام آموزشگاه قرآن خوش آمدید!\n\n"
        "برای شروع ثبت‌نام، روی دکمه 'شروع ثبت‌نام' کلیک کنید."
    )
    
    # ارسال پیام با کیبوردهای معمولی و اینلاین
    send_message(chat_id, welcome_msg, reply_markup=get_start_keyboard())
    send_message(chat_id, "لطفاً گزینه مورد نظر را انتخاب کنید:", reply_markup=get_inline_start_keyboard())
    
    # ذخیره حالت کاربر
    USER_STATES[str(user_id)] = {'state': 'start'}
    logger.info(f"User {user_id} started the bot")

def handle_registration_start(chat_id: int, user_id: int, first_name: str) -> None:
    """شروع فرآیند ثبت‌نام"""
    # ارسال درخواست نام و نام خانوادگی
    send_message(
        chat_id,
        f"{first_name} عزیز، لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی).",
        reply_markup=get_national_id_keyboard()
    )
    
    # به‌روزرسانی حالت کاربر
    USER_STATES[str(user_id)] = {'state': 'awaiting_full_name'}
    logger.info(f"User {user_id} started registration process")

def handle_full_name_input(chat_id: int, user_id: int, text: str) -> None:
    """پردازش نام و نام خانوادگی وارد شده"""
    # اعتبارسنجی نام
    if not re.match(r'^[\u0600-\u06FF\s]{3,}$', text):
        send_message(chat_id, "⚠️ نام وارد شده معتبر نیست. لطفاً نام و نام خانوادگی فارسی وارد کنید.")
        return
    
    # استخراج نام کوچک
    first_name = text.split()[0]
    
    # ذخیره اطلاعات کاربر
    if str(user_id) not in USER_DATA:
        USER_DATA[str(user_id)] = {}
    
    USER_DATA[str(user_id)].update({
        'full_name': text,
        'first_name': first_name
    })
    
    # نمایش اطلاعات فعلی
    info_msg = (
        f"{first_name} عزیز،\n"
        f"نام شما: {text}\n"
        f"کد ملی: هنوز مانده\n"
        f"تلفن: هنوز مانده"
    )
    
    send_message(chat_id, info_msg, reply_markup=get_edit_name_keyboard())
    
    # درخواست کد ملی
    send_message(
        chat_id,
        f"{first_name} عزیز، لطفاً کد ملی ۱۰ رقمی خود را وارد کنید.",
        reply_markup=get_national_id_keyboard()
    )
    
    # به‌روزرسانی حالت کاربر
    USER_STATES[str(user_id)] = {'state': 'awaiting_national_id'}
    logger.info(f"User {user_id} entered full name: {text}")

def handle_national_id_input(chat_id: int, user_id: int, text: str) -> None:
    """پردازش کد ملی وارد شده"""
    # اعتبارسنجی کد ملی
    if not validate_national_id(text):
        send_message(chat_id, "⚠️ کد ملی نامعتبر است. لطفاً یک کد ملی ۱۰ رقمی معتبر وارد کنید.")
        return
    
    # ذخیره کد ملی
    USER_DATA[str(user_id)]['national_id'] = text
    first_name = USER_DATA[str(user_id)].get('first_name', 'کاربر')
    
    # نمایش اطلاعات فعلی
    info_msg = (
        f"{first_name} عزیز،\n"
        f"نام شما: {USER_DATA[str(user_id)]['full_name']}\n"
        f"کد ملی: {text}\n"
        f"تلفن: هنوز مانده"
    )
    
    send_message(chat_id, info_msg, reply_markup=get_edit_national_id_keyboard())
    
    # درخواست شماره تلفن
    send_message(
        chat_id,
        f"{first_name} عزیز، لطفاً برای ارسال شماره تلفن خود روی دکمه زیر بزنید.",
        reply_markup=get_edit_national_id_keyboard()
    )
    
    # به‌روزرسانی حالت کاربر
    USER_STATES[str(user_id)] = {'state': 'awaiting_phone_number'}
    logger.info(f"User {user_id} entered national ID: {text}")

def handle_phone_number(chat_id: int, user_id: int, phone_number: str) -> None:
    """پردازش شماره تلفن دریافت شده"""
    # فرمت‌دهی شماره تلفن
    if phone_number.startswith('+98'):
        phone_number = '0' + phone_number[3:]
    elif phone_number.startswith('98'):
        phone_number = '0' + phone_number[2:]
    
    # ذخیره شماره تلفن
    USER_DATA[str(user_id)]['phone'] = phone_number
    first_name = USER_DATA[str(user_id)].get('first_name', 'کاربر')
    
    # نمایش اطلاعات نهایی برای تأیید
    info_msg = (
        f"📋 {first_name} عزیز، حساب کاربری شما:\n"
        f"نام: {USER_DATA[str(user_id)]['full_name']}\n"
        f"کد ملی: {USER_DATA[str(user_id)]['national_id']}\n"
        f"تلفن: {phone_number}\n\n"
        "آیا اطلاعات درست است؟"
    )
    
    send_message(
        chat_id,
        info_msg,
        reply_markup=get_final_confirmation_keyboard()
    )
    
    # به‌روزرسانی حالت کاربر
    USER_STATES[str(user_id)] = {'state': 'awaiting_final_confirmation'}
    logger.info(f"User {user_id} provided phone number: {phone_number}")

def handle_final_confirmation(chat_id: int, user_id: int) -> None:
    """پردازش تأیید نهایی"""
    first_name = USER_DATA[str(user_id)].get('first_name', 'کاربر')
    
    # ثبت نهایی کاربر
    USER_DATA[str(user_id)]['registration_date'] = str(jdatetime.datetime.now())
    USER_DATA[str(user_id)]['is_completed'] = True
    
    # ذخیره داده‌ها
    save_data()
    
    # ارسال پیام تأیید
    send_message(
        chat_id,
        f"🎉 {first_name} عزیز، ثبت‌نام شما با موفقیت تکمیل شد! موفق باشید!",
        reply_markup=get_start_keyboard()
    )
    
    # پاک کردن حالت کاربر
    if str(user_id) in USER_STATES:
        del USER_STATES[str(user_id)]
    
    logger.info(f"User {user_id} completed registration successfully")

def handle_edit_info(chat_id: int, user_id: int) -> None:
    """بازنشانی اطلاعات و شروع مجدد ثبت‌نام"""
    # پاک کردن اطلاعات کاربر
    if str(user_id) in USER_DATA:
        del USER_DATA[str(user_id)]
    
    # بازگشت به مرحله شروع ثبت‌نام
    handle_registration_start(chat_id, user_id, "کاربر")
    logger.info(f"User {user_id} requested to edit info, resetting registration")

def process_updates() -> None:
    """پردازش آپدیت‌های دریافتی"""
    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update['update_id'] + 1
            
            try:
                message = update.get('message', {})
                callback_query = update.get('callback_query', {})
                
                # پردازش پیام‌های متنی
                if message:
                    chat_id = message.get('chat', {}).get('id')
                    user_id = message.get('from', {}).get('id')
                    first_name = message.get('from', {}).get('first_name', 'کاربر')
                    text = message.get('text', '')
                    contact = message.get('contact', {})
                    
                    # پردازش دستور /start
                    if text.startswith('/start'):
                        handle_start(chat_id, user_id, first_name)
                    
                    # پردازش بر اساس حالت کاربر
                    user_state = USER_STATES.get(str(user_id), {}).get('state')
                    
                    if user_state == 'awaiting_full_name':
                        handle_full_name_input(chat_id, user_id, text)
                    
                    elif user_state == 'awaiting_national_id':
                        handle_national_id_input(chat_id, user_id, text)
                    
                    elif contact and user_state == 'awaiting_phone_number':
                        handle_phone_number(chat_id, user_id, contact.get('phone_number', ''))
                
                # پردازش callback queries
                elif callback_query:
                    chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
                    user_id = callback_query.get('from', {}).get('id')
                    data = callback_query.get('data')
                    
                    if data == 'start_registration':
                        handle_registration_start(chat_id, user_id, callback_query.get('from', {}).get('first_name', 'کاربر'))
                    
                    elif data == 'final_confirm':
                        handle_final_confirmation(chat_id, user_id)
                    
                    elif data == 'edit_info':
                        handle_edit_info(chat_id, user_id)
                    
                    elif data == 'edit_name':
                        USER_STATES[str(user_id)] = {'state': 'awaiting_full_name'}
                        send_message(
                            chat_id,
                            "لطفاً نام و نام خانوادگی خود را مجدداً وارد کنید (مثال: علی رضایی).",
                            reply_markup=get_national_id_keyboard()
                        )
                    
                    elif data == 'edit_national_id':
                        USER_STATES[str(user_id)] = {'state': 'awaiting_national_id'}
                        send_message(
                            chat_id,
                            "لطفاً کد ملی ۱۰ رقمی خود را مجدداً وارد کنید.",
                            reply_markup=get_national_id_keyboard()
                        )
            
            except Exception as e:
                logger.error(f"Error processing update: {e}")

        time.sleep(1)

def main() -> None:
    """تابع اصلی"""
    logger.info("Starting registration bot...")
    load_data()
    
    try:
        process_updates()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        save_data()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        save_data()
        sys.exit(1)

if __name__ == '__main__':
    main()