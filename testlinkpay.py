#from balebot.filters import DefaultFilter, TemplateResponseFilter
#from balebot.models.messages import TextMessage, TemplateMessage, TemplateMessageButton
#from balebot.updater import Updater
#from balebot.handlers import MessageHandler
#import asyncio
import requests
import time
import json
import sys
import logging
import os
import re






# توکن ربات (برای تست یا واقعی)
BOT_TOKEN = "811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1"  # توکن واقعی را از @BotFather جای‌گذاری کنیدپ


updater = Updater(token=BOT_TOKEN)

# شماره تلفن مقصد برای انتقال پول
DESTINATION_PHONE = "09XXXXXXXXXX"  # شماره تلفن مقصد را وارد کنید

# لینک گروه برای ارسال به کاربر
GROUP_LINK = "https://ble.ir/join/XXXXXX"  # لینک گروه را جای‌گذاری کنید

# ایجاد Dispatcher برای مدیریت پیام‌ها
dispatcher = updater.dispatcher

# پیام خوش‌آمدگویی و ارسال لینک پرداخت
def start_conversation(update, bot):
    user_peer = update.get_effective_user()
    text_message = TextMessage("خوش آمدید! برای ورود به گروه، لطفاً پرداخت را انجام دهید.")
    # دکمه پرداخت
    payment_button = TemplateMessageButton(text="پرداخت", value="request_payment", action=0)
    template_message = TemplateMessage(general_message=text_message, btn_list=[payment_button])
    bot.reply(update, template_message)
    # ثبت مرحله بعدی برای مدیریت پاسخ دکمه
    dispatcher.register_conversation_next_step_handler(
        update,
        [MessageHandler(TemplateResponseFilter(keywords="request_payment"), send_payment_link)]
    )

# ارسال لینک پرداخت
def send_payment_link(update, bot):
    user_peer = update.get_effective_user()
    # درخواست پرداخت (مثال: 100,000 تومان)
    invoice = {
        "title": "پرداخت برای ورود به گروه",
        "description": "پرداخت 100,000 تومان برای دریافت لینک گروه",
        "provider_token": "WALLET-TEST-1111111111111111",  # توکن کیف پول واقعی را جای‌گذاری کنید
        "start_parameter": "pay",
        "currency": "IRR",
        "prices": [{"label": "هزینه ورود", "amount": 10000000}]  # مبلغ به ریال (100,000 تومان)
    }
    bot.send_invoice(update, **invoice)
    # ثبت مرحله برای بررسی تأیید پرداخت
    dispatcher.register_conversation_next_step_handler(
        update,
        [MessageHandler(DefaultFilter(), check_payment)]
    )

# بررسی پرداخت و ارسال لینک گروه
def check_payment(update, bot):
    user_peer = update.get_effective_user()
    if update.pre_checkout_query:  # بررسی پرداخت
        bot.answer_pre_checkout_query(update.pre_checkout_query.id, ok=True)
        # ارسال لینک گروه پس از تأیید پرداخت
        bot.reply(update, TextMessage(f"پرداخت تأیید شد! لینک گروه: {GROUP_LINK}"))
        # انتقال مبلغ به شماره تلفن دیگر (این بخش نیاز به API کیف پول دارد)
        transfer_to_phone(bot, user_peer, DESTINATION_PHONE)
    else:
        bot.reply(update, TextMessage("پرداخت ناموفق بود. دوباره امتحان کنید."))

# تابع انتقال پول به شماره تلفن دیگر (این بخش نیاز به پیاده‌سازی API کیف پول دارد)
def transfer_to_phone(bot, user_peer, phone_number):
    # این بخش باید با API کیف پول بله پیاده‌سازی شود
    # در حال حاضر، به عنوان مثال، پیام تأیید انتقال ارسال می‌شود
    bot.send_message(user_peer, TextMessage(f"مبلغ به شماره {phone_number} منتقل شد."))

# ثبت هندلر برای شروع مکالمه
dispatcher.register_message_handler(MessageHandler(DefaultFilter(), start_conversation), commands=["start"])

# اجرای ربات
def main():
    updater.run()

if __name__ == "__main__":
    main()