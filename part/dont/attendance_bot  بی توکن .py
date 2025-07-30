import json

# تنظیمات
AUTHORIZED_USER_ID = 574330749  # آیدی مجاز
users = [f"کاربر{i+1}" for i in range(10)]  # لیست کاربران
statuses = ["حاضر", "تاخیر", "غایب", "موجه"]  # وضعیت‌های ممکن
attendance_data = {}  # ذخیره وضعیت‌ها

# تابع بررسی دسترسی کاربر
def is_user_authorized(user_id):
    return user_id == AUTHORIZED_USER_ID

# تابع نمایش منو و گرفتن ورودی
def show_menu(user):
    print(f"\n📋 {user}")
    print("لطفاً وضعیت را انتخاب کنید:")
    for i, status in enumerate(statuses, 1):
        print(f"{i}. {status}")
    while True:
        try:
            choice = int(input("شماره گزینه (1-4): "))
            if 1 <= choice <= 4:
                return statuses[choice - 1]
            print("❌ لطفاً عدد بین 1 تا 4 وارد کنید.")
        except ValueError:
            print("❌ ورودی نامعتبر! لطفاً عدد وارد کنید.")

# تابع ویرایش وضعیت
def edit_status(user):
    print(f"\n✏ ویرایش وضعیت {user}")
    return show_menu(user)

# تابع تولید گزارش
def generate_report():
    report = ["📋 گزارش نهایی حضور و غیاب:"]
    for user in users:
        status = attendance_data.get(user, "ثبت‌نشده")
        report.append(f"{user} - {status}")
    
    # نمایش گزارش متنی
    print("\n".join(report))
    
    # ذخیره گزارش JSON
    with open("attendance_report.json", "w", encoding="utf-8") as f:
        json.dump(attendance_data, f, ensure_ascii=False, indent=4)
    print("\n📎 گزارش در فایل 'attendance_report.json' ذخیره شد.")

# حلقه اصلی
def main():
    # بررسی دسترسی
    user_id = int(input("لطفاً آیدی خود را وارد کنید: "))
    if not is_user_authorized(user_id):
        print("❌ شما اجازه دسترسی ندارید!")
        return
    
    print("سلام مربی عزیز 👋")
    
    # ثبت وضعیت برای هر کاربر
    for user in users:
        status = show_menu(user)
        attendance_data[user] = status
        print(f"✔ وضعیت {user} ثبت شد: {status}")
        
        # امکان ویرایش
        edit = input(f"آیا می‌خواهید وضعیت {user} را ویرایش کنید؟ (بله/خیر): ")
        if edit.lower() == "بله":
            status = edit_status(user)
            attendance_data[user] = status
            print(f"✔ وضعیت {user} به‌روزرسانی شد: {status}")
    
    # تولید گزارش
    generate_report()

if __name__ == "__main__":
    main()