import requests
import time
import json

from main import sys1

# تنظیمات ربات
log1=sys1="appwrite mzporsony "

#BOT_TOKEN = '1423205711:aNMfw7aEfrMwHNITw4S7bTs9NP92MRzcDLg19Hjo'# یار ثبت نام 
BOT_TOKEN = '811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1'  #یار مربی
#BOT_TOKEN = '1714651531:y2xOK6EBg5nzVV6fEWGqtOdc3nVqVgOuf4PZVQ7S'#یار مدیر

API_URL = f'https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates'
SEND_URL = f'https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage'
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"  # آدرس پایه API بله
# تنظیمات کلاس‌ها
CLASSES = {
    '1': {
        'name': 'کلاس مربی اول - استاد احمدی',
        'price': '500,000 تومان',
        'schedule': 'شنبه و دوشنبه ساعت 8 تا 9'
    },
    '2': {
        'name': 'کلاس مربی دوم - استاد رضایی', 
        'price': '450,000 تومان',
        'schedule': 'یکشنبه و چهارشنبه ساعت 9 تا 10'
    }
}

# لینک‌های پرداخت (باید با درگاه پرداخت واقعی جایگزین شود)
PAYMENT_LINKS = {
    '1': 'https://pay.example.com/class1',
    '2': 'https://pay.example.com/class2'
}

# لینک کانال آموزشی
EDUCATION_CHANNEL = 'https://t.me/tavalaht_school'

# ذخیره وضعیت کاربران
user_states = {}
user_data = {}

last_update_id = 0

def send_message(chat_id, text, reply_markup=None):
    """ارسال پیام به کاربر"""
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
    
    response = requests.post(SEND_URL, json=payload)
    return response.json()

def create_keyboard(buttons):
    """ساخت کیبورد شیشه‌ای"""
    keyboard = {
        'inline_keyboard': []
    }
    
    for button_row in buttons:
        row = []
        for button in button_row:
            row.append({
                'text': button['text'],
                'callback_data': button['data']
            })
        keyboard['inline_keyboard'].append(row)
    
    return keyboard

def handle_start(chat_id):
    """مدیریت دستور /start"""
    welcome_text = f"""{sys1}\n\n
🌟 به مدرسه تلاوت قرآن کریم ارم1 خوش آمدید! 🌟

📿 در اینجا شما می‌توانید در کلاس‌های تلاوت قرآن ثبت نام کنید
📚 آموزش‌های تخصصی با اساتید مجرب
🎯 رویکرد عملی و کاربردی

برای شروع ثبت نام، روی دکمه زیر کلیک کنید:
    """
    
    keyboard = create_keyboard([[
        {'text': '🚀 شروع ثبت نام', 'data': 'start_registration'}
    ]])
    
    send_message(chat_id, welcome_text, keyboard)

def start_registration(chat_id):
    """شروع فرآیند ثبت نام"""
    user_states[chat_id] = 'waiting_name'
    user_data[chat_id] = {}
    
    text = "📝 لطفاً نام و نام خانوادگی خود را وارد کنید:"
    send_message(chat_id, text)

def handle_name_input(chat_id, name):
    """مدیریت ورودی نام"""
    user_data[chat_id]['name'] = name
    user_states[chat_id] = 'waiting_phone'
    
    text = "📱 لطفاً شماره تلفن خود را وارد کنید:\n(مثال: 09123456789)"
    send_message(chat_id, text)

def handle_phone_input(chat_id, phone):
    """مدیریت ورودی شماره تلفن"""
    user_data[chat_id]['phone'] = phone
    user_states[chat_id] = 'waiting_national_id'
    
    text = "🆔 لطفاً شماره ملی خود را وارد کنید:\n(10 رقم)"
    send_message(chat_id, text)

def handle_national_id_input(chat_id, national_id):
    """مدیریت ورودی شماره ملی"""
    user_data[chat_id]['national_id'] = national_id
    user_states[chat_id] = 'confirm_info'
    
    # نمایش اطلاعات برای تأیید
    user_info = user_data[chat_id]
    text = f"""
✅ لطفاً اطلاعات وارد شده را بررسی کنید:

👤 نام و نام خانوادگی: {user_info['name']}
📱 شماره تلفن: {user_info['phone']}
🆔 شماره ملی: {user_info['national_id']}

آیا اطلاعات صحیح است؟
    """
    
    keyboard = create_keyboard([
        [{'text': '✅ بله، صحیح است', 'data': 'confirm_info'}],
        [{'text': '❌ ویرایش اطلاعات', 'data': 'edit_info'}],
        [{'text': '❌ ویرایش 2اطلاعات', 'data': 'edit_info2'}]
    ])
    
    send_message(chat_id, text, keyboard)

def show_classes(chat_id):
    """نمایش کلاس‌های موجود"""
    user_states[chat_id] = 'selecting_class'
    
    text = """
📚 کلاس‌های موجود برای ثبت نام:

لطفاً یکی از کلاس‌های زیر را انتخاب کنید:
    """
    
    buttons = []
    for class_id, class_info in CLASSES.items():
        button_text = f"{class_info['name']}\n💰 {class_info['price']}\n🕐 {class_info['schedule']}"
        buttons.append([{'text': button_text, 'data': f'select_class_{class_id}'}])
    
    keyboard = create_keyboard(buttons)
    send_message(chat_id, text, keyboard)

