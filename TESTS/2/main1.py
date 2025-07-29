# ربات  ثبت نام قران اموزان و مدیریت تمرین‌های تلاوت قرآن
# نسخه ۳.۰
# توسعه‌دهنده: محمد زارع‌پور
#     یکشنبه  ساعت 06:31 شروع 
#  7/27/25
#برنامه های جدید 
#کامل کردن ثبت نام 
#کامل کردن عضویت در گروه                          

#اول  تصححیح ثبت نام 

# کتابخانه‌های مورد نیاز  mzpor
import jdatetime  # برای کار با تاریخ شمسی
import requests  # برای ارتباط با API بله
import json      # برای کار با داده‌های JSON
import time     # برای کار با زمان
import re       # برای کار با عبارات منظم
import logging  # برای ثبت گزارش‌ها
import os  # برای بررسی وجود فایل
import sys

# تنظیمات اولیه سیستم ثبت گزارش
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# متغیر اسم سیستم - قابل تغییر برای محل‌های مختلف اجرا
log1=sys1= ": main sys "
delay = 0.2
# توکن ربات (در محیط تولید باید از متغیر محیطی استفاده شود)
#BOT_TOKEN = '1423205711:aNMfw7aEfrMwHNITw4S7bTs9NP92MRzcDLg19Hjo'# یار ثبت نام 
BOT_TOKEN = '811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1'  #یار مربی
#BOT_TOKEN = '1714651531:y2xOK6EBg5nzVV6fEWGqtOdc3nVqVgOuf4PZVQ7S'#یار مدیر
# یار مربی توکن اصلی
API_URL = f'https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates'
SEND_URL = f'https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage'
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"  # آدرس پایه API بله

# اطلاعات کلاس‌ها
CLASSES = {
    "quran_recitation": {
        "name": "رشت بری",
        "price": "1,000 تومان",
        "schedule": "شنبه‌ها و سه‌شنبه‌ها ساعت 18:00"
    },
    "tajvid": {
        "name": "جاجی زاده",
        "price": "1,000 تومان",
        "schedule": "یکشنبه‌ها و چهارشنبه‌ها ساعت 20:00"
    }
}

# لینک‌های پرداخت (مثال)
PAYMENT_LINKS = {
    "quran_recitation": "https://example.com/pay/quran",
    "tajvid": "https://example.com/pay/tajvid"
}

def create_keyboard(buttons, is_inline=True, resize_keyboard=True, one_time_keyboard=False):
    """ایجاد کیبورد برای دکمه‌های پاسخ

    پارامترها:
        buttons (list): لیستی از دکمه‌ها. هر دکمه می‌تواند یک دیکشنری با 
        'text' و 'callback_data' باشد
                        برای دکمه‌های اینلاین، یا فقط 'text' برای کیبوردهای معمولی.
        is_inline (bool): اگر True باشد، کیبورد اینلاین (شیشه‌ای) ایجاد می‌شود.
        resize_keyboard (bool): (فقط برای کیبوردهای معمولی) اگر True باشد، کیبورد به اندازه مناسب تغییر اندازه می‌دهد.
        one_time_keyboard (bool): (فقط برای کیبوردهای معمولی) اگر True باشد، کیبورد پس از استفاده پنهان می‌شود.

    خروجی:
        dict: ساختار JSON برای کیبورد
    """
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

# پیام‌های انگیزشی برای نمایش در گزارش‌ها
motivational_quotes = [
    "🌟 تمرین تلاوت زندگی‌ات را تغییر می‌دهد!",
    "🚀 با هر تمرین، یک قدم به رشد نزدیک‌تر می‌شوی!",
    "💪 پیگیری و تمرین، کلید موفقیت توست!",
    "🔥 تمرین با دقت، کیفیت تلاوتت را بالا می‌برد!",
    "🎯 شاگرد پرتلاش! منتظر تلاوت‌های زیبای تو هستیم!",
    "🌱 هر تمرین، یک بذر برای آینده‌ای درخشان!",
    "👏 آفرین به تو که با تمرین، سطح خودت را بالا می‌بری!",
    "⏳ زمان طلاست! تمرین امروز، موفقیت فرداست!",
    "💡 تلاوت مداوم، قلب و روحت را نورانی می‌کند!",
    "🏆 شاگردان پرتلاش، آینده از آن شماست!"
]
quote_index = 0  # شاخص برای انتخاب پیام انگیزشی بعدی

