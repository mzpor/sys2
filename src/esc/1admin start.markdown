# سناریو ربات مدیریت گروه

## تنظیمات اولیه
- **توکن و API**:
  - `BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"`.
  - آدرس‌ها:
    - `API_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/getUpdates"`
    - `SEND_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"`
    - `BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"`
- **فایل داده**: `1.json` برای ذخیره اطلاعات کاربران، مربی‌ها، کمک مربی‌ها و کلاس‌ها.
- **ذخیره‌سازی**: اطلاعات فقط در تأیید نهایی یا ویرایش به‌روزرسانی می‌شود. با "شروع جدید"، فقط حافظه موقت پاک می‌شود.
- **پیام‌ها**: فارسی، کوتاه، با ایموجی‌های 🌟، ✅، ✏️، 📱، 📋، 🎉 و نام کوچک کاربر.
- **کیبوردها**: 
  - معمولی: گزینه‌های ثابت (شروع جدید، خروج، پاک‌سازی اطلاعات).
  - شیشه‌ای: برای تأیید، تصحیح یا مراحل خاص (مثل ارسال شماره تلفن با `request_contact: true`).
- **گزارش‌ها**: لاگ‌های انگلیسی در فایل `bot.log` (مثال: `INFO: User registered`).

## کیبوردهای اصلی
- **کیبورد معمولی پیش‌فرض**:
  ```
  [🔁 شروع جدید] [🚫 خروج]
  [🧹 پاک‌سازی اطلاعات]
  ```
- **کیبورد پنل مدیریتی**:
  ```
  [🔁 شروع جدید] [📊 پنل کاربری]
  [🧹 پاک‌سازی اطلاعات] [🚫 خروج]
  ```

---

## سناریو برای مدیر

### مرحله ۱: شروع
- کاربر `/start` یا `شروع جدید` را وارد می‌کند.
- اگر اولین کاربر باشد، به‌عنوان **مدیر** ثبت می‌شود.
- **پیام**:
  ```
  _🌟 کاربر عزیز، به ربات مدیریت گروه خوش آمدید!_
  شما مدیر هستید. لطفاً ثبت‌نام را ادامه دهید یا به پنل کاربری بروید.
  ```
- **کیبورد معمولی**:
  ```
  [🔁 شروع جدید] [📊 پنل کاربری] [🧹 پاک‌سازی اطلاعات] [🚫 خروج]
  ```
- **کیبورد شیشه‌ای**:
  ```
  [[{text: "📝 شروع ثبت‌نام", callback_data: "start_registration"}]]
  ```

### مرحله ۲: دریافت نام و نام خانوادگی
- کاربر دکمه `شروع ثبت‌نام` را انتخاب می‌کند.
- **پیام**:
  ```
  _لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی)._
  ```
- کاربر نام را وارد می‌کند (مثال: علی رضایی).
- ذخیره در JSON: `{"full_name": "علی رضایی", "first_name": "علی", "role": "admin"}`.
- **پیام**:
  ```
  _علی عزیز،_
  نام شما: علی رضایی
  کد ملی: هنوز مانده
  تلفن: هنوز مانده

  لطفاً کد ملی ۱۰ رقمی خود را وارد کنید.
  ```
- **کیبورد معمولی**:
  ```
  [🔁 شروع جدید] [🚫 خروج] [⬅️ برگشت به قبل]
  ```
- **کیبورد شیشه‌ای**:
  ```
  [[{text: "✏️ تصحیح نام", callback_data: "edit_name"}]]
  ```

### مرحله ۳: دریافت کد ملی
- کاربر کد ملی را وارد می‌کند (مثال: 1234567890).
- بررسی: اگر ۱۰ رقم نباشد، خطا: `_❌ کد ملی نامعتبر است. دوباره وارد کنید._`
- ذخیره در JSON: `{"full_name": "علی رضایی", "first_name": "علی", "national_id": "1234567890", "role": "admin"}`.
- **پیام**:
  ```
  _علی عزیز،_
  نام شما: علی رضایی
  کد ملی: 1234567890
  تلفن: هنوز مانده

  لطفاً برای ارسال شماره تلفن خود روی دکمه زیر بزنید.
  ```
- **کیبورد معمولی**:
  ```
  [🔁 شروع جدید] [🚫 خروج] [⬅️ برگشت به قبل]
  ```
