
# config.py
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

#BOT_TOKEN = '1423205711:aNMfw7aEfrMwHNITw4S7bTs9NP92MRzcDLg19Hjo'# یار ثبت نام 
#BOT_TOKEN = '811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1'  #یار مربی
#BOT_TOKEN = '1714651531:y2xOK6EBg5nzVV6fEWGqtOdc3nVqVgOuf4PZVQ7S'#یار مدیر

# لیست کاربران مجاز (مربیان)
AUTHORIZED_USER_IDS = [ #مربی 
    574330749,    # محمد زارع ۲
#    2045777722,   # رایتل
    1114227010,   # محمد ۱
    1775811194,   # محرابی
    #1790308237     ایراتسل
]

# لیست کمک مربیان
HELPER_COACH_USER_IDS = [ # کمک مربی 
 574330749,    # محمد زارع ۲
  #  2045777722,   # رایتل
]

# لیست مدیران (می‌توانید چندین مدیر اضافه کنید)
ADMIN_USER_IDS = [
    1114227010,   # محمد ۱
#   574330749,    # محمد زارع ۲
    1775811194,   # محرابی
]

# دیکشنری برای ذخیره گروه‌ها و مربی‌ها
GROUP_TEACHERS = {}

# دیکشنری برای ذخیره اعضای گروه‌ها
GROUP_MEMBERS = {}
