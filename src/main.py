# ربات مدیریت تمرین‌های تلاوت قرآن
# نسخه ۳.۰
# توسعه‌دهنده: محمد زارع‌پور
#   مرداد4 شنبه  ساعت 8:31 شروع 
#  7/26/25


# # در گیت سیستم1 بعد  پاینوت مین11  دیگه اینجا ورژن میزنم. و شروع شد. 
#  در گیت sys بعد main11  

# کتابخانه‌های مورد نیاز
import jdatetime  # برای کار با تاریخ شمسی
import requests  # برای ارتباط با API بله
import json      # برای کار با داده‌های JSON
import time     # برای کار با زمان
import re       # برای کار با عبارات منظم
import logging  # برای ثبت گزارش‌ها
import os  # برای بررسی وجود فایل

# تنظیمات اولیه سیستم ثبت گزارش
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# متغیر اسم سیستم - قابل تغییر برای محل‌های مختلف اجرا
log1=sys1= "main git sys2 "
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
        "name": "دوره آموزش تلاوت قرآن",
        "price": "500,000 تومان",
        "schedule": "شنبه‌ها و سه‌شنبه‌ها ساعت 18:00"
    },
    "tajvid": {
        "name": "دوره تخصصی تجوید",
        "price": "700,000 تومان",
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
                row_buttons.append({"text": button["text"], "callback_data": button["callback_data"]})
            inline_keyboard_buttons.append(row_buttons)
        return {"inline_keyboard": inline_keyboard_buttons}
    else:
        keyboard_buttons = []
        for row in buttons:
            row_buttons = []
            for button in row:
                row_buttons.append({"text": button["text"]})
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
        "text": text,            # متن پیام
        "parse_mode": "Markdown"  # پشتیبانی از قالب‌بندی مارک‌داون
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)  # افزودن دکمه‌ها در صورت وجود
    
    try:
        # ارسال درخواست POST به API با مهلت ۱۰ ثانیه
        response = requests.post(url, json=data, timeout=10)
        if response.ok:
            return response.json()  # برگرداندن پاسخ در صورت موفقیت
        else:
            logging.error(f"خطا در ارسال پیام: {response.status_code}")
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
        response = requests.post(url, json=data, timeout=10)
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

