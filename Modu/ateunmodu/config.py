# config.py
BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

AUTHORIZED_USER_IDS = [
    574330749,  # محمد زارع ۲
    1114227010,  # محمد ۱
    1775811194,  # محرابی
]

# گروه‌های تلگرامی (chat_id گروه‌ها)
GROUPS = {
    "group1": {"chat_id": "-123456789", "teacher_id": 574330749, "name": "گروه کلاس تجوید"},
    "group2": {"chat_id": "-987654321", "teacher_id": 1114227010, "name": "گروه کلاس حفظ"}
}