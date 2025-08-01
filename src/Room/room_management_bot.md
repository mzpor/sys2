# سناریوی ربات مدیریت روم

این سند توضیح می‌دهد که ربات مدیریت روم چگونه کار می‌کند. این ربات برای مدیریت اعضای روم و ثبت حضور و غیاب طراحی شده است.

## قابلیت‌های اصلی

1. **ورود به روم و مدیریت اعضا**:
   - ربات به روم وارد می‌شود و به عنوان ادمین تنظیم می‌شود
   - کاربران می‌توانند با دستور `/عضو` در گروه ثبت‌نام کنند
   - ربات لیست اعضا را نگهداری و به‌روزرسانی می‌کند

2. **مدیریت حضور و غیاب**:
   - مربی می‌تواند در چت خصوصی با ربات، لیست اعضا را مشاهده کند
   - مربی می‌تواند وضعیت حضور اعضا را ثبت کند (حاضر، غایب)

## پیکربندی اولیه

- در فایل کانفیگ، مشخصات مربی، کمک مربی و مدیر تعیین می‌شود
- توکن ربات و سایر تنظیمات اولیه در این فایل قرار می‌گیرد

## جریان کار ربات

### 1. راه‌اندازی و پیکربندی
- ربات با استفاده از توکن به API بله متصل می‌شود
- اطلاعات پیکربندی از فایل کانفیگ خوانده می‌شود
- ربات به عنوان ادمین در روم تنظیم می‌شود

### 2. ثبت‌نام اعضا
- کاربران با ارسال دستور `/عضو` در گروه ثبت‌نام می‌کنند
- ربات اطلاعات کاربر را در پایگاه داده ذخیره می‌کند
- لیست به‌روز شده اعضا نمایش داده می‌شود

### 3. مدیریت حضور و غیاب
- مربی در چت خصوصی با ربات، دستور مشاهده لیست اعضا را ارسال می‌کند
- ربات لیست اعضا را همراه با گزینه‌های حضور و غیاب نمایش می‌دهد
- مربی وضعیت حضور هر عضو را ثبت می‌کند
- ربات اطلاعات حضور و غیاب را ذخیره می‌کند

## ساختار داده‌ها

### اطلاعات اعضا
```python
members = {
    "user_id": {
        "name": "نام کاربر",
        "join_date": "تاریخ عضویت",
        "is_admin": False
    }
}
```

### اطلاعات حضور و غیاب
```python
attendance = {
    "date": {
        "user_id": "status"  # حاضر یا غایب
    }
}
```

## دستورات ربات

- `/عضو` - ثبت‌نام در گروه
- `/لیست` - نمایش لیست اعضا
- `/حضورغیاب` - (فقط برای مربی در چت خصوصی) شروع فرآیند ثبت حضور و غیاب

## پیام‌های ربات

### پیام خوش‌آمدگویی
```
🎉 به ربات مدیریت روم خوش آمدید!

دستورات:
👥 /عضو - ثبت در گروه
📋 /لیست - مشاهده لیست اعضا
```

### پیام تأیید عضویت
```
✅ [نام کاربر] عزیز، شما با موفقیت در گروه ثبت شدید!
```

### نمایش لیست اعضا
```
📋 لیست اعضا
📅 [تاریخ]

👥 اعضا:
1. [نام کاربر ۱]
2. [نام کاربر ۲]
...

📊 تعداد کل: [تعداد]
```

### پیام حضور و غیاب (در چت خصوصی مربی)
```
📋 لیست حضور و غیاب
📅 [تاریخ]

لطفاً وضعیت حضور هر عضو را مشخص کنید:
```

## نکات پیاده‌سازی

- استفاده از کتابخانه `requests` برای ارتباط با API بله
- ذخیره‌سازی داده‌ها در فایل JSON
- استفاده از کیبوردهای شیشه‌ای برای ثبت حضور و غیاب
- مدیریت خطاها و پیام‌های مناسب برای کاربران