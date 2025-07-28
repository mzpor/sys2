 """
تمرین 4: توابع تاریخ و زمان
سطح: مبتدی
هدف: آشنایی با کار با تاریخ و زمان
"""

import jdatetime
from datetime import datetime

def get_jalali_date():
    """
    دریافت تاریخ شمسی امروز
    
    خروجی:
        str: تاریخ شمسی به صورت رشته
    """
    today = jdatetime.date.today()
    return today.strftime("%Y/%m/%d")

def get_week_day():
    """
    دریافت روز هفته
    
    خروجی:
        str: نام روز هفته
    """
    today = jdatetime.date.today()
    weekdays = {
        0: "شنبه",
        1: "یکشنبه", 
        2: "دوشنبه",
        3: "سه‌شنبه",
        4: "چهارشنبه",
        5: "پنج‌شنبه",
        6: "جمعه"
    }
    return weekdays[today.weekday()]

def is_exercise_day():
    """
    بررسی اینکه آیا امروز روز تمرین است یا نه
    
    خروجی:
        bool: True اگر امروز روز تمرین باشد
    """
    today = get_week_day()
    exercise_days = ["شنبه", "دوشنبه", "چهارشنبه"]
    return today in exercise_days

def get_exercise_deadline():
    """
    دریافت مهلت ارسال تمرین
    
    خروجی:
        str: مهلت ارسال تمرین
    """
    today = jdatetime.date.today()
    # مهلت تا ساعت 23:59 همان روز
    return f"{today.strftime('%Y/%m/%d')} ساعت 23:59"

print("✅ تمرین 4: توابع تاریخ و زمان تکمیل شد!")

# تست توابع
print(f"📅 تاریخ امروز: {get_jalali_date()}")
print(f"📆 روز هفته: {get_week_day()}")
print(f"🏃‍♂️ آیا امروز روز تمرین است؟ {'بله' if is_exercise_day() else 'خیر'}")
print(f"⏰ مهلت ارسال تمرین: {get_exercise_deadline()}")

# تمرین: تابعی برای محاسبه روزهای باقی‌مانده تا آخر هفته بنویسید
# تمرین: تابعی برای تبدیل تاریخ میلادی به شمسی بنویسید
# تمرین: تابعی برای بررسی اینکه آیا امروز تعطیل است یا نه بنویسید