- **کیبورد شیشه‌ای**:
  ```
  [[{text: "✏️ تصحیح کد ملی", callback_data: "edit_national_id"}],
   [{text: "📱 ارسال شماره تلفن", request_contact: true}]]
  ```

### مرحله ۴: دریافت شماره تلفن
- کاربر دکمه `ارسال شماره تلفن` را زده و شماره (مثال: `989123456789`) ارسال می‌شود.
- ذخیره در JSON: `{"full_name": "علی رضایی", "first_name": "علی", "national_id": "1234567890", "phone": "989123456789", "role": "admin"}`.
- **پیام**:
  ```
  _📋 علی عزیز، حساب کاربری شما:_
  نام: علی رضایی
  کد ملی: 1234567890
  تلفن: 09123456789

  آیا اطلاعات درست است؟
  ```
- **کیبورد معمولی**:
  ```
  [🔁 شروع جدید] [🚫 خروج] [⬅️ برگشت به قبل]
  ```
- **کیبورد شیشه‌ای**:
  ```
  [[{text: "✅ تأیید نهایی", callback_data: "final_confirm"}],
   [{text: "✏️ تصحیح اطلاعات", callback_data: "edit_info"}]]
  ```

### مرحله ۵: تأیید نهایی
- اگر کاربر `تأیید نهایی` را انتخاب کند:
  - اطلاعات در `1.json` ذخیره می‌شود.
  - **پیام**:
    ```
    _🎉 علی عزیز، ثبت‌نام شما به عنوان مدیر با موفقیت تکمیل شد!_
    حالا می‌توانید ربات را به گروه اضافه کنید و کلاس‌ها را مدیریت کنید.
    ```
  - **کیبورد معمولی**: پنل مدیریتی نمایش داده می‌شود.
- اگر `تصحیح اطلاعات` را انتخاب کند:
  - JSON موقت پاک شده و به مرحله ۲ (دریافت نام) بازمی‌گردد.

### مرحله ۶: پنل مدیریتی
- کاربر دکمه `پنل کاربری` را انتخاب می‌کند.
- **پیام**:
  ```
  _📊 پنل مدیریتی_

  *لیست کلاس‌ها:*
  [نام کلاس]: [هزینه] تومان - [لینک گروه]
  (یا: هیچ کلاسی ثبت نشده)

  *لیست مربی‌ها:*
  [نام مربی]: [تلفن]
  (یا: هیچ مربی‌ای ثبت نشده)

  *لیست کمک مربی‌ها:*
  [نام کمک مربی]: [تلفن]
  (یا: هیچ کمک مربی‌ای ثبت نشده)

  برای مدیریت کلاس‌ها یا تأیید مربی‌ها، گزینه‌ها را انتخاب کنید.
  ```
- **کیبورد معمولی**:
  ```
  [🔁 شروع جدید] [📊 پنل کاربری] [🧹 پاک‌سازی اطلاعات] [🚫 خروج]
  ```
- **کیبورد شیشه‌ای**:
  ```
  [[{text: "➕ افزودن کلاس", callback_data: "add_class"}],
   [{text: "✏️ ویرایش کلاس", callback_data: "edit_class"}],
   [{text: "📬 تأیید مربی‌ها", callback_data: "confirm_trainer"}]]
  ```

### مرحله ۷: افزودن کلاس
- کاربر `افزودن کلاس` را انتخاب می‌کند.
- **پیام**: `_لطفاً نام کلاس را وارد کنید._`
- کاربر نام کلاس را وارد می‌کند (مثال: کلاس قرآن).
- **پیام**: `_نام کلاس: کلاس قرآن_\nلطفاً هزینه کلاس را وارد کنید (به تومان).`
- کاربر هزینه را وارد می‌کند (مثال: 500000).
- **پیام**: `_هزینه کلاس: 500000 تومان_\nلطفاً لینک گروه کلاس را وارد کنید (مثال: ble.ir/join/xxx).`
- کاربر لینک گروه را وارد می‌کند (مثال: ble.ir/join/Gah9cS9LzQ).
- ذخیره در JSON: `{"classes": {"کلاس قرآن": {"cost": "500000", "link": "ble.ir/join/Gah9cS9LzQ"}}}`.
- **پیام**:
  ```
  _✅ کلاس با موفقیت ثبت شد:_
  نام: کلاس قرآن
  هزینه: 500000 تومان
  لینک: ble.ir/join/Gah9cS9LzQ
  ```
