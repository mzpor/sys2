 """
تمرین 1: راه‌اندازی اولیه و import ها
سطح: مبتدی
هدف: آشنایی با import ها و تنظیمات اولیه
"""

# کتابخانه‌های مورد نیاز
import jdatetime  # برای کار با تاریخ شمسی
import requests   # برای ارتباط با API بله
import json       # برای کار با داده‌های JSON
import time       # برای کار با زمان
import re         # برای کار با عبارات منظم
import logging    # برای ثبت گزارش‌ها
import os         # برای بررسی وجود فایل
import sys        # برای کار با سیستم

# تنظیمات اولیه سیستم ثبت گزارش
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# متغیرهای اولیه
log1 = sys1 = "appwrite mzpor sony"
delay = 0.2

# توکن ربات (در محیط تولید باید از متغیر محیطی استفاده شود)
BOT_TOKEN = '811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1'

# آدرس‌های API
API_URL = f'https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates'
SEND_URL = f'https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage'
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

print("✅ تمرین 1: راه‌اندازی اولیه تکمیل شد!")
print(f"📝 توکن ربات: {BOT_TOKEN}")
print(f"🌐 آدرس API: {BASE_URL}")

# تمرین: سعی کنید متغیرهای بالا را تغییر دهید
# تمرین: یک متغیر جدید اضافه کنید
# تمرین: یک import جدید اضافه کنید