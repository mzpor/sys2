# config.py
# توکن بات
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

# لیست کاربران مجاز (مربیان)
AUTHORIZED_USER_IDS = [
    574330749,  # محمد زارع ۲
    2045777722,  # رایتل
  #  1790308237,  # ایرانسل
    1114227010,  # محمد ۱ (user_id شما)
    1775811194,  # محرابی
]

# user_id مدیر
ADMIN_USER_ID = 1114227010  # برای تست، user_id خودت

# دیکشنری برای ذخیره گروه‌ها و مربی‌ها
GROUP_TEACHERS = {
    # "chat_id گروه": [لیست user_id مربی‌ها]
}

# دیکشنری برای ذخیره اعضای گروه‌ها
GROUP_MEMBERS = {
    # "chat_id گروه": [لیست user_id اعضای غیرادمین]
}