- بازگشت به پنل مدیریتی.

### مرحله ۸: ویرایش کلاس
- کاربر `ویرایش کلاس` را انتخاب می‌کند.
- **پیام**: `_لطفاً کلاس موردنظر برای ویرایش را انتخاب کنید._`
- **کیبورد شیشه‌ای**: دکمه‌هایی برای هر کلاس (مثال: `[کلاس قرآن]`).
- پس از انتخاب کلاس:
  - **پیام**: `_لطفاً نام جدید کلاس را وارد کنید._`
  - مراحل مشابه افزودن کلاس برای به‌روزرسانی نام، هزینه و لینک.
- اطلاعات در JSON به‌روزرسانی می‌شود.

---

## سناریو برای مربی/کمک مربی

### مرحله ۱: شروع
- کاربر `/start` یا `شروع جدید` را وارد می‌کند.
- **پیام**:
  ```
  _🌟 خوش آمدید! به ربات مدیریت گروه خوش آمدید!_
  لطفاً نقش خود را انتخاب کنید.
  ```
- **کیبورد معمولی**:
  ```
  [🔁 شروع جدید] [🚫 خروج] [🧹 پاک‌سازی اطلاعات]
  ```
- **کیبورد شیشه‌ای**:
  ```
  [[{text: "👨‍🏫 مربی", callback_data: "select_trainer"},
    {text: "🤝 کمک مربی", callback_data: "select_assistant"},
    {text: "📚 قرآن‌آموز", callback_data: "select_student"}]]
  ```

### مرحله ۲: انتخاب نقش
- کاربر `مربی` یا `کمک مربی` را انتخاب می‌کند.
- کد تصادفی ۶ رقمی تولید و برای مدیر ارسال می‌شود.
- **پیام به مدیر**:
  ```
  _📬 درخواست جدید_
  کاربر [user_id] درخواست [مربی/کمک مربی] داده است.
  کد تأیید: [123456]
  ```
- **پیام به کاربر**:
  ```
  _لطفاً کد تأیید ارسال‌شده توسط مدیر را وارد کنید._
  ```
- **کیبورد معمولی**:
  ```
  [🔁 شروع جدید] [🚫 خروج]
  ```

### مرحله ۳: تأیید کد
- کاربر کد ۶ رقمی را وارد می‌کند.
- اگر معتبر باشد:
  - ذخیره نقش در JSON: `{"role": "trainer"}` یا `{"role": "assistant"}`.
  - **پیام**:
    ```
    _✅ کد تأیید شد._
    لطفاً نام و نام خانوادگی خود را وارد کنید (مثال: علی رضایی).
    ```
- اگر نامعتبر باشد:
  - **پیام**: `_❌ کد نامعتبر است. دوباره وارد کنید._`

### مرحله ۴: دریافت نام و نام خانوادگی
- کاربر نام را وارد می‌کند (مثال: علی رضایی).
- ذخیره در JSON: `{"full_name": "علی رضایی", "first_name": "علی", "role": "trainer/assistant"}`.
- **پیام**:
  ```
  _علی عزیز،_
  نام شما: علی رضایی
  کد ملی: هنوز مانده
  تلفن: هنوز مانده

  لطفاً کد ملی ۱۰ رقمی خود را وارد کنید.
  ```
- **کیبورد معمولی**:
  ```
  [🔁 شروع جدید] [🚫 خروج] [⬅️ برگشت به قبل]
  ```
- **کیبورد شیشه‌ای**:
  ```
  [[{text: "✏️ تصحیح نام", callback_data: "edit_name"}]]
  ```

### مرحله ۵: دریافت کد ملی
- کاربر کد ملی را وارد می‌کند (مثال: 1234567890).
- بررسی: اگر ۱۰ رقم نباشد، خطا: `_❌ کد ملی نامعتبر است. دوباره وارد کنید._`
- ذخیره در JSON: `{"full_name": "علی رضایی", "first_name": "علی", "national_id": "1234567890", "role": "trainer/assistant"}`.
- **پیام**:
  ```
  _علی عزیز،_
  نام شما: علی رضایی
  کد ملی: 1234567890
  تلفن: هنوز مانده

  لطفاً برای ارسال شماره تلفن خود روی دکمه زیر بزنید.
  ```
