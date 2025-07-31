# سناریو ربات ثبت‌نام بله (اصلاح‌شده)

## مرحله ۱: شروع
- کاربر `/start` را وارد می‌کند.
- کیبورد معمولی:  
  ```
  [شروع مجدد] [معرفی آموزشگاه] [خروج]
- پیام:  
  _🌟 خوش آمدید! به ربات ثبت‌نام آموزشگاه خوش آمدید!_  
  ```
- کیبورد شیشه‌ای:  
  ```
  [[{text: "📝 شروع ثبت‌نام", callback_data: "start_registration"}]]
  ```

  ## پیکربندی اولیه 
- **توکن و API**:
  - `BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"`.
  - آدرس‌ها:
    - `API_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates"`
    - `SEND_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"`
    - `BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"`
- **کتابخانه‌ها**:
  - `jdatetime`: تاریخ شمسی.
  - `requests`: ارتباط با API بله.
  - `json`: مدیریت JSON.
  - `time`: مدیریت زمان.
  - `re`: اعتبارسنجی با عبارات منظم.
  - `logging`: گزارش‌های انگلیسی.
  - `os`: بررسی فایل.
  - `sys`: مدیریت سیستم.
- داده‌ها در فایل JSON ذخیره و با `os` بررسی می‌شوند.
- گزارش‌ها با `logging` به‌صورت انگلیسی (مثل: `INFO: User registered`).
- کد پایتون با کامنت‌های فارسی.

اسم فایل جیسون 
DATA_FILE = "1.json"