def get_updates(offset=None):
    """دریافت پیام‌های جدید از API بله

    پارامترها:
        offset (int, اختیاری): شناسه اولین به‌روزرسانی که باید برگردانده شود

    خروجی:
        dict: پاسخ JSON حاوی به‌روزرسانی‌ها، یا None در صورت بروز خطا
    """
    url = f"{BASE_URL}/getUpdates"  # ساخت آدرس API
    params = {}  # پارامترهای درخواست
    if offset:
        params['offset'] = offset  # افزودن شناسه آخرین پیام دریافتی
    
    try:
        # ارسال درخواست GET به API با مهلت ۱۰ ثانیه
        response = requests.get(url, params=params, timeout=10)
        if response.ok:
            return response.json()  # برگرداندن پاسخ در صورت موفقیت
        else:
            logging.error(f"خطا در درخواست API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"خطای شبکه: {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    """ارسال پیام به یک چت مشخص

    پارامترها:
        chat_id (int): شناسه یکتای چت هدف
        text (str): متن پیام برای ارسال
        reply_markup (dict, اختیاری): گزینه‌های اضافی پیام (مانند دکمه‌های درون‌خطی)

    خروجی:
        dict: پاسخ JSON از API، یا None در صورت بروز خطا
    """
    url = f"{BASE_URL}/sendMessage"  # ساخت آدرس API برای ارسال پیام
    
    data = {
        "chat_id": chat_id,      # شناسه چت هدف
        "text": text             # متن اصلی بدون parse_mode
    }
    
    if reply_markup:
        # اگر reply_markup شامل هر دو نوع دکمه باشد
        if isinstance(reply_markup, dict) and 'inline_keyboard' in reply_markup and 'keyboard' in reply_markup:
            # ترکیب دکمه‌های شیشه‌ای و معمولی
            combined_markup = {}
            if reply_markup.get('inline_keyboard'):
                combined_markup['inline_keyboard'] = reply_markup['inline_keyboard']
            if reply_markup.get('keyboard'):
                combined_markup['keyboard'] = reply_markup['keyboard']
                combined_markup['resize_keyboard'] = reply_markup.get('resize_keyboard', True)
                combined_markup['one_time_keyboard'] = reply_markup.get('one_time_keyboard', False)
            data['reply_markup'] = json.dumps(combined_markup)
        else:
            data['reply_markup'] = json.dumps(reply_markup)  # افزودن دکمه‌ها در صورت وجود
    
    try:
        # ارسال درخواست POST به API با مهلت ۱۰ ثانیه
        response = requests.post(url, json=data, timeout=10)
        if response.ok:
            return response.json()  # برگرداندن پاسخ در صورت موفقیت
        else:
            logging.error(f"خطا در ارسال پیام: {response.status_code} - {response.text}")
            logging.error(f"متن ارسالی: {text}")
            logging.error(f"داده‌های ارسالی: {data}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"خطای شبکه: {e}")
        return None

def get_chat_administrators(chat_id):
    """دریافت لیست ادمین‌های یک گروه

    پارامترها:
        chat_id (int): شناسه یکتای گروه

    خروجی:
        list: لیستی از اشیاء ChatMember که هر کدام نشان‌دهنده یک ادمین است،
              یا لیست خالی در صورت بروز خطا
    """
    url = f"{BASE_URL}/getChatAdministrators"  # ساخت آدرس API
    data = {"chat_id": chat_id}  # داده‌های درخواست
    
    try:
        # ارسال درخواست POST به API با مهلت ۱۰ ثانیه
        response = requests.get(url, json=data, timeout=10)
        if response.ok: 
            result = response.json()
            if result.get('ok'):
                return result.get('result', [])  # برگرداندن لیست ادمین‌ها
            else:
                logging.error(f"خطای API: {result.get('description', 'خطای ناشناخته')}")
                return []
        else:
            logging.error(f"خطای HTTP: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"خطای شبکه: {e}")
        return []

def get_chat_member_count(chat_id):
    """دریافت تعداد اعضای یک گروه

    پارامترها:
        chat_id (int): شناسه یکتای گروه

    خروجی:
        int: تعداد اعضای گروه، یا 0 در صورت بروز خطا
    """
    url = f"{BASE_URL}/getChatMemberCount"  # ساخت آدرس API
    data = {"chat_id": chat_id}  # داده‌های درخواست
    
    try:
        # ارسال درخواست POST به API با مهلت ۱۰ ثانیه
        response = requests.post(url, json=data, timeout=10)
        if response.ok:
            result = response.json()
            if result.get('ok'):
                return result.get('result', 0)  # برگرداندن تعداد اعضا
            else:
                logging.error(f"خطای API: {result.get('description', 'خطای ناشناخته')}")
                return 0
        else:
            logging.error(f"خیطای HTTP: {response.status_code}")
            return 0
    except requests.exceptions.RequestException as e:
        logging.error(f"خطای شبکه: {e}")
        return 0

def get_simple_name(user):
    """دریافت نام ساده‌شده کاربر

    پارامترها:
        user (dict): اطلاعات کاربر شامل نام و نام خانوادگی

    خروجی:
        str: نام کامل کاربر، نام کاربری یا 'بدون نام'
    """
    first_name = user.get('first_name', '')  # دریافت نام کوچک
    last_name = user.get('last_name', '')    # دریافت نام خانوادگی
    full_name = f"{first_name} {last_name}".strip()  # ترکیب نام کامل
    
    # اگر نام کامل خالی بود و نام کاربری داشت
    if not full_name and user.get('username'):
        full_name = f"@{user.get('username')}"  # استفاده از نام کاربری
    
    return full_name if full_name else "بدون نام"  # برگرداندن نام یا مقدار پیش‌فرض

def get_jalali_date():
    """دریافت تاریخ جلالی به فرمت 'روز نام‌ماه'

    خروجی:
        str: تاریخ به فرمت '12 فروردین'
    """
    now = jdatetime.datetime.now()  # دریافت زمان فعلی به تاریخ جلالی
    
    # تعریف نام ماه‌های فارسی
    PERSIAN_MONTH_NAMES = {
        1: 'فروردین',
        2: 'اردیبهشت',
        3: 'خرداد',
        4: 'تیر',
        5: 'مرداد',
        6: 'شهریور',
        7: 'مهر',
        8: 'آبان',
        9: 'آذر',
        10: 'دی',
        11: 'بهمن',
        12: 'اسفند'
    }
    
    day = now.day  # شماره روز
    month_name = PERSIAN_MONTH_NAMES.get(now.month, '')  # نام ماه
    return f"{day} {month_name}"  # ترکیب روز و نام ماه

def get_week_day():
    """دریافت نام روز هفته به فارسی

    خروجی:
        str: نام روز هفته به فارسی (مثلاً 'شنبه')
    """
    now = jdatetime.datetime.now()  # دریافت زمان فعلی
    weekday_num = now.weekday()     # دریافت شماره روز هفته (0 تا 6)
    logging.debug(f"شماره روز هفته: {weekday_num}")
    
    # نگاشت شماره روز به نام فارسی
    WEEKDAY_MAP = {
        0: 'شنبه',
        1: 'یک‌شنبه',
        2: 'دوشنبه',
        3: 'سه‌شنبه',
        4: 'چهارشنبه',
        5: 'پنج‌شنبه',
        6: 'جمعه'
    }
    
    return WEEKDAY_MAP.get(weekday_num, 'نامشخص')  # برگرداندن نام روز یا 'نامشخص'

def is_exercise_day():
    """بررسی اینکه آیا امروز روز تلاوت است
    (شنبه، دوشنبه، چهارشنبه)

    خروجی:
        bool: True اگر امروز روز تلاوت باشد، False در غیر این صورت
    """
    now = jdatetime.datetime.now()  # دریافت زمان فعلی
    weekday = now.weekday()         # دریافت شماره روز هفته
    logging.debug(f"شماره روز هفته: {weekday}")
    
    EXERCISE_DAYS = {0, 2, 4}  # مجموعه روزهای تلاوت (شنبه=0، دوشنبه=2، چهارشنبه=4)
    return weekday in EXERCISE_DAYS   # بررسی روز فعلی

def get_exercise_deadline():
    """
    محاسبه مهلت ارسال تلاوت بر اساس روز هفته:
    - تلاوت شنبه: تا پایان روز شنبه
    - تلاوت دوشنبه: از یکشنبه تا پایان روز دوشنبه
    - تلاوت چهارشنبه: از سه‌شنبه تا پایان روز چهارشنبه

    خروجی:
        tuple: (تاریخ مهلت به فرمت Y/m/d, ساعات باقی‌مانده)
    """
    now = jdatetime.datetime.now()  # دریافت زمان فعلی
    current_weekday = now.weekday() # دریافت شماره روز هفته
    logging.debug(f"روز هفته فعلی: {current_weekday}")
    
    # محاسبه مهلت بر اساس روز هفته
    if current_weekday == 0:  # شنبه
        deadline = now.replace(hour=23, minute=59, second=59)  # پایان همان روز
    elif current_weekday in [1, 2]:  # یکشنبه و دوشنبه
        days_to_monday = 2 - current_weekday
        deadline = (now + jdatetime.timedelta(days=days_to_monday)).replace(hour=23, minute=59, second=59)
    elif current_weekday in [3, 4]:  # سه‌شنبه و چهارشنبه
        days_to_wednesday = 4 - current_weekday
        deadline = (now + jdatetime.timedelta(days=days_to_wednesday)).replace(hour=23, minute=59, second=59)
    else:  # پنج‌شنبه و جمعه
        days_to_saturday = (7 - current_weekday)
        deadline = (now + jdatetime.timedelta(days=days_to_saturday)).replace(hour=23, minute=59, second=59)
    
    # محاسبه ساعات باقی‌مانده
    hours_remaining = int((deadline - now).total_seconds() // 3600)
    
    logging.debug(f"مهلت: {deadline.strftime('%Y/%m/%d')}, ساعات باقی‌مانده: {hours_remaining}")
    return deadline.strftime('%Y/%m/%d'), hours_remaining

def is_admin(user_id, chat_id):
    """بررسی ادمین بودن کاربر

    پارامترها:
        user_id (int): شناسه کاربر
        chat_id (int): شناسه گروه

    خروجی:
        bool: True اگر کاربر ادمین باشد، False در غیر این صورت
    """
    administrators = get_chat_administrators(chat_id)  # دریافت لیست ادمین‌ها
    # ساخت مجموعه شناسه‌های ادمین‌ها
    admin_ids = {admin_info.get('user', {}).get('id') for admin_info in administrators}
    return user_id in admin_ids  # بررسی عضویت کاربر در لیست ادمین‌ها

# ذخیره‌سازی اطلاعات اعضای شناخته‌شده
# ساختار: {chat_id: {user_id: {name, id, first_name, last_name, added_time}}}
known_members = {}

# ذخیره‌سازی تمرین‌های تلاوت
# ساختار: {chat_id: {user_id: {status, score, date, message_id, exercise_day}}}
recitation_exercises = {}

# ذخیره‌سازی نمرات
# ساختار: {chat_id: {user_id: [نمرات]}}
exercise_scores = {}

# --- ثبت‌نام خصوصی ---
private_signup_states = {}  # {user_id: {'step': 'waiting_start'/'waiting_name_lastname', 'first_name': '', 'last_name': ''}}
registered_users = {}  # {user_id: {'first_name': ..., 'last_name': ..., 'mobile': ...}}
TXT_FILE = '1.txt'

def show_main_menu(chat_id, user_id):
    """نمایش منوی اصلی با دکمه‌های شیشه‌ای و پایین."""
    # Check if user is registered
    if user_id in registered_users:
        # Registered user - show original menu
        # دکمه‌های شیشه‌ای (بالا)
        inline_buttons = [
            [{'text': '📚 ثبت نام در مدرسه تلاوت', 'callback_data': 'school_registration'}],
            [{'text': '👤 حساب کاربری', 'callback_data': 'user_account'}]
        ]
        inline_keyboard = create_keyboard(inline_buttons, is_inline=True)
        
        # دکمه‌های پایین
        bottom_buttons = [
            [{'text': '📊 نظر سنجی', 'callback_data': 'survey'}],
            [{'text': 'ℹ️ در رابطه با ربات', 'callback_data': 'about_bot'}]
        ]
        bottom_keyboard = create_keyboard(bottom_buttons, is_inline=False)
        
        # ترکیب دکمه‌ها
        combined_keyboard = {
            "inline_keyboard": inline_keyboard.get("inline_keyboard", []),
            "keyboard": bottom_keyboard.get("keyboard", []),
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        
        send_message(chat_id, f"{log1} \n\nبه ربات تلاوت خوش آمدید! لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=combined_keyboard)
    else:
        # New user - show different menu
        # دکمه‌های شیشه‌ای (بالا)
        inline_buttons = [
            [{'text': '🏫 معرفی مدرسه تلاوت', 'callback_data': 'school_introduction'}],
            [{'text': '📚 ثبت نام در مدرسه تلاوت', 'callback_data': 'school_registration'}]
        ]
        inline_keyboard = create_keyboard(inline_buttons, is_inline=True)
        
        # دکمه‌های پایین
        bottom_buttons = [
            [{'text': '📊 نظر سنجی', 'callback_data': 'survey'}],
            [{'text': 'ℹ️ در رابطه با ربات', 'callback_data': 'about_bot'}]
        ]
        bottom_keyboard = create_keyboard(bottom_buttons, is_inline=False)
        
        # ترکیب دکمه‌ها
        combined_keyboard = {
            "inline_keyboard": inline_keyboard.get("inline_keyboard", []),
            "keyboard": bottom_keyboard.get("keyboard", []),
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        
        send_message(chat_id, f"{log1} \n\nبه ربات تلاوت خوش آمدید! لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=combined_keyboard)

def handle_school_introduction(chat_id, user_id):
    """معرفی مدرسه تلاوت برای کاربران جدید."""
    intro_text = "🏫 معرفی مدرسه تلاوت قرآن\n\n"
    intro_text += "🌟 مدرسه تلاوت قرآن، مرکزی تخصصی برای آموزش تلاوت قرآن کریم است.\n\n"
    intro_text += "📚 خدمات ما:\n"
    intro_text += "• آموزش تلاوت قرآن با اساتید مجرب\n"
    intro_text += "• کلاس‌های حضوری و آنلاین\n"
    intro_text += "• برنامه‌های متنوع برای همه سطوح\n"
    intro_text += "• گواهی پایان دوره معتبر\n\n"
    intro_text += "🎯 اهداف آموزشی:\n"
    intro_text += "• یادگیری اصول صحیح تلاوت\n"
    intro_text += "• تقویت صوت و لحن\n"
    intro_text += "• آشنایی با قواعد تجوید\n"
    intro_text += "• آمادگی برای مسابقات قرآنی\n\n"
    intro_text += "📞 برای اطلاعات بیشتر و ثبت نام، با ما در تماس باشید."
    
    # دکمه‌های پایین
    bottom_buttons = [
        [{'text': '📚 ثبت نام در مدرسه', 'callback_data': 'school_registration'}],
        [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
    ]
    bottom_keyboard = create_keyboard(bottom_buttons, is_inline=False)
    
    send_message(chat_id, intro_text, reply_markup=bottom_keyboard)

def start_registration(chat_id, user_id):
    """شروع فرآیند ثبت‌نام جدید."""
    # Check if the user is already in the 'waiting_name_lastname' step
    if user_id in private_signup_states and private_signup_states[user_id].get('step') == 'waiting_name_lastname':
        return # Already prompted, do nothing

    private_signup_states[user_id] = {'step': 'waiting_name_lastname'}
    send_message(chat_id, "نام و نام خانوادگی  مثال: محمدی علی).")

def handle_user_account(chat_id, user_id):
    """مدیریت حساب کاربری."""
    if user_id in registered_users:
        user_data = registered_users[user_id]
        account_info = f"👤 اطلاعات حساب کاربری:\n\n"
        account_info += f"نام: {user_data.get('first_name', '')}\n"
        account_info += f"نام خانوادگی: {user_data.get('last_name', '')}\n"
        account_info += f"موبایل: {user_data.get('mobile', '')}\n"
        account_info += f"کد ملی: {user_data.get('national_id', '')}\n"
        account_info += f"کلاس ثبت شده: {CLASSES.get(user_data.get('registered_class', ''), {}).get('name', 'ثبت نشده')}"
        
        keyboard = create_keyboard([
            [{'text': '📚 کلاس جدید', 'callback_data': 'new_class_registration'}],
            [{'text': '✏️ تصحیح اطلاعات', 'callback_data': 'edit_user_info'}],
            [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
        ])
        send_message(chat_id, account_info, reply_markup=keyboard)
    else:
        keyboard = create_keyboard([
            [{'text': '📚 ثبت نام در مدرسه', 'callback_data': 'school_registration'}],
            [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
        ])
        send_message(chat_id, "شما هنوز ثبت نام نکرده‌اید. لطفاً ابتدا ثبت نام کنید.", reply_markup=keyboard)

def handle_survey(chat_id, user_id):
    """مدیریت نظر سنجی."""
    survey_text = "📊 نظر سنجی ربات تلاوت\n\n"
    survey_text += "لطفاً نظر خود را درباره ربات به ما بگویید:\n"
    survey_text += "• کیفیت خدمات\n"
    survey_text += "• سهولت استفاده\n"
    survey_text += "• پیشنهادات بهبود"
    
    # دکمه‌های شیشه‌ای (بالا)
    inline_buttons = [
        [{'text': '⭐ عالی', 'callback_data': 'survey_excellent'}],
        [{'text': '👍 خوب', 'callback_data': 'survey_good'}],
        [{'text': '👎 نیاز به بهبود', 'callback_data': 'survey_needs_improvement'}]
    ]
    inline_keyboard = create_keyboard(inline_buttons, is_inline=True)
    
    # دکمه‌های پایین
    bottom_buttons = [
        [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
    ]
    bottom_keyboard = create_keyboard(bottom_buttons, is_inline=False)
    
    # ترکیب دکمه‌ها
    combined_keyboard = {
        "inline_keyboard": inline_keyboard.get("inline_keyboard", []),
        "keyboard": bottom_keyboard.get("keyboard", []),
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    
    send_message(chat_id, survey_text, reply_markup=combined_keyboard)

def handle_about_bot(chat_id, user_id):
    """مدیریت اطلاعات ربات."""
    about_text = "ℹ️ درباره ربات تلاوت\n\n"
    about_text += "🤖 این ربات برای مدیریت کلاس‌های تلاوت قرآن طراحی شده است.\n\n"
    about_text += "📚 قابلیت‌ها:\n"
    about_text += "• ثبت نام در کلاس‌های تلاوت\n"
    about_text += "• مدیریت حساب کاربری\n"
    about_text += "• ارسال و ارزیابی تمرینات\n"
    about_text += "• گزارش‌گیری از پیشرفت\n\n"
    about_text += "👨‍💻 توسعه‌دهنده: محمد \n"
    about_text += "📅 نسخه: 3.0"
    
    # فقط دکمه پایین
    bottom_buttons = [
        [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
    ]
    bottom_keyboard = create_keyboard(bottom_buttons, is_inline=False)
    
    send_message(chat_id, about_text, reply_markup=bottom_keyboard)

def start_name_registration(chat_id, user_id):
    """شروع ثبت نام با درخواست نام."""
    private_signup_states[user_id] = {'step': 'waiting_name_lastname'}
    send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: محمدی محمد):")

def show_name_confirmation(chat_id, user_id, first_name, last_name):
    """نمایش تایید نام و درخواست شماره تلفن."""
    # فقط دکمه پایین با request_contact
    bottom_keyboard = {
        "keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    
    # ترکیب نام و نام خانوادگی
    full_name = f"{first_name} {last_name}".strip()
    message_text = f"نام و فامیل: {full_name}\n\nلطفاً شماره تلفن خود را ارسال کنید:"
    
    # پیام با دکمه پایین بفرست
    send_message(chat_id, message_text, reply_markup=bottom_keyboard)
    
    # بعد دکمه شیشه‌ای تصحیح رو جداگانه بفرست
    inline_buttons = [
        [{'text': '✏️ تصحیح نام', 'callback_data': 'edit_name'}]
    ]
    inline_keyboard = create_keyboard(inline_buttons, is_inline=True)
    send_message(chat_id, "", reply_markup=inline_keyboard)

def show_phone_input_request(chat_id, user_id):
    """درخواست شماره تلفن با دکمه‌های پایین."""
    keyboard = create_keyboard([
        [{'text': '📱 ارسال شماره تلفن', 'request_contact': True}]
    ], is_inline=False)
    send_message(chat_id, "لطفاً شماره تلفن خود را ارسال کنید:", reply_markup=keyboard)

def show_phone_confirmation_with_buttons(chat_id, user_id, first_name, last_name, mobile):
    """نمایش تایید شماره تلفن با دکمه‌های پایین."""
    keyboard = create_keyboard([
        [{'text': '🆔 وارد کردن کد ملی', 'callback_data': 'enter_national_id'}],
        [{'text': '📊 نظر سنجی', 'callback_data': 'survey'}],
        [{'text': 'ℹ️ در رابطه با ربات', 'callback_data': 'about_bot'}],
        [{'text': '🔄 ثبت نام از اول', 'callback_data': 'restart_registration'}]
    ], is_inline=False)
    message_text = f"نام: {first_name}\nنام خانوادگی: {last_name}\nموبایل: {mobile}\n\nلطفاً کد ملی خود را وارد کنید (فقط اعداد انگلیسی):"
    send_message(chat_id, message_text, reply_markup=keyboard)

def show_survey_buttons(chat_id, user_id):
    """نمایش دکمه‌های نظر سنجی و درباره ربات."""
    keyboard = create_keyboard([
        [{'text': '📊 نظر سنجی', 'callback_data': 'survey'}],
        [{'text': 'ℹ️ در رابطه با ربات', 'callback_data': 'about_bot'}]
    ], is_inline=False)
    send_message(chat_id, "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=keyboard)

def show_phone_confirmation(chat_id, user_id, first_name, last_name, mobile):
    """نمایش تایید شماره تلفن و درخواست کد ملی."""
    keyboard = create_keyboard([
        [{'text': '🆔 وارد کردن کد ملی', 'callback_data': 'enter_national_id'}],
        [{'text': '✏️ تصحیح', 'callback_data': 'edit_phone'}]
    ])
    message_text = f"نام: {first_name}\nنام خانوادگی: {last_name}\nموبایل: {mobile}\n\nلطفاً کد ملی خود را وارد کنید (فقط اعداد انگلیسی):"
    send_message(chat_id, message_text, reply_markup=keyboard)

def show_final_confirmation(chat_id, user_id, first_name, last_name, mobile, national_id):
    """نمایش تایید نهایی و درخواست انتخاب کلاس."""
    keyboard = create_keyboard([
        [{'text': '📚 ورود به انتخاب کلاس', 'callback_data': 'select_class_final'}],
        [{'text': '✏️ تصحیح کد ملی', 'callback_data': 'edit_national_id'}]
    ])
    message_text = f"نام: {first_name}\nنام خانوادگی: {last_name}\nموبایل: {mobile}\nکد ملی: {national_id}\n\nاطلاعات شما تایید شد. حالا کلاس مورد نظر خود را انتخاب کنید:"
    send_message(chat_id, message_text, reply_markup=keyboard)

def show_classes(chat_id, user_id):
    """نمایش لیست کلاس‌ها به کاربر."""
    keyboard_buttons = []
    for class_id, class_info in CLASSES.items():
        keyboard_buttons.append([{'text': class_info['name'], 'callback_data': f'select_class_{class_id}'}])
    keyboard = create_keyboard(keyboard_buttons)
    send_message(chat_id, "لطفا کلاس مورد نظر خود را انتخاب کنید:", reply_markup=keyboard)
    private_signup_states[user_id]['step'] = 'waiting_for_class_selection'

def handle_class_selection(chat_id, user_id, class_id):
    """مدیریت انتخاب کلاس توسط کاربر."""
    if class_id in CLASSES:
        private_signup_states[user_id]['selected_class'] = class_id
        class_info = CLASSES[class_id]
        message_text = f"شما کلاس *{class_info['name']}* را انتخاب کردید.\nهزینه: {class_info['price']}\nبرنامه: {class_info['schedule']}\n\nبرای ادامه، لطفا پرداخت را انجام دهید."
        keyboard = create_keyboard([[{'text': 'لینک پرداخت', 'callback_data': f'show_payment_{class_id}'}]])
        send_message(chat_id, message_text, reply_markup=keyboard)
        private_signup_states[user_id]['step'] = 'waiting_for_payment_link_request'
    else:
        send_message(chat_id, "کلاس انتخابی نامعتبر است. لطفا دوباره تلاش کنید.")

def show_payment_link(chat_id, user_id, class_id):
    """نمایش لینک پرداخت به کاربر."""
    payment_link = PAYMENT_LINKS.get(class_id)
    if payment_link:
        message_text = f"لطفا برای نهایی کردن ثبت‌نام، از طریق لینک زیر پرداخت را انجام دهید:\n{payment_link}\n\nپس از پرداخت، روی دکمه 'پرداخت کردم' کلیک کنید."
        keyboard = create_keyboard([[{'text': 'پرداخت کردم', 'callback_data': 'payment_completed'}]])
        send_message(chat_id, message_text, reply_markup=keyboard)
        private_signup_states[user_id]['step'] = 'waiting_for_payment_confirmation'
    else:
        send_message(chat_id, "لینک پرداخت برای این کلاس موجود نیست.")

def handle_payment_completion(chat_id, user_id):
    """مدیریت تایید پرداخت توسط کاربر."""
    if user_id in private_signup_states and 'selected_class' in private_signup_states[user_id]:
        selected_class_id = private_signup_states[user_id]['selected_class']
        class_name = CLASSES[selected_class_id]['name']
        
        # Check if this is an editing session
        is_editing = private_signup_states[user_id].get('is_editing', False)
        
        # ذخیره اطلاعات کاربر
        registered_users[user_id] = {
            'first_name': private_signup_states[user_id]['first_name'],
            'last_name': private_signup_states[user_id]['last_name'],
            'mobile': private_signup_states[user_id]['mobile'],
            'national_id': private_signup_states[user_id].get('national_id'),
            'registered_class': selected_class_id
        }
        save_users_to_file()

        if is_editing:
            success_message = f"اطلاعات شما با موفقیت به‌روزرسانی شد.\nکلاس: *{class_name}*"
        else:
            success_message = f"تبریک می‌گوییم! ثبت‌نام شما در کلاس *{class_name}* با موفقیت انجام شد.\nلینک ورود به کلاس به زودی برای شما ارسال خواهد شد.\n\nاز همراهی شما سپاسگزاریم!\n\nلینک کانال آموزشی: [لینک کانال](https://t.me/your_educational_channel)"
        
        # Show success message with main menu options
        keyboard = create_keyboard([
            [{'text': '👤 حساب کاربری', 'callback_data': 'user_account'}],
            [{'text': '📚 کلاس جدید', 'callback_data': 'new_class_registration'}],
            [{'text': '📊 نظر سنجی', 'callback_data': 'survey'}],
            [{'text': 'ℹ️ در رابطه با ربات', 'callback_data': 'about_bot'}]
        ])
        send_message(chat_id, success_message, reply_markup=keyboard)
        private_signup_states[user_id]['step'] = 'registered'
    else:
        send_message(chat_id, "خطا در تکمیل فرآیند پرداخت. لطفا دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.")

# تابع ذخیره‌سازی اطلاعات کاربران در فایل
# فقط آخرین اطلاعات هر کاربر ذخیره می‌شود
# هیچ append یا ذخیره تکراری انجام نمی‌شود
def save_users_to_file():
    try:
        with open(TXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(registered_users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f'خطا در ذخیره فایل: {e}')

# تابع بارگذاری اطلاعات کاربران از فایل (در شروع برنامه)
def load_users_from_file():
    global registered_users
    if os.path.exists(TXT_FILE):
        try:
            with open(TXT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    registered_users = data
        except Exception as e:
            logging.error(f'خطا در خواندن فایل: {e}')

load_users_from_file()

def add_known_member(user_info, chat_id):
    """افزودن عضو جدید به لیست اعضای شناخته‌شده

    پارامترها:
        user_info (dict): اطلاعات کاربر
        chat_id (int): شناسه گروه
    """
    user_id = user_info.get('id')
    if not user_id:
        logging.error("شناسه کاربر نامعتبر است")
        return
    
    # افزودن به لیست اعضای شناخته‌شده
    if chat_id not in known_members:
        known_members[chat_id] = {}
    if user_id not in known_members[chat_id]:
        known_members[chat_id][user_id] = {
            'name': get_simple_name(user_info),
            'id': user_id,
            'first_name': user_info.get('first_name', ''),
            'last_name': user_info.get('last_name', ''),
            'added_time': time.time()
        }
    
    # ایجاد رکورد تمرین برای عضو جدید
    if chat_id not in recitation_exercises:
        recitation_exercises[chat_id] = {}
    if user_id not in recitation_exercises[chat_id]:
        recitation_exercises[chat_id][user_id] = {
            'status': 'waiting',      # وضعیت: منتظر تلاوت
            'score': None,            # نمره: هنوز ثبت نشده
            'date': '',               # تاریخ ارسال
            'message_id': None,       # شناسه پیام تلاوت
            'exercise_day': 'Saturday' # روز تلاوت
        }

def handle_recitation_exercise(message):
    """پردازش ارسال تمرین تلاوت

    پارامترها:
        message (dict): پیام دریافتی از کاربر

    خروجی:
        bool: True اگر پیام تمرین معتبر باشد، False در غیر این صورت
    """
    # استخراج اطلاعات اصلی از پیام
    chat_id = message['chat']['id']      # شناسه گروه
    user_info = message['from']          # اطلاعات فرستنده
    user_id = user_info.get('id')        # شناسه کاربر
    user_name = get_simple_name(user_info)  # نام کاربر
    
    # بررسی نوع فایل ارسالی
    has_voice = 'voice' in message  # آیا فایل صوتی ضبط شده دارد
    has_audio = 'audio' in message  # آیا فایل صوتی آپلود شده دارد
    
    # بررسی متن توضیحات
    text = message.get('caption', '').lower()  # متن توضیحات (تبدیل به حروف کوچک)
    exercise_pattern = r'\b(تلاوت|تمرین|ارسال تلاوت)\b'  # الگوی جستجوی کلمات کلیدی
    is_exercise = bool(re.search(exercise_pattern, text, re.IGNORECASE))  # آیا کلمات کلیدی در متن هست
    
    # اگر فرستنده ادمین باشد، تمرین را نادیده می‌گیریم
    if is_admin(user_id, chat_id):
        logging.info(f"ادمین {user_name} ({user_id}) سعی کرد تمرین ارسال کند. نادیده گرفته شد.")
        return False

    # اگر پیام شامل فایل صوتی و کلمات کلیدی باشد
    if (has_voice or has_audio) and is_exercise:
        now = jdatetime.datetime.now()  # زمان فعلی
        weekday = now.weekday()         # روز هفته
        
        # تعیین روز تلاوت و بررسی مهلت ارسال
        if weekday == 0:  # شنبه
            exercise_day = 'Saturday'
        elif weekday in [1, 2]:  # یکشنبه و دوشنبه
            exercise_day = 'Monday'
        elif weekday in [3, 4]:  # سه‌شنبه و چهارشنبه
            exercise_day = 'Wednesday'
        else:  # پنج‌شنبه و جمعه
            send_message(chat_id, "⚠️ مهلت ارسال تلاوت به پایان رسیده است. لطفاً در روزهای تعیین شده تلاوت خود را ارسال کنید.")
            return False
        
        # اطمینان از وجود ساختار داده برای گروه
        if chat_id not in recitation_exercises:
            recitation_exercises[chat_id] = {}
        
        # ثبت اطلاعات تمرین
        recitation_exercises[chat_id][user_id] = {
            'status': 'sent',                    # وضعیت: ارسال شده
            'score': None,                       # نمره: هنوز ثبت نشده
            'date': get_jalali_date(),           # تاریخ ارسال
            'message_id': message['message_id'],  # شناسه پیام
            'user_name': user_name,              # نام کاربر
            'exercise_day': exercise_day         # روز تمرین
        }
        
        # تولید و ارسال گزارش وضعیت تمرین‌ها
        report_message = generate_exercise_report(chat_id)
        send_message(chat_id, report_message)
        
        return True  # تمرین با موفقیت ثبت شد
    
    return False  # پیام، تمرین معتبر نیست

def handle_admin_score(message):
    """پردازش نمره‌دهی توسط ادمین

    پارامترها:
        message (dict): پیام دریافتی از ادمین

    خروجی:
        bool: True اگر نمره‌دهی موفق باشد، False در غیر این صورت
    """
    # استخراج اطلاعات اصلی از پیام
    chat_id = message['chat']['id']      # شناسه گروه
    user_info = message['from']          # اطلاعات ادمین
    user_id = user_info.get('id')        # شناسه ادمین
    
    # بررسی ادمین بودن فرستنده
    if not is_admin(user_id, chat_id):
        return False
    
    # بررسی پاسخ به پیام تمرین
    if 'reply_to_message' not in message:
        return False
    
    # استخراج اطلاعات پیام تمرین
    reply_message = message['reply_to_message']           # پیام تمرین
    replied_user_id = reply_message['from']['id']        # شناسه کاربر
    replied_message_id = reply_message['message_id']     # شناسه پیام
    
    # بررسی وجود رکورد تمرین
    if chat_id not in recitation_exercises or replied_user_id not in recitation_exercises[chat_id]:
        return False
    
    # بررسی تطابق شناسه پیام
    exercise_data = recitation_exercises[chat_id][replied_user_id]
    if exercise_data.get('message_id') != replied_message_id:
        return False  # پیام مورد نظر، تمرین نیست
    
    # استخراج نمره از متن پیام
    text = message.get('text', '').lower()                # متن پیام (تبدیل به حروف کوچک)
    score_pattern = r'\b(عالی|خوب|بد)\b'                # الگوی جستجوی نمره
    match = re.search(score_pattern, text, re.IGNORECASE)  # جستجوی نمره در متن
    score = match.group(0) if match else None             # استخراج نمره
    
    # اگر نمره معتبر باشد و قبلاً نمره‌ای ثبت نشده باشد
    if score and not exercise_data.get('score'):
        exercise_data['score'] = score  # ثبت نمره در رکورد تمرین
        
        # اطمینان از وجود ساختار داده برای نمرات
        if chat_id not in exercise_scores:
            exercise_scores[chat_id] = {}
        if replied_user_id not in exercise_scores[chat_id]:
            exercise_scores[chat_id][replied_user_id] = []
        
        # افزودن نمره جدید به تاریخچه نمرات
        exercise_scores[chat_id][replied_user_id].append({
            'score': score,                                         # نمره
            'date': get_jalali_date(),                             # تاریخ
            'week_day': exercise_data.get('exercise_day', get_week_day())  # روز هفته
        })
        
        # تهیه و ارسال پیام تأیید نمره
        user_name = exercise_data.get('user_name', 'کاربر')
        response = f"🎯 استاد به شما این نمره رو داد: **{score}**\n\n"  # پیام اصلی
        response += f"👤 {user_name}\n"                                   # نام کاربر
        response += f"📅 {get_jalali_date()}\n{get_week_day()}\n\n"       # تاریخ و روز
        # افزودن گزارش کامل تمرین‌ها
        response += generate_exercise_report(chat_id, immediate=True, scored_user=user_name, scored_value=score)
        send_message(chat_id, response)  # ارسال پیام
        
        return True  # نمره‌دهی موفق
    
    return False  # نمره‌دهی ناموفق

def generate_exercise_report(chat_id, immediate=False, scored_user=None, scored_value=None):
    """تولید گزارش وضعیت تمرین‌ها

    پارامترها:
        chat_id (int): شناسه گروه
        immediate (bool): آیا گزارش بلافاصله بعد از نمره‌دهی است
        scored_user (str): نام کاربری که نمره گرفته
        scored_value (str): نمره داده شده

    خروجی:
        str: متن گزارش آماده شده
    """
    global quote_index  # شاخص پیام انگیزشی
    
    # بررسی وجود اعضا
    if chat_id not in known_members:
        return "هیچ عضوی ثبت نشده!"
    
    # شروع گزارش با عنوان و تاریخ
    report = f"📋 گزارش تمرین تلاوت\n\n"  # عنوان گزارش
    report += f"📅 {get_week_day()} {get_jalali_date()}"  # تاریخ و روز
    
    # افزودن اطلاعات نمره جدید (اگر وجود داشته باشد)
    if immediate and scored_user:
        report += f"🆕 نمره جدید: {scored_user} - {scored_value}\n\n"
    
    # نمایش وضعیت روز تمرین
    if is_exercise_day():
        report += f"🟢 امروز روز تمرین است ({get_week_day()})\n\n"
    else:
        report += f"🔴 امروز روز تمرین نیست ({get_week_day()})\n\n"
    
    # لیست‌های مختلف برای دسته‌بندی وضعیت تمرین‌ها
    sent_exercises = []      # تمرین‌های ارسال شده
    waiting_exercises = []    # در انتظار ارسال تمرین
    scored_exercises = []     # تمرین‌های نمره‌دهی شده
    
    # تعیین روز تمرین فعلی
    current_exercise_day = (
        # تعیین روز تمرین بر اساس روز هفته
        'Saturday' if jdatetime.datetime.now().weekday() == 5 else    # شنبه
        'Monday' if jdatetime.datetime.now().weekday() in [6, 0] else  # یکشنبه و دوشنبه
        'Wednesday' if jdatetime.datetime.now().weekday() == 1 else    # سه‌شنبه
        'Thursday'                                                      # پنج‌شنبه
    )
    
    # دریافت لیست ادمین‌ها برای حذف آنها از گزارش
    administrators = get_chat_administrators(chat_id)
    admin_ids = {admin_info.get('user', {}).get('id') for admin_info in administrators}

    # بررسی وضعیت تمرین هر کاربر در گروه
    for user_id, user_data in known_members[chat_id].items():
        # نادیده گرفتن ادمین‌ها در گزارش
        if user_id in admin_ids:
            continue
        user_name = user_data['name']  # دریافت نام کاربر برای نمایش در گزارش
        
        # بررسی وجود رکورد تمرین برای کاربر
        if chat_id in recitation_exercises and user_id in recitation_exercises[chat_id]:
            exercise = recitation_exercises[chat_id][user_id]
            
            # اگر تمرین ارسال شده و مربوط به روز جاری است
            if exercise['status'] == 'sent' and exercise.get('exercise_day') == current_exercise_day:
                if exercise['score']:  # اگر نمره داده شده
                    scored_exercises.append(f"✅ {user_name} - نمره: {exercise['score']}")
                else:  # در انتظار نمره
                    sent_exercises.append(f"⏳ {user_name} - در انتظار بررسی")
            else:  # تمرین ارسال نشده
                waiting_exercises.append(f"❌ {user_name} - در انتظار تمرین")
        else:  # رکورد تمرین وجود ندارد
            waiting_exercises.append(f"❌ {user_name} - در انتظار تمرین")
    
    # افزودن لیست تمرین‌های نمره‌دهی شده به گزارش
    if scored_exercises:
        report += "🎯 نمره گرفته‌ها:\n"
        for item in scored_exercises:
            report += f"{item}\n"
        report += "\n"
    
    if sent_exercises:
        report += "⏳ تمرین‌های در انتظار نمره:\n"
        for item in sent_exercises:
            report += f"{item}\n"
        report += "\n"
    
    if waiting_exercises:
        report += "❌ در انتظار تمرین:\n"
        for item in waiting_exercises:
            report += f"{item}\n"
        report += "\n"
    
    total = len(known_members[chat_id])
    sent_count = len(sent_exercises) + len(scored_exercises)
    participation_percentage = (sent_count / total * 100) if total > 0 else 0
    
    report += f"📊 آمار کلی:\n"
    report += f"👥 کل اعضا: {total}\n"
    report += f"📤 تمرین فرستاده: {sent_count}\n"
    report += f"📥 در انتظار: {len(waiting_exercises)}\n"
    report += f"📈 درصد مشارکت: {participation_percentage:.1f}%\n\n"
    
    report += f"💡 پیام انگیزشی:\n{motivational_quotes[quote_index]}\n\n"
    quote_index = (quote_index + 1) % len(motivational_quotes)
    
    deadline, hours_remaining = get_exercise_deadline()
    report += f"⏰ مهلت ارسال تمرین:\n"
    report += f"تا پایان {deadline} ({hours_remaining} ساعت باقی‌مانده)\n"
    report += "🏃‍♂️ عجله کنید، فرصت را از دست ندهید!"
    
    return report

def generate_score_report(chat_id):
    """تولید گزارش کلی نمرات اعضای گروه
    
    این تابع گزارشی از وضعیت نمرات تمام اعضای گروه تولید می‌کند. گزارش شامل:
    - دسته‌بندی کاربران بر اساس آخرین نمره (عالی، خوب، نیاز به تلاش)
    - لیست افرادی که هنوز تمرین ارسال نکرده‌اند
    - تاریخ و روز هفته
    
    Args:
        chat_id: شناسه یکتای گروه
    
    Returns:
        None - پیام مستقیماً به گروه ارسال می‌شود
    """
    global quote_index
    
    # بررسی وجود نمره در گروه
    if chat_id not in exercise_scores or not any(exercise_scores[chat_id].values()):
        send_message(chat_id, "هنوز هیچ نمره‌ای ثبت نشده!")
        return
    
    # شروع ساخت گزارش با عنوان و تاریخ
    report = f"🏆 گزارش کلی نمرات\n\n"
    report += f"📅 {get_week_day()} {get_jalali_date()}\n\n"
    
    # لیست‌های مختلف برای دسته‌بندی کاربران بر اساس نمره
    excellent_users = []  # کاربران با نمره عالی
    good_users = []       # کاربران با نمره خوب
    bad_users = []        # کاربران با نمره نیاز به تلاش
    no_exercise = []      # کاربران بدون تمرین
    
    # دریافت لیست ادمین‌ها برای حذف از گزارش
    administrators = get_chat_administrators(chat_id)
    admin_ids = {admin_info.get('user', {}).get('id') for admin_info in administrators}

    # بررسی و دسته‌بندی هر کاربر بر اساس آخرین نمره
    for user_id, user_data in known_members[chat_id].items():
        # نادیده گرفتن ادمین‌ها در گزارش
        if user_id in admin_ids:
            continue
        user_name = user_data['name']
        
        # بررسی وجود نمره برای کاربر
        if user_id in exercise_scores[chat_id] and exercise_scores[chat_id][user_id]:
            # دریافت آخرین نمره کاربر
            last_score = exercise_scores[chat_id][user_id][-1]['score']
            
            # دسته‌بندی کاربر بر اساس نمره
            if last_score == 'عالی':
                excellent_users.append(user_name)
            elif last_score == 'خوب':
                good_users.append(user_name)
            elif last_score == 'بد':
                bad_users.append(user_name)
        else:  # کاربر بدون نمره
            no_exercise.append(user_name)
    
    if excellent_users:
        report += "🌟 عالی:\n"
        for i, name in enumerate(sorted(excellent_users), 1):
            report += f"{i}. {name}\n"
        report += "\n"
    
    if good_users:
        report += "👍 خوب:\n"
        for i, name in enumerate(sorted(good_users), 1):
            report += f"{i}. {name}\n"
        report += "\n"
    
    if bad_users:
        report += "👎 بد:\n"
        for i, name in enumerate(sorted(bad_users), 1):
            report += f"{i}. {name}\n"
        report += "\n"
    
    if no_exercise:
        report += "❌ بدون تمرین:\n"
        for i, name in enumerate(sorted(no_exercise), 1):
            report += f"{i}. {name}\n"
        report += "\n"
    
    total = len(known_members[chat_id])
    report += f"📊 آمار:\n"
    report += f"🌟 عالی: {len(excellent_users)}\n"
    report += f"👍 خوب: {len(good_users)}\n"
    report += f"👎 بد: {len(bad_users)}\n"
    report += f"❌ بدون تمرین: {len(no_exercise)}\n"
    report += f"👥 کل: {total}\n\n"
    
    report += f"💡 پیام انگیزشی:\n{motivational_quotes[quote_index]}\n\n"
    quote_index = (quote_index + 1) % len(motivational_quotes)
    
    deadline, hours_remaining = get_exercise_deadline()
    report += f"⏰ مهلت ارسال تمرین:\n"
    report += f"تا پایان {deadline} ({hours_remaining} ساعت باقی‌مانده)\n"
    report += "🏃‍♂️ عجله کنید، فرصت را از دست ندهید!"
    
    send_message(chat_id, report)

def get_simple_members_list(chat_id):
    """تهیه لیست ساده از اعضای گروه
    
    این تابع لیستی از تمام اعضای گروه را به همراه آمار کلی تهیه می‌کند.
    لیست شامل دو بخش اصلی است:
    - لیست ادمین‌ها
    - لیست دانش‌آموزان (قرآن‌آموزان)
    
    Args:
        chat_id: شناسه یکتای گروه
    
    Returns:
        str: گزارش کامل شامل لیست اعضا و آمار گروه
    """
    # دریافت اطلاعات ادمین‌ها
    administrators = get_chat_administrators(chat_id)
    admin_ids = {admin_info.get('user', {}).get('id') for admin_info in administrators}
    admin_names = sorted([get_simple_name(admin_info.get('user', {})) for admin_info in administrators])
    
    # تهیه لیست قرآن‌آموزان (به جز ادمین‌ها)
    regular_members = sorted([user_info['name'] for user_id, user_info in known_members.get(chat_id, {}).items() 
                            if user_id not in admin_ids])
    
    report = f"📋 لیست اعضای گروه\n\n"
    report += f"📅 {get_week_day()} {get_jalali_date()}"
    
    report += "👑 ادمین‌های گروه:\n"
    if admin_names:
        for admin_name in admin_names:
            report += f"- {admin_name}\n"
    report += "\n"
    
    report += "👥 دانش‌آموزان مدرسه تلاوت:\n"
    if regular_members:
        for i, member_name in enumerate(regular_members, 1):
            report += f"{i}. {member_name}\n"
    report += "\n"
    
    total_known = len(regular_members)
    total_admins = len(admin_names)
    total_group = get_chat_member_count(chat_id)
    
    report += f"📊 آمار:\n"
    report += f"👑 تعداد ادمین‌ها: {total_admins} نفر\n"
    report += f"👥 تعداد قرآن‌آموزان: {total_known} نفر\n"
    report += f"🔍 کل اعضای عضو شده: {total_known + total_admins} نفر\n"
    report += f"👥 کل اعضای گروه: {total_group} نفر\n\n"
    
    if total_known < total_group - total_admins:
        report += "💡 نکته: شاگردان عزیز لطفا /عضو شوید برای ارسال تمرین و ارزیابی \n\n"
        report += "⚠️ محدودیت: API .بله، امکان دریافت همه اعضا را نمی‌دهد. پس عزیزان باید حتما عضو شوند"
    
    return report

def welcome_new_member(chat_id, user_info):
    """خوش‌آمدگویی به عضو جدید و درخواست عضویت
    
    این تابع پیام خوش‌آمدگویی را برای اعضای جدید (غیر ادمین) ارسال می‌کند
    و از آنها می‌خواهد که با دستور /عضو در لیست گروه ثبت‌نام کنند.
    
    Args:
        chat_id: شناسه یکتای گروه
        user_info: اطلاعات کاربر جدید شامل شناسه و نام
    """
    # دریافت شناسه کاربر
    user_id = user_info.get('id')
    
    # ارسال پیام خوش‌آمدگویی فقط برای کاربران غیر ادمین
    if not is_admin(user_id, chat_id):
        user_name = get_simple_name(user_info)
        welcome_msg = f"🎉 سلام {user_name}!\n\n"
        welcome_msg += "برای ثبت در لیست گروه، لطفاً /عضو بزنید 👍\n"
        welcome_msg += f"📅 {get_week_day()} {get_jalali_date()}"
        send_message(chat_id, welcome_msg)

def handle_callback_query(message):
    """پردازش دکمه‌های شیشه‌ای (اینلاین) ربات
    
    این تابع پاسخ‌های مربوط به دکمه‌های شیشه‌ای ربات را مدیریت می‌کند.
    
    Args:
        message: پیام دریافتی از تلگرام شامل اطلاعات چت و کاربر
    """
    user_id = message['from']['id']
    chat_id = message['message']['chat']['id'] if 'message' in message and 'chat' in message['message'] else None

    if chat_id is None:
        # Log an error or handle cases where chat_id is not available from the message
        # For now, we'll just return if chat_id cannot be determined
        print("Error: chat_id not found in callback_query message.")
        return
    callback_data = message['data']

    if callback_data == 'request_membership':
        send_message(chat_id, "درخواست عضویت شما دریافت شد. لطفا منتظر تایید ادمین باشید.")
    elif callback_data == 'start_private_registration':
        start_registration(chat_id, user_id)
    elif callback_data == 'confirm_info':
        if user_id in private_signup_states and private_signup_states[user_id]['step'] == 'waiting_for_info_confirmation':
            show_classes(chat_id, user_id)
        else:
            send_message(chat_id, "خطا در فرآیند ثبت نام. لطفا دوباره از /شروع استفاده کنید.")
    elif callback_data == 'edit_info':
        private_signup_states[user_id] = {'step': 'waiting_name_lastname'}
        send_message(chat_id, "لطفا نام و نام خانوادگی خود را دوباره وارد کنید (مثال: محمدی علی).")
    elif callback_data.startswith('select_class_'):
        class_id = callback_data.replace('select_class_', '')
        handle_class_selection(chat_id, user_id, class_id)
    elif callback_data.startswith('show_payment_'):
        class_id = callback_data.replace('show_payment_', '')
        show_payment_link(chat_id, user_id, class_id)
    elif callback_data == 'payment_completed':
        handle_payment_completion(chat_id, user_id)
    elif callback_data == 'start_bot_features':
        welcome_message =   "به ربات ارم1 تلاوت م خوش آمدید!\n\n"
        send_message(chat_id, welcome_message)
    # New callback handlers for the main menu system
    elif callback_data == 'school_registration':
        if user_id in registered_users:
            # User is already registered, show class selection
            show_classes(chat_id, user_id)
        else:
            # User is not registered, start registration process
            start_name_registration(chat_id, user_id)
    elif callback_data == 'user_account':
        handle_user_account(chat_id, user_id)
    elif callback_data == 'survey':
        handle_survey(chat_id, user_id)
    elif callback_data == 'about_bot':
        handle_about_bot(chat_id, user_id)
    elif callback_data == 'school_introduction':
        handle_school_introduction(chat_id, user_id)
    elif callback_data == 'back_to_main_menu':
        show_main_menu(chat_id, user_id)
    elif callback_data == 'new_class_registration':
        show_classes(chat_id, user_id)
    elif callback_data == 'share_phone':
        if user_id in private_signup_states:
            state = private_signup_states[user_id]
            # Create contact sharing keyboard
            contact_keyboard = create_keyboard([[
                {'text': '📱 ارسال شماره تلفن', 'request_contact': True}
            ]], is_inline=False)
            send_message(chat_id, "لطفاً روی دکمه زیر کلیک کنید تا شماره تلفن شما ارسال شود:", reply_markup=contact_keyboard)
            state['step'] = 'waiting_phone_contact'
    elif callback_data == 'enter_national_id':
        if user_id in private_signup_states:
            state = private_signup_states[user_id]
            state['step'] = 'waiting_national_id'
            send_message(chat_id, "لطفاً کد ملی خود را وارد کنید (فقط اعداد انگلیسی - 10 رقم):")
    elif callback_data == 'select_class_final':
        if user_id in private_signup_states:
            show_classes(chat_id, user_id)
    elif callback_data == 'edit_name':
        if user_id in private_signup_states:
            state = private_signup_states[user_id]
            state['step'] = 'waiting_name_lastname'
            send_message(chat_id, "لطفاً نام و نام خانوادگی خود را دوباره وارد کنید (مثال: محمدی علی):")
    elif callback_data == 'edit_phone':
        if user_id in private_signup_states:
            state = private_signup_states[user_id]
            show_phone_input_request(chat_id, user_id)
            state['step'] = 'waiting_phone_contact'
    elif callback_data == 'edit_national_id':
        if user_id in private_signup_states:
            state = private_signup_states[user_id]
            state['step'] = 'waiting_national_id'
            send_message(chat_id, "لطفاً کد ملی خود را دوباره وارد کنید (فقط اعداد انگلیسی - 10 رقم):")
    elif callback_data == 'restart_registration':
        if user_id in private_signup_states:
            # Clear registration state and start over
            private_signup_states[user_id] = {'step': 'waiting_name_lastname'}
            send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: محمدی علی):")
    elif callback_data == 'edit_user_info':
        if user_id in registered_users:
            # Start editing process for registered user
            user_data = registered_users[user_id]
            private_signup_states[user_id] = {
                'step': 'waiting_name_lastname',
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'mobile': user_data.get('mobile', ''),
                'national_id': user_data.get('national_id', ''),
                'is_editing': True
            }
            send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: محمدی علی):")
    elif callback_data in ['survey_excellent', 'survey_good', 'survey_needs_improvement']:
        survey_responses = {
            'survey_excellent': '⭐ عالی',
            'survey_good': '👍 خوب', 
            'survey_needs_improvement': '👎 نیاز به بهبود'
        }
        response = survey_responses.get(callback_data, '')
        send_message(chat_id, f"از نظر شما متشکریم! ({response})\n\nنظر شما ثبت شد.")
        show_main_menu(chat_id, user_id)


def process_message(message):
    """پردازش پیام‌های دریافتی از کاربران
    
    این تابع اصلی‌ترین تابع پردازش پیام‌های ربات است که وظایف زیر را انجام می‌دهد:
    - بررسی نوع چت (فقط در گروه کار می‌کند)
    - شناسایی کاربر و وضعیت ادمین بودن
    - ثبت کاربر در لیست اعضای عضو شده
    - پردازش دستورات مختلف ربات
    
    Args:
        message: پیام دریافتی از تلگرام شامل تمام اطلاعات پیام
    """
    # دریافت اطلاعات اصلی از پیام
    chat_id = message['chat']['id']
    chat_type = message['chat']['type']
    user_info = message['from']
    user_id = user_info.get('id')

    # --- ثبت‌نام خصوصی ---
    if chat_type == 'private':
        if user_id not in private_signup_states:
            private_signup_states[user_id] = {'step': 'waiting_start', 'first_name': '', 'last_name': '', 'mobile': '', 'national_id': ''}
        state = private_signup_states[user_id]

        if 'text' in message and message['text'].strip() == '/start':
            # Check if user is already registered
            if user_id in registered_users:
                user_data = registered_users[user_id]
                welcome_text = f"سلام {user_data.get('first_name', 'کاربر')} عزیز!\n\nبه ربات تلاوت خوش آمدید!"
                keyboard = create_keyboard([
                    [{'text': '📚 کلاس جدید', 'callback_data': 'new_class_registration'}],
                    [{'text': '👤 حساب کاربری', 'callback_data': 'user_account'}],
                    [{'text': '📊 نظر سنجی', 'callback_data': 'survey'}],
                    [{'text': 'ℹ️ در رابطه با ربات', 'callback_data': 'about_bot'}]
                ])
                send_message(chat_id, welcome_text, reply_markup=keyboard)
            else:
                # New user - show main menu
                show_main_menu(chat_id, user_id)
            return          

        if state.get('step') == 'waiting_name_lastname' and 'text' in message:
            parts = message['text'].strip().split()
            if len(parts) >= 2:
                state['first_name'] = parts[0]
                state['last_name'] = ' '.join(parts[1:])
                show_name_confirmation(chat_id, user_id, parts[0], ' '.join(parts[1:]))
            else:
                send_message(chat_id, "لطفا نام و نام خانوادگی خود را به درستی وارد کنید (مثال: محمدی علی).")
            return

        if state.get('step') == 'waiting_phone_contact' and 'contact' in message:
            mobile = message['contact'].get('phone_number', '')
            state['mobile'] = mobile
            show_phone_confirmation_with_buttons(chat_id, user_id, state['first_name'], state['last_name'], mobile)
            return

        if state.get('step') == 'waiting_national_id' and 'text' in message:
            national_id = message['text'].strip()
            # Check if only English numbers are used
            if re.fullmatch(r'[0-9]{10}', national_id) and not re.search(r'[۰-۹]', national_id):
                state['national_id'] = national_id
                show_final_confirmation(chat_id, user_id, state['first_name'], state['last_name'], state['mobile'], national_id)
            else:
                send_message(chat_id, "کد ملی نامعتبر است. لطفا فقط اعداد انگلیسی استفاده کنید (10 رقم).")
            return



    # بررسی استفاده از ربات در گروه
    if chat_type not in ['group', 'supergroup']:
        send_message(chat_id, "این ربات فقط در گروه‌ها کار می‌کند!")
        return
    
    # دریافت اطلاعات کاربر
    user_info = message['from']
    user_id = user_info.get('id')
    
    # بررسی وضعیت ادمین بودن کاربر
    is_admin_user = is_admin(user_id, chat_id)
    
    # ثبت کاربر در لیست اعضای عضو شده
    add_known_member(user_info, chat_id)
    
    # پردازش پیام‌های متنی
    if 'text' in message:
        text = message['text'].strip().lower()
        
        # دستور شروع - فقط برای ادمین‌ها
        if (text == '/شروع') and is_admin_user:
            # ساخت پیام راهنمای ربات
            welcome = "🤖 ربات ارزیابی تلاوت در گروه\n\n"
            welcome += "دستورات:\n"
            welcome += "👥 /شروع - فقط با اجازه ادمین\n"
            welcome += "📋 /لیست - لیست اعضای \n"
            welcome += "🎯 /گزارش - گزارش تمرینات\n"
            welcome += "🏆 /نمرات - گزارش نمرات\n"
            welcome += "👥 /عضو  - ثبت نام عضو جدید\n\n"
            welcome += "🎵 نحوه کار:\n"
            welcome += "•با کپشن 'ارسال‌تلاوت' تمرین خود را ارسال کنید.\n"
            welcome += "•با ریپلای 'عالی'، 'خوب' یا 'بد' ارزیابی خواهید شد.\n\n"
            welcome += f"📅 امروز: {get_week_day()} ، {get_jalali_date()}\n"
            welcome += "⏰ روزهای تمرین: شنبه، دوشنبه، چهارشنبه"
            send_message(chat_id, welcome)
        elif text == '/عضو' and not is_admin_user:
            administrators = get_chat_administrators(chat_id)
            admin_ids = {admin_info.get('user', {}).get('id') for admin_info in administrators}
            regular_members = sorted([user_info['name'] for user_id, user_info in known_members.get(chat_id, {}).items() 
                                    if user_id not in admin_ids])
            user_name = get_simple_name(user_info)
            response = f"🎉 {user_name} ورودت رو به کلاس تبریک می‌گم!\n\n"
            response += "👥  قرآن‌آموزان:\n"
            for i, member_name in enumerate(regular_members, 1):
                response += f"{i}. {member_name}\n"
            response += f"\n📅 امروز: {get_week_day()} ، {get_jalali_date()}\n\n"
            response += "از قرآن‌آموزان تازه به گروه آمده درخواست می‌شود روی /عضو ضربه بزنند. با تشکر"
            send_message(chat_id, response)
        elif text == '/لیست':
            report = get_simple_members_list(chat_id)
            send_message(chat_id, report)
        elif is_admin_user and text in ['/گزارش']:
            report = generate_exercise_report(chat_id)
            send_message(chat_id, report)
     #   elif is_admin_user and text in ['/استارت', '/نمرات']:
        elif is_admin_user and text in ['/نمرات']:
            generate_score_report(chat_id)


3.
def process_new_chat_member(message):
    """پردازش عضو جدید گروه
    
    این تابع وظیفه خوش‌آمدگویی و ثبت اعضای جدید گروه را بر عهده دارد.
    برای هر عضو جدید:
    - او را در لیست اعضای عضو شده ثبت می‌کند
    - پیام خوش‌آمدگویی برایش ارسال می‌کند
    
    Args:
        message: پیام دریافتی از تلگرام شامل اطلاعات اعضای جدید
    """
    # بررسی وجود عضو جدید در پیام
    if 'new_chat_members' in message:
        chat_id = message['chat']['id']
        # پردازش هر عضو جدید
        for new_member in message['new_chat_members']:
            add_known_member(new_member, chat_id)
            welcome_new_member(chat_id, new_member)

def main():
    """تابع اصلی اجرای ربات
    
    این تابع حلقه اصلی ربات را اجرا می‌کند که شامل:
    - دریافت به‌روزرسانی‌ها از تلگرام
    - پردازش پیام‌ها و دستورات
    - مدیریت خطاها و وقفه‌ها
    """
    logging.info("Bot from {} started1.. ".format(log1))
    #print(sys.executable)
    #logging.info("Python executable path: %s", sys.executable)

    offset = None  # شناسه آخرین به‌روزرسانی پردازش شده
    
    while True:
        try:
            # دریافت به‌روزرسانی‌های جدید
            updates = get_updates(offset)
            if updates and updates.get('ok'):
                for update in updates.get('result', []):
                    if 'message' in update:
                        message = update['message']    
                        chat_id = message['chat']['id']    
                        text = message.get('text', '') 
                        # 💖 قلب محمد: لاگ شخصی
                        print(f'from :{sys1} ...recieved message from {chat_id} with: {text}')
                        logging.debug(f"Processing message: {update['message']}")
                        process_message(update['message'])
                        process_new_chat_member(update['message'])
                        handle_recitation_exercise(update['message'])
                        handle_admin_score(update['message'])
                    elif 'callback_query' in update:
                        callback = update['callback_query']    
                        message = callback['message']
                        
                        #message = update['message']    
                        chat_id = message['chat']['id']    
                        text = message.get('text', '') 
                        # 💖 قلب محمد: لاگ شخصی
                        print(f'from :{sys1} ...recieved message from {chat_id} with: {text}')
                        logging.info(f"Received callback_query: {update['callback_query']['data']}")
                        handle_callback_query(update['callback_query'])
                    # به‌روزرسانی شناسه آخرین پیام پردازش شده
                    offset = update['update_id'] + 1
            time.sleep(0.5)  # تاخیر برای جلوگیری از فشار به سرور
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            break
        except Exception as e:
            logging.error(f"General error: {str(e)} - Traceback: {str(type(e).__name__)}")
            delay = min(delay + 2, 10)  # با هر خطا، تأخیر زیاد بشه تا 10 ثانیه
            #time.sleep(delay)
            time.sleep(10)  # تاخیر بیشتر در صورت بروز خطا

if __name__ == "__main__":
    main()