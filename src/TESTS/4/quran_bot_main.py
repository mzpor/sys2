 # قوی‌ترین ربات مدیریت قرآن و تلاوت
# نسخه ۴.۰ - سیستم جامع مدیریت قرآنی
# توسعه‌دهنده: محمد زارع‌پور

import jdatetime
import requests
import json
import time
import re
import logging
import os
import sys
from datetime import datetime, timedelta

# تنظیمات اولیه
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log1 = sys1 = ": Quran Bot v4.0 "
delay = 0.2

# توکن ربات
BOT_TOKEN = '811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1'
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

# اطلاعات کلاس‌های قرآنی
QURAN_CLASSES = {
    "tajweed_basic": {
        "name": "دوره مقدماتی تجوید",
        "price": "300,000 تومان",
        "schedule": "شنبه‌ها و سه‌شنبه‌ها ساعت 17:00",
        "duration": "3 ماه",
        "level": "مبتدی"
    },
    "tajweed_advanced": {
        "name": "دوره پیشرفته تجوید",
        "price": "500,000 تومان", 
        "schedule": "یکشنبه‌ها و چهارشنبه‌ها ساعت 19:00",
        "duration": "4 ماه",
        "level": "متوسط"
    },
    "recitation_basic": {
        "name": "دوره مقدماتی تلاوت",
        "price": "400,000 تومان",
        "schedule": "دوشنبه‌ها و پنج‌شنبه‌ها ساعت 18:00",
        "duration": "3 ماه",
        "level": "مبتدی"
    },
    "recitation_advanced": {
        "name": "دوره پیشرفته تلاوت",
        "price": "600,000 تومان",
        "schedule": "سه‌شنبه‌ها و جمعه‌ها ساعت 20:00",
        "duration": "4 ماه",
        "level": "متوسط"
    },
    "memorization": {
        "name": "دوره حفظ قرآن",
        "price": "800,000 تومان",
        "schedule": "هر روز ساعت 16:00",
        "duration": "12 ماه",
        "level": "پیشرفته"
    },
    "quranic_sciences": {
        "name": "علوم قرآنی",
        "price": "700,000 تومان",
        "schedule": "جمعه‌ها ساعت 10:00",
        "duration": "6 ماه",
        "level": "متوسط"
    }
}

# لینک‌های پرداخت
PAYMENT_LINKS = {
    "tajweed_basic": "https://example.com/pay/tajweed_basic",
    "tajweed_advanced": "https://example.com/pay/tajweed_advanced",
    "recitation_basic": "https://example.com/pay/recitation_basic",
    "recitation_advanced": "https://example.com/pay/recitation_advanced",
    "memorization": "https://example.com/pay/memorization",
    "quranic_sciences": "https://example.com/pay/quranic_sciences"
}

# سرویس‌های ویژه برای کاربران ثبت‌نام شده
VIP_SERVICES = {
    "personal_coaching": {
        "name": "مربی خصوصی",
        "description": "جلسات خصوصی با استاد مجرب",
        "price": "200,000 تومان در جلسه"
    },
    "online_library": {
        "name": "کتابخانه آنلاین",
        "description": "دسترسی به منابع آموزشی و صوتی",
        "price": "رایگان برای اعضا"
    },
    "certificate": {
        "name": "گواهی پایان دوره",
        "description": "گواهی معتبر پایان دوره",
        "price": "50,000 تومان"
    },
    "competition": {
        "name": "مسابقات قرآنی",
        "description": "شرکت در مسابقات داخلی و خارجی",
        "price": "رایگان"
    },
    "workshop": {
        "name": "کارگاه‌های تخصصی",
        "description": "کارگاه‌های تکمیلی و تخصصی",
        "price": "100,000 تومان"
    },
    "consultation": {
        "name": "مشاوره تحصیلی",
        "description": "مشاوره در انتخاب مسیر قرآنی",
        "price": "رایگان"
    }
}

# پیام‌های انگیزشی
MOTIVATIONAL_QUOTES = [
    "🌟 قرآن نور هدایت است، با تلاوت آن قلب خود را روشن کنید!",
    "🚀 هر آیه‌ای که می‌خوانید، یک قدم به خدا نزدیک‌تر می‌شوید!",
    "💪 تلاوت قرآن، بهترین عبادت و نزدیک‌ترین راه به پروردگار!",
    "🔥 با هر تلاوت، روح و روان خود را پاک و صفا دهید!",
    "🎯 قرآن کتاب زندگی است، با آن زندگی کنید!",
    "🌱 هر حرف قرآن، بذری از نور در قلب شما می‌کارد!",
    "👏 آفرین به شما که قرآن را سرلوحه زندگی خود قرار داده‌اید!",
    "⏳ زمان طلاست! امروز بهترین زمان برای شروع تلاوت است!",
    "💡 قرآن شفای دلهاست، با تلاوت آن شفا یابید!",
    "🏆 قرآن‌آموزان، سربازان خدا در راه هدایت بشر هستند!"
]

# متغیرهای سراسری
quote_index = 0
known_members = {}
recitation_exercises = {}
exercise_scores = {}
private_signup_states = {}
registered_users = {}
admin_services = {}
TXT_FILE = 'quran_users.txt'