- **کیبورد معمولی**:
  ```
  [🔁 شروع جدید] [🚫 خروج] [⬅️ برگشت به قبل]
  ```
- **کیبورد شیشه‌ای**:
  ```
  [[{text: "✏️ تصحیح کد ملی", callback_data: "edit_national_id"}],
   [{text: "📱 ارسال شماره تلفن", request_contact: true}]]
  ```

### مرحله ۶: دریافت شماره تلفن
- کاربر دکمه `ارسال شماره تلفن` را زده و شماره (مثال: `989123456789`) ارسال می‌شود.
- ذخیره در JSON: `{"full_name": "علی رضایی", "first_name": "علی", "national_id": "1234567890", "phone": "989123456789", "role": "trainer/assistant"}`.
- **پیام**:
  ```
  _📋 علی عزیز، حساب کاربری شما:_
  نام: علی رضایی
  کد ملی: 1234567890
  تلفن: 09123456789

  آیا اطلاعات درست است؟
  ```
- **کیبورد معمولی**:
  ```
  [🔁 شروع جدید] [🚫 خروج] [⬅️ برگشت به قبل]
  ```
- **کیبورد شیشه‌ای**:
  ```
  [[{text: "✅ تأیید نهایی", callback_data: "final_confirm"}],
   [{text: "✏️ تصحیح اطلاعات", callback_data: "edit_info"}]]
  ```

### مرحله ۷: تأیید نهایی
- اگر `تأیید نهایی` انتخاب شود:
  - اطلاعات در JSON ذخیره می‌شود: `{"trainers"/"assistants": {user_id: {"full_name": "علی رضایی", "national_id": "1234567890", "phone": "989123456789"}}}`.
  - **پیام به مدیر**:
    ```
    _📬 [علی] به عنوان [مربی/کمک مربی] ثبت شد:_
    نام: علی رضایی
    کد ملی: 1234567890
    تلفن: 09123456789
    ```
  - **پیام به کاربر**:
    ```
    _🎉 علی عزیز، ثبت‌نام شما به عنوان [مربی/کمک مربی] تکمیل شد!_
    لطفاً منتظر تأیید مدیر و لینک گروه باشید.
    ```
- اگر `تصحیح اطلاعات` انتخاب شود:
  - بازگشت به مرحله دریافت نام.

### مرحله ۸: دسترسی به گروه
- مدیر لینک گروه (مثال: `ble.ir/join/Gah9cS9LzQ`) را به مربی/کمک مربی ارسال می‌کند.
- مربی/کمک مربی با لینک وارد گروه شده و توسط مدیر به‌عنوان ادمین اضافه می‌شود.
- **پیام به مربی/کمک مربی**:
  ```
  _📍 روز حضور و غیاب به شما اعلام خواهد شد._
  لینک گروه: [ble.ir/join/Gah9cS9LzQ]
  ```

---

## ویژگی‌های اضافی
- **ورود مجدد**:
  - اگر کاربر (مدیر/مربی/کمک مربی) قبلاً ثبت‌نام کرده باشد، پیام خوش‌آمد با نام کوچک و اطلاعات حساب نمایش داده می‌شود.
  - مدیر به پنل کاربری هدایت می‌شود؛ مربی/کمک مربی به انتظار لینک گروه.
- **خطاها**:
  - نام نامعتبر: `_❌ نام فقط باید حروف فارسی داشته باشد._`
  - کد ملی نامعتبر: `_❌ کد ملی باید ۱۰ رقم باشد._`
  - شماره تلفن نامعتبر: `_❌ شماره تلفن باید با 989 شروع شود._`
  - کد تأیید نامعتبر: `_❌ کد نامعتبر است. دوباره وارد کنید._`
- **پاک‌سازی اطلاعات**: فقط حافظه موقت پاک می‌شود؛ فایل JSON دست‌نخورده می‌ماند.
- **اعلان‌ها**: پیام‌های مرتب و زیبا با ایموجی و فرمت ثابت:
  ```
  _[نام کوچک] عزیز،_
  نام شما: [نام کامل]
  کد ملی: [کد ملی یا هنوز مانده]
  تلفن: [تلفن یا هنوز مانده]
  ```