 # مدیریت چت خصوصی و سرویس‌های ویژه
# بخش ثبت‌نام، مدیریت حساب کاربری و سرویس‌های VIP

import jdatetime
import requests
import json
import time
import re
import logging
from quran_bot_main import *

def show_main_menu(chat_id, user_id):
    """نمایش منوی اصلی با سرویس‌های ویژه"""
    if user_id in registered_users:
        # کاربر ثبت‌نام شده - منوی کامل
        inline_buttons = [
            [{'text': '📚 ثبت نام در کلاس‌های قرآن', 'callback_data': 'quran_registration'}],
            [{'text': '👤 حساب کاربری', 'callback_data': 'user_account'}],
            [{'text': '⭐ سرویس‌های ویژه', 'callback_data': 'vip_services'}],
            [{'text': '🏆 مسابقات قرآنی', 'callback_data': 'quran_competitions'}]
        ]
        inline_keyboard = create_keyboard(inline_buttons, is_inline=True)
        
        bottom_buttons = [
            [{'text': '📊 نظر سنجی', 'callback_data': 'survey'}],
            [{'text': 'ℹ️ درباره ربات', 'callback_data': 'about_bot'}],
            [{'text': '📞 پشتیبانی', 'callback_data': 'support'}]
        ]
        bottom_keyboard = create_keyboard(bottom_buttons, is_inline=False)
        
        combined_keyboard = {
            "inline_keyboard": inline_keyboard.get("inline_keyboard", []),
            "keyboard": bottom_keyboard.get("keyboard", []),
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        
        send_message(chat_id, f"{log1} \n\nبه ربات قرآن خوش آمدید! 🌟\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=combined_keyboard)
    else:
        # کاربر جدید - منوی معرفی
        inline_buttons = [
            [{'text': '🏫 معرفی مرکز قرآن', 'callback_data': 'quran_center_intro'}],
            [{'text': '📚 ثبت نام در کلاس‌های قرآن', 'callback_data': 'quran_registration'}],
            [{'text': '⭐ سرویس‌های ویژه', 'callback_data': 'vip_services'}]
        ]
        inline_keyboard = create_keyboard(inline_buttons, is_inline=True)
        
        bottom_buttons = [
            [{'text': '📊 نظر سنجی', 'callback_data': 'survey'}],
            [{'text': 'ℹ️ درباره ربات', 'callback_data': 'about_bot'}],
            [{'text': '📞 پشتیبانی', 'callback_data': 'support'}]
        ]
        bottom_keyboard = create_keyboard(bottom_buttons, is_inline=False)
        
        combined_keyboard = {
            "inline_keyboard": inline_keyboard.get("inline_keyboard", []),
            "keyboard": bottom_keyboard.get("keyboard", []),
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        
        send_message(chat_id, f"{log1} \n\nبه ربات قرآن خوش آمدید! 🌟\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=combined_keyboard)

def handle_quran_center_intro(chat_id, user_id):
    """معرفی مرکز قرآن"""
    intro_text = "🏫 معرفی مرکز تخصصی قرآن کریم\n\n"
    intro_text += "🌟 مرکز تخصصی قرآن کریم، مرکزی پیشرفته برای آموزش قرآن است.\n\n"
    intro_text += "📚 خدمات ما:\n"
    intro_text += "• آموزش تجوید و تلاوت قرآن\n"
    intro_text += "• کلاس‌های حضوری و آنلاین\n"
    intro_text += "• دوره‌های حفظ قرآن\n"
    intro_text += "• علوم قرآنی و تفسیر\n"
    intro_text += "• مسابقات قرآنی\n"
    intro_text += "• گواهی پایان دوره معتبر\n\n"
    intro_text += "🎯 اهداف آموزشی:\n"
    intro_text += "• یادگیری اصول صحیح تلاوت\n"
    intro_text += "• تقویت صوت و لحن\n"
    intro_text += "• آشنایی با قواعد تجوید\n"
    intro_text += "• حفظ قرآن کریم\n"
    intro_text += "• آمادگی برای مسابقات قرآنی\n\n"
    intro_text += "⭐ سرویس‌های ویژه:\n"
    intro_text += "• مربی خصوصی\n"
    intro_text += "• کتابخانه آنلاین\n"
    intro_text += "• مشاوره تحصیلی\n"
    intro_text += "• کارگاه‌های تخصصی\n\n"
    intro_text += "📞 برای اطلاعات بیشتر و ثبت نام، با ما در تماس باشید."
    
    bottom_buttons = [
        [{'text': '📚 ثبت نام در کلاس‌ها', 'callback_data': 'quran_registration'}],
        [{'text': '⭐ سرویس‌های ویژه', 'callback_data': 'vip_services'}],
        [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
    ]
    bottom_keyboard = create_keyboard(bottom_buttons, is_inline=False)
    
    send_message(chat_id, intro_text, reply_markup=bottom_keyboard)

def handle_vip_services(chat_id, user_id):
    """مدیریت سرویس‌های ویژه"""
    if user_id in registered_users:
        # کاربر ثبت‌نام شده - سرویس‌های کامل
        services_text = "⭐ سرویس‌های ویژه برای اعضا\n\n"
        services_text += "به عنوان عضو ثبت‌نام شده، می‌توانید از سرویس‌های زیر استفاده کنید:\n\n"
        
        for service_id, service_info in VIP_SERVICES.items():
            services_text += f"🌟 {service_info['name']}\n"
            services_text += f"📝 {service_info['description']}\n"
            services_text += f"💰 {service_info['price']}\n\n"
        
        keyboard_buttons = []
        for service_id, service_info in VIP_SERVICES.items():
            keyboard_buttons.append([{'text': f"⭐ {service_info['name']}", 'callback_data': f'vip_service_{service_id}'}])
        
        keyboard_buttons.append([{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}])
        keyboard = create_keyboard(keyboard_buttons)
        
        send_message(chat_id, services_text, reply_markup=keyboard)
    else:
        # کاربر جدید - معرفی سرویس‌ها
        services_text = "⭐ سرویس‌های ویژه مرکز قرآن\n\n"
        services_text += "پس از ثبت‌نام، می‌توانید از سرویس‌های ویژه زیر استفاده کنید:\n\n"
        
        for service_id, service_info in list(VIP_SERVICES.items())[:3]:  # فقط 3 سرویس اول
            services_text += f"🌟 {service_info['name']}\n"
            services_text += f"📝 {service_info['description']}\n"
            services_text += f"💰 {service_info['price']}\n\n"
        
        services_text += "برای دسترسی به تمام سرویس‌ها، ابتدا ثبت‌نام کنید."
        
        keyboard = create_keyboard([
            [{'text': '📚 ثبت نام در کلاس‌ها', 'callback_data': 'quran_registration'}],
            [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
        ])
        
        send_message(chat_id, services_text, reply_markup=keyboard)

def handle_quran_competitions(chat_id, user_id):
    """مدیریت مسابقات قرآنی"""
    competitions_text = "🏆 مسابقات قرآنی\n\n"
    competitions_text += "شرکت در مسابقات قرآنی بهترین راه برای ارتقای مهارت‌های قرآنی است.\n\n"
    competitions_text += "📅 مسابقات جاری:\n"
    competitions_text += "• مسابقه تلاوت قرآن - سطح مبتدی\n"
    competitions_text += "• مسابقه حفظ قرآن - سطح متوسط\n"
    competitions_text += "• مسابقه تجوید - سطح پیشرفته\n\n"
    competitions_text += "🏅 جوایز:\n"
    competitions_text += "• گواهی معتبر\n"
    competitions_text += "• هدایای نقدی\n"
    competitions_text += "• بورسیه تحصیلی\n\n"
    
    if user_id in registered_users:
        competitions_text += "✅ شما ثبت‌نام شده‌اید و می‌توانید در مسابقات شرکت کنید."
        keyboard = create_keyboard([
            [{'text': '🏆 ثبت نام در مسابقه', 'callback_data': 'register_competition'}],
            [{'text': '📋 قوانین مسابقات', 'callback_data': 'competition_rules'}],
            [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
        ])
    else:
        competitions_text += "⚠️ برای شرکت در مسابقات، ابتدا ثبت‌نام کنید."
        keyboard = create_keyboard([
            [{'text': '📚 ثبت نام در کلاس‌ها', 'callback_data': 'quran_registration'}],
            [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
        ])
    
    send_message(chat_id, competitions_text, reply_markup=keyboard)

def start_registration(chat_id, user_id):
    """شروع فرآیند ثبت‌نام"""
    if user_id in private_signup_states and private_signup_states[user_id].get('step') == 'waiting_name_lastname':
        return

    private_signup_states[user_id] = {'step': 'waiting_name_lastname'}
    send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: محمدی علی):")

def handle_user_account(chat_id, user_id):
    """مدیریت حساب کاربری"""
    if user_id in registered_users:
        user_data = registered_users[user_id]
        account_info = f"👤 اطلاعات حساب کاربری\n\n"
        account_info += f"👤 نام: {user_data.get('first_name', '')}\n"
        account_info += f"👤 نام خانوادگی: {user_data.get('last_name', '')}\n"
        account_info += f"📱 موبایل: {user_data.get('mobile', '')}\n"
        account_info += f"🆔 کد ملی: {user_data.get('national_id', '')}\n"
        account_info += f"📚 کلاس ثبت شده: {QURAN_CLASSES.get(user_data.get('registered_class', ''), {}).get('name', 'ثبت نشده')}\n"
        account_info += f"⭐ وضعیت VIP: فعال\n"
        account_info += f"📅 تاریخ عضویت: {user_data.get('join_date', 'نامشخص')}"
        
        keyboard = create_keyboard([
            [{'text': '📚 کلاس جدید', 'callback_data': 'new_class_registration'}],
            [{'text': '⭐ سرویس‌های ویژه', 'callback_data': 'vip_services'}],
            [{'text': '✏️ تصحیح اطلاعات', 'callback_data': 'edit_user_info'}],
            [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
        ])
        send_message(chat_id, account_info, reply_markup=keyboard)
    else:
        keyboard = create_keyboard([
            [{'text': '📚 ثبت نام در کلاس‌ها', 'callback_data': 'quran_registration'}],
            [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
        ])
        send_message(chat_id, "شما هنوز ثبت نام نکرده‌اید. لطفاً ابتدا ثبت نام کنید.", reply_markup=keyboard)

def show_classes(chat_id, user_id):
    """نمایش لیست کلاس‌های قرآن"""
    classes_text = "📚 کلاس‌های قرآن کریم\n\n"
    classes_text += "لطفاً کلاس مورد نظر خود را انتخاب کنید:\n\n"
    
    keyboard_buttons = []
    for class_id, class_info in QURAN_CLASSES.items():
        classes_text += f"📚 {class_info['name']}\n"
        classes_text += f"💰 {class_info['price']}\n"
        classes_text += f"⏰ {class_info['schedule']}\n"
        classes_text += f"📅 مدت: {class_info['duration']}\n"
        classes_text += f"📊 سطح: {class_info['level']}\n\n"
        
        keyboard_buttons.append([{'text': class_info['name'], 'callback_data': f'select_class_{class_id}'}])
    
    keyboard = create_keyboard(keyboard_buttons)
    send_message(chat_id, classes_text, reply_markup=keyboard)
    private_signup_states[user_id]['step'] = 'waiting_for_class_selection'

def handle_class_selection(chat_id, user_id, class_id):
    """مدیریت انتخاب کلاس"""
    if class_id in QURAN_CLASSES:
        private_signup_states[user_id]['selected_class'] = class_id
        class_info = QURAN_CLASSES[class_id]
        message_text = f"شما کلاس *{class_info['name']}* را انتخاب کردید.\n\n"
        message_text += f"💰 هزینه: {class_info['price']}\n"
        message_text += f"⏰ برنامه: {class_info['schedule']}\n"
        message_text += f"📅 مدت: {class_info['duration']}\n"
        message_text += f"📊 سطح: {class_info['level']}\n\n"
        message_text += "برای ادامه، لطفا پرداخت را انجام دهید."
        
        keyboard = create_keyboard([[{'text': '💳 پرداخت', 'callback_data': f'show_payment_{class_id}'}]])
        send_message(chat_id, message_text, reply_markup=keyboard)
        private_signup_states[user_id]['step'] = 'waiting_for_payment_link_request'
    else:
        send_message(chat_id, "کلاس انتخابی نامعتبر است. لطفا دوباره تلاش کنید.")

def show_payment_link(chat_id, user_id, class_id):
    """نمایش لینک پرداخت"""
    payment_link = PAYMENT_LINKS.get(class_id)
    if payment_link:
        message_text = f"لطفا برای نهایی کردن ثبت‌نام، از طریق لینک زیر پرداخت را انجام دهید:\n\n"
        message_text += f"🔗 {payment_link}\n\n"
        message_text += "پس از پرداخت، روی دکمه 'پرداخت کردم' کلیک کنید."
        
        keyboard = create_keyboard([[{'text': '✅ پرداخت کردم', 'callback_data': 'payment_completed'}]])
        send_message(chat_id, message_text, reply_markup=keyboard)
        private_signup_states[user_id]['step'] = 'waiting_for_payment_confirmation'
    else:
        send_message(chat_id, "لینک پرداخت برای این کلاس موجود نیست.")

def handle_payment_completion(chat_id, user_id):
    """مدیریت تایید پرداخت"""
    if user_id in private_signup_states and 'selected_class' in private_signup_states[user_id]:
        selected_class_id = private_signup_states[user_id]['selected_class']
        class_name = QURAN_CLASSES[selected_class_id]['name']
        
        is_editing = private_signup_states[user_id].get('is_editing', False)
        
        registered_users[user_id] = {
            'first_name': private_signup_states[user_id]['first_name'],
            'last_name': private_signup_states[user_id]['last_name'],
            'mobile': private_signup_states[user_id]['mobile'],
            'national_id': private_signup_states[user_id].get('national_id'),
            'registered_class': selected_class_id,
            'join_date': get_jalali_date(),
            'vip_status': True
        }
        save_users_to_file()

        if is_editing:
            success_message = f"اطلاعات شما با موفقیت به‌روزرسانی شد.\nکلاس: *{class_name}*"
        else:
            success_message = f"🎉 تبریک می‌گوییم!\n\n"
            success_message += f"ثبت‌نام شما در کلاس *{class_name}* با موفقیت انجام شد.\n\n"
            success_message += "⭐ سرویس‌های ویژه شما فعال شد:\n"
            success_message += "• دسترسی به کتابخانه آنلاین\n"
            success_message += "• شرکت در مسابقات قرآنی\n"
            success_message += "• مشاوره تحصیلی رایگان\n"
            success_message += "• کارگاه‌های تخصصی\n\n"
            success_message += "📞 لینک ورود به کلاس به زودی برای شما ارسال خواهد شد.\n\n"
            success_message += "از همراهی شما سپاسگزاریم! 🙏"
        
        keyboard = create_keyboard([
            [{'text': '👤 حساب کاربری', 'callback_data': 'user_account'}],
            [{'text': '⭐ سرویس‌های ویژه', 'callback_data': 'vip_services'}],
            [{'text': '📚 کلاس جدید', 'callback_data': 'new_class_registration'}],
            [{'text': '🏆 مسابقات قرآنی', 'callback_data': 'quran_competitions'}]
        ])
        send_message(chat_id, success_message, reply_markup=keyboard)
        private_signup_states[user_id]['step'] = 'registered'
    else:
        send_message(chat_id, "خطا در تکمیل فرآیند پرداخت. لطفا دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.")

def handle_survey(chat_id, user_id):
    """مدیریت نظر سنجی"""
    survey_text = "📊 نظر سنجی ربات قرآن\n\n"
    survey_text += "لطفاً نظر خود را درباره ربات و خدمات ما بگویید:\n\n"
    survey_text += "• کیفیت خدمات آموزشی\n"
    survey_text += "• سهولت استفاده از ربات\n"
    survey_text += "• سرویس‌های ویژه\n"
    survey_text += "• پیشنهادات بهبود"
    
    inline_buttons = [
        [{'text': '⭐ عالی', 'callback_data': 'survey_excellent'}],
        [{'text': '👍 خوب', 'callback_data': 'survey_good'}],
        [{'text': '📊 متوسط', 'callback_data': 'survey_average'}],
        [{'text': '👎 نیاز به بهبود', 'callback_data': 'survey_needs_improvement'}]
    ]
    inline_keyboard = create_keyboard(inline_buttons, is_inline=True)
    
    bottom_buttons = [
        [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
    ]
    bottom_keyboard = create_keyboard(bottom_buttons, is_inline=False)
    
    combined_keyboard = {
        "inline_keyboard": inline_keyboard.get("inline_keyboard", []),
        "keyboard": bottom_keyboard.get("keyboard", []),
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    
    send_message(chat_id, survey_text, reply_markup=combined_keyboard)

def handle_about_bot(chat_id, user_id):
    """مدیریت اطلاعات ربات"""
    about_text = "ℹ️ درباره ربات قرآن\n\n"
    about_text += "🤖 این ربات برای مدیریت کلاس‌های قرآن و ارائه سرویس‌های ویژه طراحی شده است.\n\n"
    about_text += "📚 قابلیت‌ها:\n"
    about_text += "• ثبت نام در کلاس‌های قرآن\n"
    about_text += "• مدیریت تمرین‌های تلاوت\n"
    about_text += "• سرویس‌های ویژه VIP\n"
    about_text += "• مسابقات قرآنی\n"
    about_text += "• گزارش‌گیری از پیشرفت\n"
    about_text += "• مشاوره تحصیلی\n\n"
    about_text += "👨‍💻 توسعه‌دهنده: محمد زارع‌پور\n"
    about_text += "📅 نسخه: 4.0\n"
    about_text += "🌟 سیستم جامع مدیریت قرآنی"
    
    bottom_buttons = [
        [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
    ]
    bottom_keyboard = create_keyboard(bottom_buttons, is_inline=False)
    
    send_message(chat_id, about_text, reply_markup=bottom_keyboard)

def handle_support(chat_id, user_id):
    """مدیریت پشتیبانی"""
    support_text = "📞 پشتیبانی\n\n"
    support_text += "برای ارتباط با پشتیبانی:\n\n"
    support_text += "📱 تلگرام: @quran_support\n"
    support_text += "📧 ایمیل: support@qurancenter.com\n"
    support_text += "📞 تلفن: 021-12345678\n\n"
    support_text += "⏰ ساعات کاری:\n"
    support_text += "شنبه تا چهارشنبه: 8 صبح تا 6 عصر\n"
    support_text += "پنج‌شنبه: 8 صبح تا 12 ظهر"
    
    keyboard = create_keyboard([
        [{'text': '🔙 بازگشت به منو', 'callback_data': 'back_to_main_menu'}]
    ])
    
    send_message(chat_id, support_text, reply_markup=keyboard)

def handle_callback_query(message):
    """پردازش دکمه‌های شیشه‌ای"""
    user_id = message['from']['id']
    chat_id = message['message']['chat']['id'] if 'message' in message and 'chat' in message['message'] else None

    if chat_id is None:
        print("Error: chat_id not found in callback_query message.")
        return
    callback_data = message['data']

    # مدیریت منوی اصلی
    if callback_data == 'quran_center_intro':
        handle_quran_center_intro(chat_id, user_id)
    elif callback_data == 'quran_registration':
        if user_id in registered_users:
            show_classes(chat_id, user_id)
        else:
            start_registration(chat_id, user_id)
    elif callback_data == 'user_account':
        handle_user_account(chat_id, user_id)
    elif callback_data == 'vip_services':
        handle_vip_services(chat_id, user_id)
    elif callback_data == 'quran_competitions':
        handle_quran_competitions(chat_id, user_id)
    elif callback_data == 'back_to_main_menu':
        show_main_menu(chat_id, user_id)
    elif callback_data == 'new_class_registration':
        show_classes(chat_id, user_id)
    elif callback_data == 'survey':
        handle_survey(chat_id, user_id)
    elif callback_data == 'about_bot':
        handle_about_bot(chat_id, user_id)
    elif callback_data == 'support':
        handle_support(chat_id, user_id)
    
    # مدیریت انتخاب کلاس
    elif callback_data.startswith('select_class_'):
        class_id = callback_data.replace('select_class_', '')
        handle_class_selection(chat_id, user_id, class_id)
    elif callback_data.startswith('show_payment_'):
        class_id = callback_data.replace('show_payment_', '')
        show_payment_link(chat_id, user_id, class_id)
    elif callback_data == 'payment_completed':
        handle_payment_completion(chat_id, user_id)
    
    # مدیریت سرویس‌های VIP
    elif callback_data.startswith('vip_service_'):
        service_id = callback_data.replace('vip_service_', '')
        if service_id in VIP_SERVICES:
            service_info = VIP_SERVICES[service_id]
            service_text = f"⭐ {service_info['name']}\n\n"
            service_text += f"📝 {service_info['description']}\n"
            service_text += f"💰 {service_info['price']}\n\n"
            service_text += "برای استفاده از این سرویس، با پشتیبانی تماس بگیرید."
            
            keyboard = create_keyboard([
                [{'text': '📞 تماس با پشتیبانی', 'callback_data': 'support'}],
                [{'text': '🔙 بازگشت', 'callback_data': 'vip_services'}]
            ])
            send_message(chat_id, service_text, reply_markup=keyboard)
    
    # مدیریت مسابقات
    elif callback_data == 'register_competition':
        send_message(chat_id, "🏆 برای ثبت‌نام در مسابقات، با پشتیبانی تماس بگیرید.")
    elif callback_data == 'competition_rules':
        rules_text = "📋 قوانین مسابقات قرآنی\n\n"
        rules_text += "1. شرکت‌کنندگان باید عضو مرکز باشند\n"
        rules_text += "2. رعایت اصول اخلاقی و اسلامی\n"
        rules_text += "3. ارسال فایل صوتی با کیفیت مناسب\n"
        rules_text += "4. رعایت مهلت‌های تعیین شده\n"
        rules_text += "5. داوری توسط هیئت علمی مرکز\n\n"
        rules_text += "🏅 جوایز بر اساس کیفیت تلاوت اهدا می‌شود."
        
        keyboard = create_keyboard([
            [{'text': '🔙 بازگشت', 'callback_data': 'quran_competitions'}]
        ])
        send_message(chat_id, rules_text, reply_markup=keyboard)
    
    # مدیریت نظر سنجی
    elif callback_data in ['survey_excellent', 'survey_good', 'survey_average', 'survey_needs_improvement']:
        survey_responses = {
            'survey_excellent': '⭐ عالی',
            'survey_good': '👍 خوب',
            'survey_average': '📊 متوسط',
            'survey_needs_improvement': '👎 نیاز به بهبود'
        }
        response = survey_responses.get(callback_data, '')
        send_message(chat_id, f"از نظر شما متشکریم! ({response})\n\nنظر شما ثبت شد.")
        show_main_menu(chat_id, user_id)

def process_private_message(message):
    """پردازش پیام‌های خصوصی"""
    chat_id = message['chat']['id']
    chat_type = message['chat']['type']
    user_info = message['from']
    user_id = user_info.get('id')

    if chat_type == 'private':
        if user_id not in private_signup_states:
            private_signup_states[user_id] = {'step': 'waiting_start', 'first_name': '', 'last_name': '', 'mobile': '', 'national_id': ''}
        state = private_signup_states[user_id]

        if 'text' in message and message['text'].strip() == '/start':
            if user_id in registered_users:
                user_data = registered_users[user_id]
                welcome_text = f"سلام {user_data.get('first_name', 'کاربر')} عزیز!\n\n"
                welcome_text += "به ربات قرآن خوش آمدید! 🌟\n\n"
                welcome_text += "سرویس‌های ویژه شما فعال است."
                
                keyboard = create_keyboard([
                    [{'text': '👤 حساب کاربری', 'callback_data': 'user_account'}],
                    [{'text': '⭐ سرویس‌های ویژه', 'callback_data': 'vip_services'}],
                    [{'text': '📚 کلاس جدید', 'callback_data': 'new_class_registration'}],
                    [{'text': '🏆 مسابقات قرآنی', 'callback_data': 'quran_competitions'}]
                ])
                send_message(chat_id, welcome_text, reply_markup=keyboard)
            else:
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
            if re.fullmatch(r'[0-9]{10}', national_id) and not re.search(r'[۰-۹]', national_id):
                state['national_id'] = national_id
                show_final_confirmation(chat_id, user_id, state['first_name'], state['last_name'], state['mobile'], national_id)
            else:
                send_message(chat_id, "کد ملی نامعتبر است. لطفا فقط اعداد انگلیسی استفاده کنید (10 رقم).")
            return

def show_name_confirmation(chat_id, user_id, first_name, last_name):
    """نمایش تایید نام و درخواست شماره تلفن"""
    bottom_keyboard = {
        "keyboard": [[{"text": "📱 ارسال شماره تلفن", "request_contact": True}]],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    
    full_name = f"{first_name} {last_name}".strip()
    message_text = f"نام و فامیل: {full_name}\n\nلطفاً شماره تلفن خود را ارسال کنید:"
    
    send_message(chat_id, message_text, reply_markup=bottom_keyboard)
    
    inline_buttons = [
        [{'text': '✏️ تصحیح نام', 'callback_data': 'edit_name'}]
    ]
    inline_keyboard = create_keyboard(inline_buttons, is_inline=True)
    send_message(chat_id, "", reply_markup=inline_keyboard)

def show_phone_confirmation_with_buttons(chat_id, user_id, first_name, last_name, mobile):
    """نمایش تایید شماره تلفن"""
    keyboard = create_keyboard([
        [{'text': '🆔 وارد کردن کد ملی', 'callback_data': 'enter_national_id'}],
        [{'text': '✏️ تصحیح', 'callback_data': 'edit_phone'}]
    ], is_inline=False)
    message_text = f"نام: {first_name}\nنام خانوادگی: {last_name}\nموبایل: {mobile}\n\nلطفاً کد ملی خود را وارد کنید (فقط اعداد انگلیسی):"
    send_message(chat_id, message_text, reply_markup=keyboard)

def show_final_confirmation(chat_id, user_id, first_name, last_name, mobile, national_id):
    """نمایش تایید نهایی"""
    keyboard = create_keyboard([
        [{'text': '📚 ورود به انتخاب کلاس', 'callback_data': 'select_class_final'}],
        [{'text': '✏️ تصحیح کد ملی', 'callback_data': 'edit_national_id'}]
    ])
    message_text = f"نام: {first_name}\nنام خانوادگی: {last_name}\nموبایل: {mobile}\nکد ملی: {national_id}\n\nاطلاعات شما تایید شد. حالا کلاس مورد نظر خود را انتخاب کنید:"
    send_message(chat_id, message_text, reply_markup=keyboard)