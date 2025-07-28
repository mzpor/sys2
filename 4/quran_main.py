 # قوی‌ترین ربات مدیریت قرآن و تلاوت
# فایل اصلی اجرا - هماهنگی تمام ماژول‌ها
# نسخه ۴.۰

import jdatetime
import requests
import json
import time
import re
import logging
import os
import sys

# Import all modules
from quran_bot_main import *
from quran_group_handler import *
from quran_private_handler import *
from quran_admin_handler import *

def process_message(message):
    """پردازش پیام‌های دریافتی از کاربران"""
    chat_id = message['chat']['id']
    chat_type = message['chat']['type']
    user_info = message['from']
    user_id = user_info.get('id')

    # پردازش پیام‌های خصوصی
    if chat_type == 'private':
        process_private_message(message)
        return

    # بررسی استفاده از ربات در گروه
    if chat_type not in ['group', 'supergroup']:
        send_message(chat_id, "این ربات فقط در گروه‌ها کار می‌کند!")
        return
    
    # بررسی وضعیت ادمین بودن کاربر
    is_admin_user = is_admin(user_id, chat_id)
    
    # ثبت کاربر در لیست اعضای عضو شده
    add_known_member(user_info, chat_id)
    
    # پردازش دستورات ادمین
    if process_admin_commands(message):
        return
    
    # پردازش پیام‌های متنی
    if 'text' in message:
        text = message['text'].strip().lower()
        
        # دستور شروع - فقط برای ادمین‌ها
        if (text == '/شروع') and is_admin_user:
            welcome = "🤖 ربات ارزیابی تلاوت قرآن در گروه\n\n"
            welcome += "دستورات:\n"
            welcome += "👥 /شروع - فقط با اجازه ادمین\n"
            welcome += "📋 /لیست - لیست اعضای \n"
            welcome += "🎯 /گزارش - گزارش تمرینات\n"
            welcome += "🏆 /نمرات - گزارش نمرات\n"
            welcome += "👥 /عضو  - ثبت نام عضو جدید\n"
            welcome += "👑 /ادمین - داشبورد ادمین\n\n"
            welcome += "🎵 نحوه کار:\n"
            welcome += "•با کپشن 'ارسال‌تلاوت' تمرین خود را ارسال کنید.\n"
            welcome += "•با ریپلای 'عالی'، 'خوب'، 'متوسط'، 'ضعیف' یا 'بد' ارزیابی خواهید شد.\n\n"
            welcome += f"📅 امروز: {get_week_day()} ، {get_jalali_date()}\n"
            welcome += "⏰ روزهای تمرین: شنبه، دوشنبه، چهارشنبه"
            send_message(chat_id, welcome)
        elif text == '/عضو' and not is_admin_user:
            administrators = get_chat_administrators(chat_id)
            admin_ids = {admin_info.get('user', {}).get('id') for admin_info in administrators}
            regular_members = sorted([user_info['name'] for user_id, user_info in known_members.get(chat_id, {}).items() 
                                    if user_id not in admin_ids])
            user_name = get_simple_name(user_info)
            response = f"🎉 {user_name} ورودت رو به کلاس قرآن تبریک می‌گم!\n\n"
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
        elif is_admin_user and text in ['/نمرات']:
            generate_score_report(chat_id)

def handle_callback_query(message):
    """پردازش دکمه‌های شیشه‌ای"""
    user_id = message['from']['id']
    chat_id = message['message']['chat']['id'] if 'message' in message and 'chat' in message['message'] else None
    callback_data = message['data']

    if chat_id is None:
        print("Error: chat_id not found in callback_query message.")
        return

    # پردازش دکمه‌های ادمین
    if callback_data.startswith('admin_'):
        handle_admin_callback_query(message)
        return

    # پردازش دکمه‌های خصوصی
    if chat_type == 'private':
        handle_callback_query(message)
        return

    # پردازش دکمه‌های گروه
    if callback_data == 'request_membership':
        send_message(chat_id, "درخواست عضویت شما دریافت شد. لطفا منتظر تایید ادمین باشید.")

def main():
    """تابع اصلی اجرای ربات"""
    logging.info("Quran Bot v4.0 started!")
    print(f"🚀 {log1} Quran Bot v4.0 started!")

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
                        chat_type = message['chat']['type']
                        
                        # 💖 قلب محمد: لاگ شخصی
                        print(f'from :{sys1} ...received message from {chat_id} ({chat_type}) with: {text}')
                        logging.debug(f"Processing message: {update['message']}")
                        
                        process_message(update['message'])
                        process_new_chat_member(update['message'])
                        handle_recitation_exercise(update['message'])
                        handle_admin_score(update['message'])
                        
                    elif 'callback_query' in update:
                        callback = update['callback_query']    
                        message = callback['message']
                        
                        chat_id = message['chat']['id']    
                        text = message.get('text', '') 
                        chat_type = message['chat']['type']
                        
                        # 💖 قلب محمد: لاگ شخصی
                        print(f'from :{sys1} ...received callback from {chat_id} ({chat_type}) with: {callback["data"]}')
                        logging.info(f"Received callback_query: {update['callback_query']['data']}")
                        
                        handle_callback_query(update['callback_query'])
                        
                    # به‌روزرسانی شناسه آخرین پیام پردازش شده
                    offset = update['update_id'] + 1
            time.sleep(0.5)  # تاخیر برای جلوگیری از فشار به سرور
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            print("🛑 Bot stopped by user")
            break
        except Exception as e:
            logging.error(f"General error: {str(e)} - Traceback: {str(type(e).__name__)}")
            print(f"❌ Error: {str(e)}")
            delay = min(delay + 2, 10)  # با هر خطا، تأخیر زیاد بشه تا 10 ثانیه
            time.sleep(10)  # تاخیر بیشتر در صورت بروز خطا

if __name__ == "__main__":
    main()