def start_registration(chat_id, user_id):
    """شروع فرآیند ثبت‌نام جدید."""
    # Check if the user is already in the 'waiting_name_lastname' step
    if user_id in private_signup_states and private_signup_states[user_id].get('step') == 'waiting_name_lastname':
        return # Already prompted, do nothing

    private_signup_states[user_id] = {'step': 'waiting_name_lastname'}
    send_message(chat_id, "نام و نام خانوادگی  مثال: محمدی علی).")

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
        
        # ذخیره اطلاعات کاربر
        registered_users[user_id] = {
            'first_name': private_signup_states[user_id]['first_name'],
            'last_name': private_signup_states[user_id]['last_name'],
            'mobile': private_signup_states[user_id]['mobile'],
            'national_id': private_signup_states[user_id].get('national_id'),
            'registered_class': selected_class_id
        }
        save_users_to_file()

        send_message(chat_id, f"تبریک می‌گوییم! ثبت‌نام شما در کلاس *{class_name}* با موفقیت انجام شد.\nلینک ورود به کلاس به زودی برای شما ارسال خواهد شد.\n\nاز همراهی شما سپاسگزاریم!\n\nلینک کانال آموزشی: [لینک کانال](https://t.me/your_educational_channel)")
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
            keyboard = create_keyboard([
                      [{'text': 'همراه با ربات تلاوت', 'callback_data': 'start_bot_features'}],

                ])
          
            send_message(chat_id, f"{sys1} \n\nبه ربات تلاوت خوش آمدید!\nبرای مشاهده قابلیت‌های ربات، روی دکمه زیر کلیک کنید:", reply_markup=keyboard)
           # send_message(chat_id,     f"{سیستم1}\n\n"    "به ربات\n"    "تلاوت خوش آمدید!\n"    "برای مشاهده قابلیت‌های ربات، روی دکمه زیر کلیک کنید:",     reply_markup=keyboard)
            state['step'] = 'waiting_for_bot_features_command'
            return          

        if state.get('step') == 'waiting_name_lastname' and 'text' in message:
            parts = message['text'].strip().split()
            if len(parts) >= 2:
                state['first_name'] = parts[0]
                state['last_name'] = ' '.join(parts[1:])
                send_message(chat_id, "لطفاً شماره موبایل خود را وارد کنید:")
                state['step'] = 'waiting_mobile'
            else:
                send_message(chat_id, "لطفا نام و نام خانوادگی خود را به درستی وارد کنید (مثال: محمدی علی).")
            return

        if state.get('step') == 'waiting_mobile' and 'text' in message:
            mobile_number = message['text'].strip()
            if re.fullmatch(r'09\d{9}', mobile_number):
                state['mobile'] = mobile_number
                send_message(chat_id, "لطفاً کد ملی خود را وارد کنید:")
                state['step'] = 'waiting_national_id'
            else:
                send_message(chat_id, "شماره موبایل نامعتبر است. لطفا یک شماره 11 رقمی صحیح وارد کنید (مثال: 09123456789).")
            return

        if state.get('step') == 'waiting_national_id' and 'text' in message:
            national_id = message['text'].strip()
            if re.fullmatch(r'\d{10}', national_id):
                state['national_id'] = national_id
                user_data = private_signup_states[user_id]
                message_text = f"اطلاعات شما:\nنام: {user_data['first_name']}\nنام خانوادگی: {user_data['last_name']}\nموبایل: {user_data['mobile']}\nکد ملی: {user_data['national_id']}\n\nآیا اطلاعات فوق صحیح است؟"
                keyboard = create_keyboard([[{'text': 'تایید و ادامه', 'callback_data': 'confirm_info'}], [{'text': 'ویرایش اطلاعات', 'callback_data': 'edit_info'}]])
                send_message(chat_id, message_text, reply_markup=keyboard)
                state['step'] = 'waiting_for_info_confirmation'
            else:
                send_message(chat_id, "کد ملی نامعتبر است. لطفا یک کد ملی 10 رقمی صحیح وارد کنید.")
            return


        # اگر کاربر در انتظار ارسال شماره موبایل است
        if state.get('step') == 'waiting_mobile_contact' and 'contact' in message:
            mobile = message['contact'].get('phone_number', '')
            state['mobile'] = mobile
            send_message(chat_id, f"نام: {state['first_name']}\nنام خانوادگی: {state['last_name']}\nموبایل: {mobile}\n\nاطلاعات شما ثبت شد. برای ادامه، لطفا از دکمه‌های مربوطه استفاده کنید.")
            state['step'] = 'registration_completed'
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
    logging.info("Bot1 started1..{} ".format(log1))
    offset = None  # شناسه آخرین به‌روزرسانی پردازش شده
    
    while True:
        try:
            # دریافت به‌روزرسانی‌های جدید
            updates = get_updates(offset)
            if updates and updates.get('ok'):
                for update in updates.get('result', []):
                    if 'message' in update:
                        logging.debug(f"Processing message: {update['message']}")
                        process_message(update['message'])
                        process_new_chat_member(update['message'])
                        handle_recitation_exercise(update['message'])
                        handle_admin_score(update['message'])
                    elif 'callback_query' in update:
                        logging.info(f"Received callback_query: {update['callback_query']['data']}")
                        handle_callback_query(update['callback_query'])
                    # به‌روزرسانی شناسه آخرین پیام پردازش شده
                    offset = update['update_id'] + 1
            time.sleep(1)  # تاخیر برای جلوگیری از فشار به سرور
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            break
        except Exception as e:
            logging.error(f"General error: {str(e)} - Traceback: {str(type(e).__name__)}")
            time.sleep(5)  # تاخیر بیشتر در صورت بروز خطا

if __name__ == "__main__":
    main()
