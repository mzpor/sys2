import requests
import json


# توکن ربات از متغیر محیطی
#BOT_TOKEN = os.environ.get('BOT_TOKEN', '811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1')  # یار مربی (برای تست)
BOT_TOKEN = '811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1'
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

# لیست کاربران
users = [f"کاربر{i+1}" for i in range(10)]
statuses = ["حاضر", "تاخیر", "غایب", "موجه"]

# دیکشنری برای ذخیره وضعیت‌ها (اگه API نداری)
attendance_data = {}

# تابع برای شبیه‌سازی ارسال کیبورد شیشه‌ای
def send_inline_keyboard(user):
    print(f"\n📋 {user}")
    print("انتخاب وضعیت:")
    for i, status in enumerate(statuses):
        print(f"{i+1}. {status} (دکمه شیشه‌ای: {status})")
    return input("کد وضعیت انتخابی (1-4): ")

# تابع برای ثبت وضعیت در API یا دیکشنری
def submit_attendance(user, status):
    # اگر API داری، اینجا درخواست POST می‌فرستی
    url = "https://your-attendance-api.com/submit"  # جای اینو با API واقعی عوض کن
    payload = {
        "user": user,
        "status": status
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ وضعیت {user} ثبت شد: {status}")
            attendance_data[user] = status  # ذخیره در دیکشنری
        else:
            print(f"❌ ثبت ناموفق برای {user}: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ خطا در ارتباط با API: {e}")
        # ذخیره در دیکشنری به جای API
        attendance_data[user] = status
        print(f"✅ وضعیت {user} به صورت محلی ثبت شد: {status}")

# تابع برای تولید گزارش نهایی
def generate_report():
    report = []
    for user in users:
        status = attendance_data.get(user, "ثبت‌نشده")
        report.append(f"{user} - {status}")
    
    # چاپ گزارش
    print("\n📋 گزارش نهایی حضور و غیاب:")
    for line in report:
        print(line)
    
    # ذخیره گزارش به صورت JSON
    with open("attendance_report.json", "w", encoding="utf-8") as f:
        json.dump(attendance_data, f, ensure_ascii=False, indent=4)
    print("\n📎 گزارش به صورت JSON در فایل 'attendance_report.json' ذخیره شد.")

# شبیه‌سازی فرآیند
def main():
    print("🤖 ربات حضور و غیاب شروع به کار کرد!")
    print("📌 لطفاً برای هر کاربر وضعیت را انتخاب کنید.")

    for user in users:
        selected = send_inline_keyboard(user)
        try:
            chosen_status = statuses[int(selected) - 1]
            submit_attendance(user, chosen_status)
        except (ValueError, IndexError):
            print(f"❌ ورودی نامعتبر برای {user}. لطفاً عدد 1 تا 4 وارد کنید.")
    
    # تولید گزارش نهایی
    generate_report()

if __name__ == "__main__":
    main()