def create_keyboard(buttons, is_inline=True, resize_keyboard=True, one_time_keyboard=False):
    """ایجاد کیبورد برای دکمه‌های پاسخ"""
    if is_inline:
        inline_keyboard_buttons = []
        for row in buttons:
            row_buttons = []
            for button in row:
                button_data = {"text": button["text"]}
                if "callback_data" in button:
                    button_data["callback_data"] = button["callback_data"]
                if "request_contact" in button:
                    button_data["request_contact"] = button["request_contact"]
                row_buttons.append(button_data)
            inline_keyboard_buttons.append(row_buttons)
        return {"inline_keyboard": inline_keyboard_buttons}
    else:
        keyboard_buttons = []
        for row in buttons:
            row_buttons = []
            for button in row:
                button_data = {"text": button["text"]}
                if "request_contact" in button:
                    button_data["request_contact"] = button["request_contact"]
                if "request_location" in button:
                    button_data["request_location"] = button["request_location"]
                row_buttons.append(button_data)
            keyboard_buttons.append(row_buttons)
        return {"keyboard": keyboard_buttons, "resize_keyboard": resize_keyboard, "one_time_keyboard": one_time_keyboard}

def send_message(chat_id, text, reply_markup=None):
    """ارسال پیام به یک چت مشخص"""
    url = f"{BASE_URL}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": text
    }
    
    if reply_markup:
        if isinstance(reply_markup, dict) and 'inline_keyboard' in reply_markup and 'keyboard' in reply_markup:
            combined_markup = {}
            if reply_markup.get('inline_keyboard'):
                combined_markup['inline_keyboard'] = reply_markup['inline_keyboard']
            if reply_markup.get('keyboard'):
                combined_markup['keyboard'] = reply_markup['keyboard']
                combined_markup['resize_keyboard'] = reply_markup.get('resize_keyboard', True)
                combined_markup['one_time_keyboard'] = reply_markup.get('one_time_keyboard', False)
            data['reply_markup'] = json.dumps(combined_markup)
        else:
            data['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.ok:
            return response.json()
        else:
            logging.error(f"خطا در ارسال پیام: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"خطای شبکه: {e}")
        return None

def get_updates(offset=None):
    """دریافت پیام‌های جدید از API"""
    url = f"{BASE_URL}/getUpdates"
    params = {}
    if offset:
        params['offset'] = offset
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.ok:
            return response.json()
        else:
            logging.error(f"خطا در درخواست API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"خطای شبکه: {e}")
        return None

def get_chat_administrators(chat_id):
    """دریافت لیست ادمین‌های یک گروه"""
    url = f"{BASE_URL}/getChatAdministrators"
    data = {"chat_id": chat_id}
    
    try:
        response = requests.get(url, json=data, timeout=10)
        if response.ok: 
            result = response.json()
            if result.get('ok'):
                return result.get('result', [])
            else:
                logging.error(f"خطای API: {result.get('description', 'خطای ناشناخته')}")
                return []
        else:
            logging.error(f"خطای HTTP: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"خطای شبکه: {e}")
        return []

def get_simple_name(user):
    """دریافت نام ساده‌شده کاربر"""
    first_name = user.get('first_name', '')
    last_name = user.get('last_name', '')
    full_name = f"{first_name} {last_name}".strip()
    
    if not full_name and user.get('username'):
        full_name = f"@{user.get('username')}"
    
    return full_name if full_name else "بدون نام"

def get_jalali_date():
    """دریافت تاریخ جلالی"""
    now = jdatetime.datetime.now()
    PERSIAN_MONTH_NAMES = {
        1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد', 4: 'تیر', 5: 'مرداد', 6: 'شهریور',
        7: 'مهر', 8: 'آبان', 9: 'آذر', 10: 'دی', 11: 'بهمن', 12: 'اسفند'
    }
    day = now.day
    month_name = PERSIAN_MONTH_NAMES.get(now.month, '')
    return f"{day} {month_name}"

def get_week_day():
    """دریافت نام روز هفته"""
    now = jdatetime.datetime.now()
    weekday_num = now.weekday()
    WEEKDAY_MAP = {
        0: 'شنبه', 1: 'یک‌شنبه', 2: 'دوشنبه', 3: 'سه‌شنبه',
        4: 'چهارشنبه', 5: 'پنج‌شنبه', 6: 'جمعه'
    }
    return WEEKDAY_MAP.get(weekday_num, 'نامشخص')

def is_exercise_day():
    """بررسی روز تمرین"""
    now = jdatetime.datetime.now()
    weekday = now.weekday()
    EXERCISE_DAYS = {0, 2, 4}  # شنبه، دوشنبه، چهارشنبه
    return weekday in EXERCISE_DAYS

def is_admin(user_id, chat_id):
    """بررسی ادمین بودن کاربر"""
    administrators = get_chat_administrators(chat_id)
    admin_ids = {admin_info.get('user', {}).get('id') for admin_info in administrators}
    return user_id in admin_ids

def save_users_to_file():
    """ذخیره کاربران در فایل"""
    try:
        with open(TXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(registered_users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f'خطا در ذخیره فایل: {e}')

def load_users_from_file():
    """بارگذاری کاربران از فایل"""
    global registered_users
    if os.path.exists(TXT_FILE):
        try:
            with open(TXT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    registered_users = data
        except Exception as e:
            logging.error(f'خطا در خواندن فایل: {e}')

# بارگذاری کاربران در شروع
load_users_from_file()