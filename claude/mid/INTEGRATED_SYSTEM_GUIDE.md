# راهنمای سیستم یکپارچه کارگاه و پرداخت

## 🚀 سیستم جدید یکپارچه

### ✅ تغییرات انجام شده:

1. **ماژول پرداخت تبدیل شد به کلاس:**
   - `pay.py` → `PaymentModule`
   - اتصال مستقیم با سیستم کارگاه
   - استفاده از نام و هزینه کارگاه‌ها

2. **هماهنگی کامل:**
   - نام کارگاه‌ها از سیستم کارگاه
   - هزینه‌ها از سیستم کارگاه
   - لینک‌های گروه از سیستم کارگاه

3. **ویژگی‌های جدید:**
   - پشتیبانی از اعداد فارسی و انگلیسی
   - نرمال‌سازی خودکار هزینه‌ها
   - مدیریت خطا بهتر

## 📱 نحوه استفاده

### 1. مدیریت کارگاه (برای مدیران)
```
/kargah
```
- لیست کارگاه‌ها
- اضافه کردن کارگاه جدید
- ویرایش کارگاه‌ها
- حذف کارگاه‌ها

### 2. سیستم پرداخت (برای کاربران)
```
/start
```
- انتخاب کارگاه
- پرداخت آنلاین
- دریافت لینک گروه

## 🔧 ساختار جدید

### ماژول‌های سیستم:
```
main.py              # فایل اصلی ربات
├── kargah_module.py    # مدیریت کارگاه‌ها
├── payment_module.py   # سیستم پرداخت
├── attendance_module.py # حضور و غیاب
└── group_management_module.py # مدیریت گروه‌ها
```

### جریان کار:
1. **مدیر کارگاه‌ها را اضافه می‌کند** (`/kargah`)
2. **کاربران کارگاه‌ها را می‌بینند** (`/start`)
3. **پرداخت انجام می‌شود** (اتوماتیک)
4. **لینک گروه ارسال می‌شود** (اتوماتیک)

## 💰 سیستم پرداخت

### ویژگی‌های پرداخت:
- **پشتیبانی از اعداد فارسی:** `۱۰۰۰۰` → `10000 تومان`
- **پشتیبانی از اعداد انگلیسی:** `10000` → `10000 تومان`
- **فرمت‌های مختلف:** `500,000 تومان`, `۷۵۰۰۰۰ تومان`
- **تبدیل خودکار:** ریال به تومان

### مثال‌های ورودی:
```
۱۰۰۰۰        → 10000 تومان
10000        → 10000 تومان
۵۰۰,۰۰۰ تومان → 500,000 تومان
500,000 تومان → 500,000 تومان
۷۵۰۰۰۰       → 750000 تومان
750000       → 750000 تومان
```

## 🎯 مزایای سیستم جدید

### ✅ برای مدیران:
1. **مدیریت متمرکز:** همه کارگاه‌ها در یک جا
2. **ویرایش آسان:** تغییر نام، هزینه، لینک
3. **هماهنگی کامل:** تغییرات فوری در سیستم پرداخت

### ✅ برای کاربران:
1. **انتخاب آسان:** لیست کارگاه‌های موجود
2. **پرداخت امن:** سیستم پرداخت یکپارچه
3. **دسترسی سریع:** لینک گروه بعد از پرداخت

### ✅ برای سیستم:
1. **یکپارچگی:** همه چیز هماهنگ
2. **مدیریت خطا:** پیام‌های واضح
3. **قابلیت توسعه:** اضافه کردن ویژگی‌های جدید

## 🧪 تست سیستم

### تست ماژول کارگاه:
```bash
python test_kargah.py
```

### تست ماژول پرداخت:
```bash
python test_payment_module.py
```

### تست نرمال‌سازی هزینه:
```bash
python test_cost_normalization.py
```

## 📊 نمونه کارکرد

### 1. مدیر کارگاه اضافه می‌کند:
```
/kargah
📝 اضافه کردن کارگاه
نام مربی: آقای رشوند
هزینه: 500,000 تومان
لینک: https://t.me/workshop1
✅ کارگاه با موفقیت اضافه شد!
```

### 2. کاربر کارگاه را می‌بیند:
```
/start
🎓 لطفاً یکی از کارگاه‌ها رو انتخاب کن:

[📚 آقای رشوند - 500,000 تومان]
[📚 آقای حتم خانی - 500,000 تومان]
[🔙 بازگشت]
```

### 3. پرداخت انجام می‌شود:
```
💳 پرداخت برای آقای رشوند
مبلغ: 500,000 تومان
[پرداخت آنلاین]
```

### 4. بعد از پرداخت:
```
💸 پرداخت برای 'آقای رشوند' با موفقیت انجام شد!
📎 لینک ورود به گروه: https://t.me/workshop1
🎉 از اینکه همراه شدید، بی‌نهایت سپاسگزاریم!
```

## 🆘 عیب‌یابی

### مشکلات رایج:
1. **کارگاه نمایش داده نمی‌شود:** بررسی کنید که کارگاه اضافه شده باشد
2. **پرداخت کار نمی‌کند:** بررسی توکن پرداخت
3. **خطای نرمال‌سازی:** بررسی فرمت هزینه

### راه‌حل‌ها:
1. **ربات را دوباره راه‌اندازی کنید**
2. **فایل‌های JSON را بررسی کنید**
3. **لاگ‌ها را چک کنید**

## ✅ نتیجه

حالا سیستم کاملاً یکپارچه است:
- **کارگاه‌ها** با **پرداخت** هماهنگ هستند
- **نام و هزینه** از یک منبع می‌آیند
- **لینک‌های گروه** خودکار ارسال می‌شوند
- **اعداد فارسی و انگلیسی** پشتیبانی می‌شوند

سیستم آماده استفاده است! 🎉 