def handle_class_selection(chat_id, class_id):
    """مدیریت انتخاب کلاس"""
    user_data[chat_id]['selected_class'] = class_id
    class_info = CLASSES[class_id]
    
    text = f"""
✅ شما کلاس زیر را انتخاب کردید:

📚 {class_info['name']}
💰 هزینه: {class_info['price']}
🕐 زمان برگزاری: {class_info['schedule']}

برای تکمیل ثبت نام، لطفاً هزینه کلاس را پرداخت کنید:
    """
    
    keyboard = create_keyboard([[
        {'text': '💳 پرداخت آنلاین', 'data': f'payment_{class_id}'}
    ]])
    
    send_message(chat_id, text, keyboard)

def show_payment_link(chat_id, class_id):
    """نمایش لینک پرداخت"""
    payment_link = PAYMENT_LINKS[class_id]
    class_info = CLASSES[class_id]
    
    text = f"""
💳 پرداخت آنلاین

📚 کلاس: {class_info['name']}
💰 مبلغ قابل پرداخت: {class_info['price']}

🔗 لینک پرداخت: {payment_link}

⚠️ پس از پرداخت موفق، روی دکمه "پرداخت انجام شد" کلیک کنید.
    """
    
    keyboard = create_keyboard([[
        {'text': '✅ پرداخت انجام شد', 'data': 'payment_completed'}
    ]])
    
    send_message(chat_id, text, keyboard)

def handle_payment_completion(chat_id):
    """مدیریت تکمیل پرداخت"""
    user_info = user_data[chat_id]
    class_info = CLASSES[user_info['selected_class']]
    
    # در اینجا باید پرداخت را تایید کنید (با API درگاه پرداخت)
    # برای نمونه، فرض می‌کنیم پرداخت موفق بوده
    
    success_text = f"""
🎉 تبریک! ثبت نام شما با موفقیت تکمیل شد!

👤 نام: {user_info['name']}
📚 کلاس انتخابی: {class_info['name']}
✅ وضعیت پرداخت: تکمیل شده

🔗 لینک کانال آموزشی: {EDUCATION_CHANNEL}

📌 لطفاً در کانال عضو شوید تا از جدیدترین اطلاعات و برنامه‌های کلاسی مطلع شوید.

موفق باشید! 🌟
    """
    
    send_message(chat_id, success_text)
    
    # پاک کردن داده‌های کاربر
    if chat_id in user_states:
        del user_states[chat_id]
    if chat_id in user_data:
        del user_data[chat_id]
#####################################################################
def handle_callback_query(chat_id, callback_data):
    """مدیریت دکمه‌های شیشه‌ای"""
    if callback_data == 'start_registration':
        start_registration(chat_id)
    elif callback_data == 'confirm_info':
        show_classes(chat_id)
   # elif callback_data == 'edit_info2':
   #     start_registration(chat_id)
    elif callback_data == 'edit_info':
        start_registration(chat_id)
    elif callback_data.startswith('select_class_'):
        class_id = callback_data.split('_')[-1]
        handle_class_selection(chat_id, class_id)
    elif callback_data.startswith('payment_'):
        class_id = callback_data.split('_')[-1]
        show_payment_link(chat_id, class_id)
    elif callback_data == 'payment_completed':
        handle_payment_completion(chat_id)
#####################################################################
def handle_message(chat_id, text):
    """مدیریت پیام‌های متنی"""
    current_state = user_states.get(chat_id, 'none')
    
    if text == '/start':
        handle_start(chat_id)
    elif current_state == 'waiting_name':
        handle_name_input(chat_id, text)
    elif current_state == 'waiting_phone':
        if len(text) == 11 and text.startswith('09'):
            handle_phone_input(chat_id, text)
        else:
            send_message(chat_id, "❌ شماره تلفن نامعتبر است. لطفاً دوباره وارد کنید:")
    elif current_state == 'waiting_national_id':
        if len(text) == 10 and text.isdigit():
            handle_national_id_input(chat_id, text)
        else:
            send_message(chat_id, "❌ شماره ملی باید 10 رقم باشد. لطفاً دوباره وارد کنید:")
    else:
        send_message(chat_id, "لطفاً از منوها و دکمه‌ها استفاده کنید یا /start را ارسال کنید.")

# حلقه اصلی ربات
while True:
    try:
        params = {'offset': last_update_id + 1, 'timeout': 30}
        response = requests.get(API_URL, params=params).json()
        
        if 'result' in response:
            for update in response['result']:
                last_update_id = update['update_id']
                
                # مدیریت پیام‌های متنی
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    text = update['message'].get('text', '')                   
                    print(f'{log1} ...recieved message from {chat_id} with: {text}')
                    handle_message(chat_id, text)
                
                # مدیریت دکمه‌های شیشه‌ای
                elif 'callback_query' in update:
                    chat_id = update['callback_query']['message']['chat']['id']
                    callback_data = update['callback_query']['data']
                    print(f'دریافت callback: {callback_data} از چت {chat_id}')
                    handle_callback_query(chat_id, callback_data)
        
        time.sleep(1)
        
    except Exception as e:
        print(f'خطا: {e}')
        time.sleep(5)