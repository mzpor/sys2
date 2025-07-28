 # ربات سلامت و ورزش
# HealthFitnessBot - برنامه ورزشی، رژیم غذایی، پیگیری سلامت
# توسعه‌دهنده: محمد زارع‌پور

import telebot
import json
import datetime
import sqlite3
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

# تنظیمات اولیه
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(BOT_TOKEN)

# دیتابیس
def init_database():
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            age INTEGER,
            gender TEXT,
            weight REAL,
            height REAL,
            activity_level TEXT DEFAULT 'moderate',
            fitness_goal TEXT,
            join_date TEXT
        )
    ''')
    
    # جدول برنامه‌های ورزشی
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_plans (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT,
            difficulty TEXT,
            duration INTEGER,
            description TEXT,
            exercises TEXT,
            calories_burn INTEGER,
            created_date TEXT
        )
    ''')
    
    # جدول تمرین‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            muscle_group TEXT,
            difficulty TEXT,
            description TEXT,
            instructions TEXT,
            video_url TEXT,
            image_url TEXT
        )
    ''')
    
    # جدول رژیم‌های غذایی
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_plans (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            goal TEXT,
            calories INTEGER,
            protein REAL,
            carbs REAL,
            fat REAL,
            description TEXT,
            meals TEXT,
            created_date TEXT
        )
    ''')
    
    # جدول پیگیری سلامت
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_tracking (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            date TEXT,
            weight REAL,
            steps INTEGER,
            calories_burned INTEGER,
            calories_consumed INTEGER,
            water_intake REAL,
            sleep_hours REAL,
            mood TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # جدول پیشرفت کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            workout_id INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            duration INTEGER,
            calories_burned INTEGER,
            completion_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (workout_id) REFERENCES workout_plans (id)
        )
    ''')
    
    # جدول اهداف ورزشی
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fitness_goals (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            goal_type TEXT,
            target_value REAL,
            current_value REAL,
            deadline TEXT,
            status TEXT DEFAULT 'active',
            created_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# برنامه‌های ورزشی نمونه
def insert_sample_workouts():
    workouts = [
        {
            "title": "تمرینات هوازی - مبتدی",
            "category": "هوازی",
            "difficulty": "مبتدی",
            "duration": 30,
            "description": "تمرینات هوازی مناسب برای مبتدیان",
            "exercises": "1. پیاده‌روی سریع (10 دقیقه)\n2. دویدن درجا (5 دقیقه)\n3. پرش پروانه (3 دقیقه)\n4. اسکوات (5 دقیقه)\n5. شنا (5 دقیقه)\n6. کشش (2 دقیقه)",
            "calories_burn": 200
        },
        {
            "title": "تمرینات قدرتی - بالاتنه",
            "category": "قدرتی",
            "difficulty": "متوسط",
            "duration": 45,
            "description": "تمرینات قدرتی برای تقویت عضلات بالاتنه",
            "exercises": "1. شنا (3 ست 10 تایی)\n2. پرس سینه (3 ست 12 تایی)\n3. پول‌آپ (3 ست 5 تایی)\n4. دیپ (3 ست 10 تایی)\n5. پلانک (3 ست 30 ثانیه)",
            "calories_burn": 300
        },
        {
            "title": "یوگا - آرامش",
            "category": "یوگا",
            "difficulty": "آسان",
            "duration": 20,
            "description": "تمرینات یوگا برای آرامش و انعطاف‌پذیری",
            "exercises": "1. وضعیت کودک (2 دقیقه)\n2. وضعیت گربه-گاو (3 دقیقه)\n3. وضعیت سگ رو به پایین (2 دقیقه)\n4. وضعیت جنگجو (3 دقیقه)\n5. مدیتیشن (10 دقیقه)",
            "calories_burn": 100
        }
    ]
    
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    
    for workout in workouts:
        cursor.execute('''
            INSERT OR IGNORE INTO workout_plans 
            (title, category, difficulty, duration, description, exercises, calories_burn, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (workout["title"], workout["category"], workout["difficulty"], workout["duration"],
              workout["description"], workout["exercises"], workout["calories_burn"],
              datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# رژیم‌های غذایی نمونه
def insert_sample_meal_plans():
    meal_plans = [
        {
            "title": "رژیم کاهش وزن",
            "goal": "کاهش وزن",
            "calories": 1500,
            "protein": 120,
            "carbs": 150,
            "fat": 50,
            "description": "رژیم متعادل برای کاهش وزن سالم",
            "meals": "صبحانه: جو دوسر + میوه\nناهار: سینه مرغ + سبزیجات\nشام: ماهی + برنج قهوه‌ای\nمیان‌وعده: آجیل + میوه"
        },
        {
            "title": "رژیم عضله‌سازی",
            "goal": "عضله‌سازی",
            "calories": 2500,
            "protein": 180,
            "carbs": 250,
            "fat": 80,
            "description": "رژیم پرپروتئین برای عضله‌سازی",
            "meals": "صبحانه: تخم‌مرغ + نان کامل\nناهار: گوشت + سیب‌زمینی\nشام: ماهی + کینوا\nمیان‌وعده: پروتئین شیک + موز"
        },
        {
            "title": "رژیم سالم",
            "goal": "حفظ وزن",
            "calories": 2000,
            "protein": 150,
            "carbs": 200,
            "fat": 65,
            "description": "رژیم متعادل برای حفظ سلامت",
            "meals": "صبحانه: نان کامل + پنیر\nناهار: مرغ + سالاد\nشام: ماهی + سبزیجات\nمیان‌وعده: میوه + آجیل"
        }
    ]
    
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    
    for meal_plan in meal_plans:
        cursor.execute('''
            INSERT OR IGNORE INTO meal_plans 
            (title, goal, calories, protein, carbs, fat, description, meals, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (meal_plan["title"], meal_plan["goal"], meal_plan["calories"], meal_plan["protein"],
              meal_plan["carbs"], meal_plan["fat"], meal_plan["description"], meal_plan["meals"],
              datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# مدیریت کاربران
def add_user(user_id, username, first_name):
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, join_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_info(user_id):
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_profile(user_id, age, gender, weight, height, activity_level, fitness_goal):
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET age = ?, gender = ?, weight = ?, height = ?, activity_level = ?, fitness_goal = ?
        WHERE user_id = ?
    ''', (age, gender, weight, height, activity_level, fitness_goal, user_id))
    conn.commit()
    conn.close()

# مدیریت برنامه‌های ورزشی
def get_workouts_by_category(category=None, difficulty=None):
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    
    if category and difficulty:
        cursor.execute('SELECT * FROM workout_plans WHERE category = ? AND difficulty = ?', (category, difficulty))
    elif category:
        cursor.execute('SELECT * FROM workout_plans WHERE category = ?', (category,))
    elif difficulty:
        cursor.execute('SELECT * FROM workout_plans WHERE difficulty = ?', (difficulty,))
    else:
        cursor.execute('SELECT * FROM workout_plans ORDER BY created_date DESC')
    
    workouts = cursor.fetchall()
    conn.close()
    return workouts

def get_workout_by_id(workout_id):
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM workout_plans WHERE id = ?', (workout_id,))
    workout = cursor.fetchone()
    conn.close()
    return workout

# مدیریت رژیم‌های غذایی
def get_meal_plans_by_goal(goal=None):
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    
    if goal:
        cursor.execute('SELECT * FROM meal_plans WHERE goal = ?', (goal,))
    else:
        cursor.execute('SELECT * FROM meal_plans ORDER BY created_date DESC')
    
    meal_plans = cursor.fetchall()
    conn.close()
    return meal_plans

def get_meal_plan_by_id(meal_plan_id):
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM meal_plans WHERE id = ?', (meal_plan_id,))
    meal_plan = cursor.fetchone()
    conn.close()
    return meal_plan

# مدیریت پیگیری سلامت
def add_health_tracking(user_id, weight, steps, calories_burned, calories_consumed, water_intake, sleep_hours, mood, notes):
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO health_tracking 
        (user_id, date, weight, steps, calories_burned, calories_consumed, water_intake, sleep_hours, mood, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, datetime.datetime.now().isoformat(), weight, steps, calories_burned, calories_consumed,
          water_intake, sleep_hours, mood, notes))
    conn.commit()
    conn.close()

def get_user_health_data(user_id, days=7):
    conn = sqlite3.connect('health_fitness.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM health_tracking 
        WHERE user_id = ? 
        ORDER BY date DESC 
        LIMIT ?
    ''', (user_id, days))
    health_data = cursor.fetchall()
    conn.close()
    return health_data

# محاسبه BMI
def calculate_bmi(weight, height):
    height_m = height / 100  # تبدیل سانتی‌متر به متر
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "کم‌وزن"
    elif bmi < 25:
        return "نرمال"
    elif bmi < 30:
        return "اضافه وزن"
    else:
        return "چاق"

# کلیدهای میانبر
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('💪 برنامه ورزشی', '🍎 رژیم غذایی')
    keyboard.row('📊 پیگیری سلامت', '🎯 اهداف ورزشی')
    keyboard.row('📈 پیشرفت من', '📖 راهنما')
    return keyboard

def create_workout_categories_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🏃 هوازی", callback_data="workout_cardio"),
        InlineKeyboardButton("💪 قدرتی", callback_data="workout_strength")
    )
    keyboard.row(
        InlineKeyboardButton("🧘 یوگا", callback_data="workout_yoga"),
        InlineKeyboardButton("🏊 شنا", callback_data="workout_swimming")
    )
    keyboard.row(
        InlineKeyboardButton("🚴 دوچرخه", callback_data="workout_cycling"),
        InlineKeyboardButton("🎯 همه برنامه‌ها", callback_data="workout_all")
    )
    return keyboard

def create_meal_goals_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📉 کاهش وزن", callback_data="meal_weight_loss"),
        InlineKeyboardButton("💪 عضله‌سازی", callback_data="meal_muscle_gain")
    )
    keyboard.row(
        InlineKeyboardButton("⚖️ حفظ وزن", callback_data="meal_maintenance"),
        InlineKeyboardButton("🏃 ورزشکار", callback_data="meal_athlete")
    )
    return keyboard

def create_workout_keyboard(workout_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📖 مشاهده برنامه", callback_data=f"view_workout_{workout_id}"),
        InlineKeyboardButton("🎥 ویدیو", callback_data=f"video_workout_{workout_id}")
    )
    keyboard.row(
        InlineKeyboardButton("✅ شروع تمرین", callback_data=f"start_workout_{workout_id}"),
        InlineKeyboardButton("📝 گزارش", callback_data=f"report_workout_{workout_id}")
    )
    return keyboard

# دستورات ربات
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    add_user(user_id, username, first_name)
    
    welcome_text = f"""
💪 سلام {first_name} عزیز!

به ربات سلامت و ورزش خوش آمدید! 🏃‍♂️

این ربات به شما کمک می‌کند تا:
• برنامه ورزشی مناسب دریافت کنید
• رژیم غذایی سالم داشته باشید
• سلامت خود را پیگیری کنید
• اهداف ورزشی تعیین کنید

🎯 ویژگی‌ها:
• برنامه‌های ورزشی متنوع
• رژیم‌های غذایی سالم
• پیگیری سلامت روزانه
• محاسبه BMI و کالری
• تعیین اهداف ورزشی

لطفاً ابتدا اطلاعات پروفایل خود را تکمیل کنید:
    """
    
    msg = bot.reply_to(message, welcome_text)
    bot.register_next_step_handler(msg, setup_profile)

def setup_profile(message):
    msg = bot.reply_to(message, "📏 سن خود را وارد کنید:")
    bot.register_next_step_handler(msg, process_age)

def process_age(message):
    try:
        age = int(message.text)
        msg = bot.reply_to(message, "👤 جنسیت خود را انتخاب کنید (مرد/زن):")
        bot.register_next_step_handler(msg, process_gender, age)
    except ValueError:
        bot.reply_to(message, "لطفاً عدد صحیح وارد کنید.")
        return

def process_gender(message, age):
    gender = message.text
    msg = bot.reply_to(message, "⚖️ وزن خود را به کیلوگرم وارد کنید:")
    bot.register_next_step_handler(msg, process_weight, age, gender)

def process_weight(message, age, gender):
    try:
        weight = float(message.text)
        msg = bot.reply_to(message, "📏 قد خود را به سانتی‌متر وارد کنید:")
        bot.register_next_step_handler(msg, process_height, age, gender, weight)
    except ValueError:
        bot.reply_to(message, "لطفاً عدد صحیح وارد کنید.")
        return

def process_height(message, age, gender, weight):
    try:
        height = float(message.text)
        msg = bot.reply_to(message, "🏃 سطح فعالیت خود را انتخاب کنید:\n1. کم تحرک\n2. متوسط\n3. پرتحرک")
        bot.register_next_step_handler(msg, process_activity, age, gender, weight, height)
    except ValueError:
        bot.reply_to(message, "لطفاً عدد صحیح وارد کنید.")
        return

def process_activity(message, age, gender, weight, height):
    activity_map = {"1": "low", "2": "moderate", "3": "high"}
    activity_level = activity_map.get(message.text, "moderate")
    
    msg = bot.reply_to(message, "🎯 هدف ورزشی خود را انتخاب کنید:\n1. کاهش وزن\n2. عضله‌سازی\n3. حفظ وزن\n4. افزایش استقامت")
    bot.register_next_step_handler(msg, process_goal, age, gender, weight, height, activity_level)

def process_goal(message, age, gender, weight, height, activity_level):
    goal_map = {"1": "کاهش وزن", "2": "عضله‌سازی", "3": "حفظ وزن", "4": "افزایش استقامت"}
    fitness_goal = goal_map.get(message.text, "حفظ وزن")
    
    user_id = message.from_user.id
    update_user_profile(user_id, age, gender, weight, height, activity_level, fitness_goal)
    
    # محاسبه BMI
    bmi = calculate_bmi(weight, height)
    bmi_category = get_bmi_category(bmi)
    
    success_text = f"""
✅ پروفایل شما با موفقیت تکمیل شد!

📊 اطلاعات شما:
👤 سن: {age} سال
👤 جنسیت: {gender}
⚖️ وزن: {weight} کیلوگرم
📏 قد: {height} سانتی‌متر
🏃 سطح فعالیت: {activity_level}
🎯 هدف: {fitness_goal}

📈 شاخص توده بدنی (BMI):
• مقدار: {bmi}
• وضعیت: {bmi_category}

حالا می‌توانید از امکانات ربات استفاده کنید!
    """
    
    bot.reply_to(message, success_text, reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '💪 برنامه ورزشی')
def workout_menu(message):
    workout_text = """
💪 برنامه‌های ورزشی

دسته‌بندی‌های موجود:

🏃 هوازی:
• دویدن
• پیاده‌روی
• دوچرخه‌سواری
• شنا

💪 قدرتی:
• تمرینات بالاتنه
• تمرینات پایین‌تنه
• تمرینات کل بدن
• تمرینات با وزنه

🧘 یوگا:
• یوگا برای مبتدیان
• یوگا برای انعطاف‌پذیری
• یوگا برای آرامش
• یوگا برای قدرت

لطفاً نوع تمرین مورد نظر را انتخاب کنید:
    """
    
    bot.reply_to(message, workout_text, reply_markup=create_workout_categories_keyboard())

@bot.message_handler(func=lambda message: message.text == '🍎 رژیم غذایی')
def meal_menu(message):
    meal_text = """
🍎 رژیم‌های غذایی

رژیم‌های موجود بر اساس هدف:

📉 کاهش وزن:
• رژیم کم کالری
• رژیم متعادل
• رژیم پروتئین بالا

💪 عضله‌سازی:
• رژیم پرپروتئین
• رژیم کربوهیدرات بالا
• رژیم افزایش وزن

⚖️ حفظ وزن:
• رژیم متعادل
• رژیم سالم
• رژیم گیاهی

🏃 ورزشکار:
• رژیم قبل از تمرین
• رژیم بعد از تمرین
• رژیم مسابقه

لطفاً هدف خود را انتخاب کنید:
    """
    
    bot.reply_to(message, meal_text, reply_markup=create_meal_goals_keyboard())

@bot.message_handler(func=lambda message: message.text == '📊 پیگیری سلامت')
def health_tracking_menu(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    if not user_info or not user_info[4]:  # اگر سن ثبت نشده
        bot.reply_to(message, "لطفاً ابتدا پروفایل خود را تکمیل کنید.")
        return
    
    tracking_text = """
📊 پیگیری سلامت

برای ثبت اطلاعات روزانه، لطفاً موارد زیر را وارد کنید:

📏 وزن امروز (کیلوگرم):
    """
    
    msg = bot.reply_to(message, tracking_text)
    bot.register_next_step_handler(msg, process_daily_weight)

def process_daily_weight(message):
    try:
        weight = float(message.text)
        msg = bot.reply_to(message, "👟 تعداد قدم‌های امروز:")
        bot.register_next_step_handler(msg, process_daily_steps, weight)
    except ValueError:
        bot.reply_to(message, "لطفاً عدد صحیح وارد کنید.")
        return

def process_daily_steps(message, weight):
    try:
        steps = int(message.text)
        msg = bot.reply_to(message, "🔥 کالری سوزانده شده امروز:")
        bot.register_next_step_handler(msg, process_daily_calories_burned, weight, steps)
    except ValueError:
        bot.reply_to(message, "لطفاً عدد صحیح وارد کنید.")
        return

def process_daily_calories_burned(message, weight, steps):
    try:
        calories_burned = int(message.text)
        msg = bot.reply_to(message, "🍎 کالری مصرف شده امروز:")
        bot.register_next_step_handler(msg, process_daily_calories_consumed, weight, steps, calories_burned)
    except ValueError:
        bot.reply_to(message, "لطفاً عدد صحیح وارد کنید.")
        return

def process_daily_calories_consumed(message, weight, steps, calories_burned):
    try:
        calories_consumed = int(message.text)
        msg = bot.reply_to(message, "💧 مصرف آب امروز (لیتر):")
        bot.register_next_step_handler(msg, process_daily_water, weight, steps, calories_burned, calories_consumed)
    except ValueError:
        bot.reply_to(message, "لطفاً عدد صحیح وارد کنید.")
        return

def process_daily_water(message, weight, steps, calories_burned, calories_consumed):
    try:
        water_intake = float(message.text)
        msg = bot.reply_to(message, "😴 ساعت خواب دیشب:")
        bot.register_next_step_handler(msg, process_daily_sleep, weight, steps, calories_burned, calories_consumed, water_intake)
    except ValueError:
        bot.reply_to(message, "لطفاً عدد صحیح وارد کنید.")
        return

def process_daily_sleep(message, weight, steps, calories_burned, calories_consumed, water_intake):
    try:
        sleep_hours = float(message.text)
        msg = bot.reply_to(message, "😊 روحیه امروز (عالی/خوب/متوسط/بد):")
        bot.register_next_step_handler(msg, process_daily_mood, weight, steps, calories_burned, calories_consumed, water_intake, sleep_hours)
    except ValueError:
        bot.reply_to(message, "لطفاً عدد صحیح وارد کنید.")
        return

def process_daily_mood(message, weight, steps, calories_burned, calories_consumed, water_intake, sleep_hours):
    mood = message.text
    msg = bot.reply_to(message, "📝 یادداشت (اختیاری):")
    bot.register_next_step_handler(msg, save_daily_data, weight, steps, calories_burned, calories_consumed, water_intake, sleep_hours, mood)

def save_daily_data(message, weight, steps, calories_burned, calories_consumed, water_intake, sleep_hours, mood):
    notes = message.text
    user_id = message.from_user.id
    
    add_health_tracking(user_id, weight, steps, calories_burned, calories_consumed, water_intake, sleep_hours, mood, notes)
    
    success_text = f"""
✅ اطلاعات روزانه شما ثبت شد!

📊 خلاصه امروز:
⚖️ وزن: {weight} کیلوگرم
👟 قدم‌ها: {steps} قدم
🔥 کالری سوزانده: {calories_burned} کالری
🍎 کالری مصرف شده: {calories_consumed} کالری
💧 آب: {water_intake} لیتر
😴 خواب: {sleep_hours} ساعت
😊 روحیه: {mood}

📈 پیشرفت شما در حال پیگیری است!
    """
    
    bot.reply_to(message, success_text)

@bot.message_handler(func=lambda message: message.text == '🎯 اهداف ورزشی')
def fitness_goals_menu(message):
    goals_text = """
🎯 اهداف ورزشی

اهداف قابل تعیین:

📉 کاهش وزن:
• کاهش 5 کیلوگرم در 3 ماه
• کاهش 10 کیلوگرم در 6 ماه
• رسیدن به وزن ایده‌آل

💪 عضله‌سازی:
• افزایش 5 کیلوگرم عضله
• تقویت عضلات بالاتنه
• افزایش قدرت کلی

🏃 افزایش استقامت:
• دویدن 5 کیلومتر
• دوچرخه‌سواری 20 کیلومتر
• شنا 1 کیلومتر

⚖️ حفظ وزن:
• حفظ وزن فعلی
• بهبود ترکیب بدنی
• افزایش انرژی

لطفاً نوع هدف خود را انتخاب کنید:
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📉 کاهش وزن", callback_data="goal_weight_loss"),
        InlineKeyboardButton("💪 عضله‌سازی", callback_data="goal_muscle_gain")
    )
    keyboard.row(
        InlineKeyboardButton("🏃 افزایش استقامت", callback_data="goal_endurance"),
        InlineKeyboardButton("⚖️ حفظ وزن", callback_data="goal_maintenance")
    )
    
    bot.reply_to(message, goals_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📈 پیشرفت من')
def my_progress(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    if not user_info:
        bot.reply_to(message, "اطلاعات شما یافت نشد.")
        return
    
    health_data = get_user_health_data(user_id, 7)
    
    progress_text = f"""
📈 پیشرفت شما:

👤 نام: {user_info[3]}
📅 تاریخ عضویت: {user_info[10][:10]}
⚖️ وزن فعلی: {user_info[6] or 'ثبت نشده'} کیلوگرم
📏 قد: {user_info[7] or 'ثبت نشده'} سانتی‌متر
🎯 هدف: {user_info[9] or 'تعیین نشده'}

📊 آمار هفته گذشته:
    """
    
    if health_data:
        total_steps = sum(data[4] for data in health_data if data[4])
        total_calories_burned = sum(data[5] for data in health_data if data[5])
        avg_weight = sum(data[3] for data in health_data if data[3]) / len(health_data)
        
        progress_text += f"👟 کل قدم‌ها: {total_steps:,} قدم\n"
        progress_text += f"🔥 کل کالری سوزانده: {total_calories_burned} کالری\n"
        progress_text += f"⚖️ میانگین وزن: {avg_weight:.1f} کیلوگرم\n"
    else:
        progress_text += "هنوز اطلاعاتی ثبت نشده است.\n"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📊 نمودار پیشرفت", callback_data="progress_chart"),
        InlineKeyboardButton("📋 گزارش تفصیلی", callback_data="detailed_report")
    )
    keyboard.row(
        InlineKeyboardButton("🎯 تعیین هدف جدید", callback_data="set_new_goal"),
        InlineKeyboardButton("📈 آمار کلی", callback_data="overall_stats")
    )
    
    bot.reply_to(message, progress_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📖 راهنما')
def help_command(message):
    help_text = """
📖 راهنمای ربات سلامت و ورزش

💪 برنامه ورزشی:
• انتخاب نوع تمرین
• دریافت برنامه مناسب
• پیگیری پیشرفت
• گزارش تمرینات

🍎 رژیم غذایی:
• انتخاب رژیم مناسب
• محاسبه کالری
• برنامه غذایی
• مشاوره تغذیه

📊 پیگیری سلامت:
• ثبت وزن روزانه
• شمارش قدم‌ها
• محاسبه کالری
• پیگیری خواب و روحیه

🎯 اهداف ورزشی:
• تعیین هدف
• پیگیری پیشرفت
• دریافت بازخورد
• جشن موفقیت

📈 پیشرفت من:
• مشاهده آمار
• نمودار پیشرفت
• گزارش تفصیلی
• مقایسه با گذشته

💡 نکات مهم:
• هر روز ورزش کنید
• رژیم متعادل داشته باشید
• آب کافی بنوشید
• خواب کافی داشته باشید

📞 پشتیبانی:
برای سوالات بیشتر با پشتیبانی تماس بگیرید.
    """
    
    bot.reply_to(message, help_text)

# مدیریت callback ها
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("workout_"):
        category = call.data.split("_")[1]
        workouts = get_workouts_by_category(category)
        
        if not workouts:
            bot.answer_callback_query(call.id, "هیچ برنامه‌ای در این دسته‌بندی موجود نیست")
            return
        
        workouts_text = f"💪 برنامه‌های ورزشی {category}:\n\n"
        
        for i, workout in enumerate(workouts, 1):
            difficulty_emoji = "🟢" if workout[3] == "مبتدی" else "🟡" if workout[3] == "متوسط" else "🔴"
            workouts_text += f"{i}. {difficulty_emoji} {workout[1]}\n"
            workouts_text += f"   ⏰ مدت: {workout[4]} دقیقه\n"
            workouts_text += f"   🔥 کالری: {workout[7]} کالری\n\n"
        
        keyboard = InlineKeyboardMarkup()
        for i, workout in enumerate(workouts[:5], 1):
            keyboard.row(InlineKeyboardButton(f"{i}. {workout[1]}", callback_data=f"workout_{workout[0]}"))
        
        bot.edit_message_text(workouts_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)

# راه‌اندازی ربات
if __name__ == "__main__":
    init_database()
    insert_sample_workouts()
    insert_sample_meal_plans()
    print("💪 ربات سلامت و ورزش راه‌اندازی شد!")
    print("🏃‍♂️ آماده برای برنامه‌ریزی ورزشی...")
    bot.polling(none_stop=True)