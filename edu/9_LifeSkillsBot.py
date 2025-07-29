 # ربات مهارت‌های زندگی
# LifeSkillsBot - آموزش مهارت‌های عملی زندگی
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
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            age_group TEXT DEFAULT 'teen',
            join_date TEXT,
            completed_skills INTEGER DEFAULT 0,
            total_points INTEGER DEFAULT 0
        )
    ''')
    
    # جدول مهارت‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT,
            difficulty TEXT,
            description TEXT,
            learning_objectives TEXT,
            practical_exercises TEXT,
            assessment_criteria TEXT,
            duration INTEGER,
            created_date TEXT
        )
    ''')
    
    # جدول پیشرفت کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            skill_id INTEGER,
            status TEXT DEFAULT 'not_started',
            progress_percentage INTEGER DEFAULT 0,
            assessment_score INTEGER DEFAULT 0,
            completion_date TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (skill_id) REFERENCES skills (id)
        )
    ''')
    
    # جدول ارزیابی‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY,
            skill_id INTEGER,
            user_id INTEGER,
            questions TEXT,
            answers TEXT,
            score INTEGER,
            assessment_date TEXT,
            FOREIGN KEY (skill_id) REFERENCES skills (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # جدول چالش‌های عملی
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS practical_challenges (
            id INTEGER PRIMARY KEY,
            skill_id INTEGER,
            title TEXT,
            description TEXT,
            difficulty TEXT,
            duration INTEGER,
            materials_needed TEXT,
            instructions TEXT,
            created_date TEXT,
            FOREIGN KEY (skill_id) REFERENCES skills (id)
        )
    ''')
    
    # جدول گواهی‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            skill_id INTEGER,
            certificate_number TEXT,
            issue_date TEXT,
            expiry_date TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (skill_id) REFERENCES skills (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# مهارت‌های نمونه
def insert_sample_skills():
    skills = [
        {
            "title": "مدیریت مالی شخصی",
            "category": "مالی",
            "difficulty": "متوسط",
            "description": "یادگیری مدیریت درآمد، هزینه‌ها و پس‌انداز",
            "learning_objectives": "• بودجه‌بندی ماهانه\n• کنترل هزینه‌ها\n• پس‌انداز هوشمند\n• سرمایه‌گذاری اولیه",
            "practical_exercises": "• تهیه بودجه ماهانه\n• ثبت هزینه‌های روزانه\n• برنامه پس‌انداز\n• تحقیق در مورد سرمایه‌گذاری",
            "assessment_criteria": "• توانایی بودجه‌بندی\n• کنترل هزینه‌ها\n• پس‌انداز منظم\n• آگاهی مالی",
            "duration": 30
        },
        {
            "title": "مهارت‌های ارتباطی",
            "category": "ارتباطات",
            "difficulty": "متوسط",
            "description": "تقویت مهارت‌های گفتاری و شنیداری",
            "learning_objectives": "• گوش دادن فعال\n• صحبت مؤثر\n• حل تعارض\n• کار گروهی",
            "practical_exercises": "• تمرین گوش دادن\n• سخنرانی کوتاه\n• مذاکره\n• کار تیمی",
            "assessment_criteria": "• کیفیت گوش دادن\n• وضوح بیان\n• حل مسئله\n• همکاری",
            "duration": 25
        },
        {
            "title": "مدیریت زمان",
            "category": "مدیریت",
            "difficulty": "آسان",
            "description": "یادگیری برنامه‌ریزی و اولویت‌بندی کارها",
            "learning_objectives": "• برنامه‌ریزی روزانه\n• اولویت‌بندی کارها\n• مدیریت مهلت‌ها\n• تعادل کار و زندگی",
            "practical_exercises": "• تهیه برنامه روزانه\n• لیست کارها\n• مدیریت زمان مطالعه\n• برنامه‌ریزی هفتگی",
            "assessment_criteria": "• رعایت برنامه\n• تکمیل کارها\n• مدیریت مهلت‌ها\n• تعادل زمانی",
            "duration": 20
        },
        {
            "title": "مهارت‌های آشپزی",
            "category": "زندگی روزمره",
            "difficulty": "آسان",
            "description": "یادگیری پخت غذاهای ساده و سالم",
            "learning_objectives": "• پخت غذاهای ساده\n• رعایت بهداشت\n• برنامه‌ریزی غذایی\n• صرفه‌جویی",
            "practical_exercises": "• پخت صبحانه سالم\n• تهیه ناهار ساده\n• پخت شام\n• نگهداری مواد غذایی",
            "assessment_criteria": "• کیفیت غذا\n• رعایت بهداشت\n• برنامه‌ریزی\n• صرفه‌جویی",
            "duration": 35
        },
        {
            "title": "مهارت‌های رایانه",
            "category": "تکنولوژی",
            "difficulty": "متوسط",
            "description": "یادگیری استفاده از رایانه و اینترنت",
            "learning_objectives": "• کار با نرم‌افزارهای اصلی\n• جستجو در اینترنت\n• ایمیل و ارتباطات\n• امنیت دیجیتال",
            "practical_exercises": "• کار با Word\n• جستجوی اطلاعات\n• ارسال ایمیل\n• تنظیمات امنیتی",
            "assessment_criteria": "• مهارت نرم‌افزاری\n• جستجوی مؤثر\n• ارتباط دیجیتال\n• امنیت",
            "duration": 40
        }
    ]
    
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    
    for skill in skills:
        cursor.execute('''
            INSERT OR IGNORE INTO skills 
            (title, category, difficulty, description, learning_objectives, practical_exercises, assessment_criteria, duration, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (skill["title"], skill["category"], skill["difficulty"], skill["description"],
              skill["learning_objectives"], skill["practical_exercises"], skill["assessment_criteria"],
              skill["duration"], datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# چالش‌های عملی نمونه
def insert_sample_challenges():
    challenges = [
        {
            "skill_id": 1,
            "title": "بودجه‌بندی یک ماه",
            "description": "تهیه و اجرای بودجه ماهانه شخصی",
            "difficulty": "متوسط",
            "duration": 30,
            "materials_needed": "دفترچه، ماشین حساب، اپلیکیشن بودجه",
            "instructions": "1. درآمد ماهانه را ثبت کنید\n2. هزینه‌های ثابت را لیست کنید\n3. بودجه متغیر تعیین کنید\n4. هزینه‌ها را پیگیری کنید"
        },
        {
            "skill_id": 2,
            "title": "گفتگو با غریبه",
            "description": "شروع گفتگو با افراد جدید",
            "difficulty": "آسان",
            "duration": 15,
            "materials_needed": "موضوعات گفتگو، اعتماد به نفس",
            "instructions": "1. موضوع مناسب انتخاب کنید\n2. با سلام شروع کنید\n3. سوالات باز بپرسید\n4. گوش دهید و پاسخ دهید"
        },
        {
            "skill_id": 3,
            "title": "برنامه‌ریزی هفتگی",
            "description": "تهیه برنامه کامل هفتگی",
            "difficulty": "آسان",
            "duration": 7,
            "materials_needed": "تقویم، دفترچه، تایمر",
            "instructions": "1. کارهای هفته را لیست کنید\n2. اولویت‌بندی کنید\n3. زمان‌بندی کنید\n4. اجرا و پیگیری کنید"
        }
    ]
    
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    
    for challenge in challenges:
        cursor.execute('''
            INSERT OR IGNORE INTO practical_challenges 
            (skill_id, title, description, difficulty, duration, materials_needed, instructions, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (challenge["skill_id"], challenge["title"], challenge["description"], challenge["difficulty"],
              challenge["duration"], challenge["materials_needed"], challenge["instructions"],
              datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# مدیریت کاربران
def add_user(user_id, username, first_name):
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, join_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_info(user_id):
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_progress(user_id, skill_id, progress_percentage, assessment_score=None):
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    
    # بررسی پیشرفت موجود
    cursor.execute('SELECT id FROM user_progress WHERE user_id = ? AND skill_id = ?', (user_id, skill_id))
    existing = cursor.fetchone()
    
    if existing:
        # به‌روزرسانی پیشرفت موجود
        cursor.execute('''
            UPDATE user_progress 
            SET progress_percentage = ?, assessment_score = ?, completion_date = ?
            WHERE user_id = ? AND skill_id = ?
        ''', (progress_percentage, assessment_score, datetime.datetime.now().isoformat(), user_id, skill_id))
    else:
        # ثبت پیشرفت جدید
        cursor.execute('''
            INSERT INTO user_progress (user_id, skill_id, progress_percentage, assessment_score, completion_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, skill_id, progress_percentage, assessment_score, datetime.datetime.now().isoformat()))
    
    # به‌روزرسانی آمار کاربر
    if progress_percentage == 100:
        cursor.execute('UPDATE users SET completed_skills = completed_skills + 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()

# مدیریت مهارت‌ها
def get_skills_by_category(category=None):
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    
    if category:
        cursor.execute('SELECT * FROM skills WHERE category = ? ORDER BY difficulty', (category,))
    else:
        cursor.execute('SELECT * FROM skills ORDER BY category, difficulty')
    
    skills = cursor.fetchall()
    conn.close()
    return skills

def get_skill_by_id(skill_id):
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM skills WHERE id = ?', (skill_id,))
    skill = cursor.fetchone()
    conn.close()
    return skill

def get_user_skill_progress(user_id, skill_id):
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_progress WHERE user_id = ? AND skill_id = ?', (user_id, skill_id))
    progress = cursor.fetchone()
    conn.close()
    return progress

# مدیریت ارزیابی‌ها
def create_assessment(skill_id, user_id, questions, answers, score):
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO assessments (skill_id, user_id, questions, answers, score, assessment_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (skill_id, user_id, questions, answers, score, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_assessments(user_id):
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, s.title as skill_title
        FROM assessments a
        JOIN skills s ON a.skill_id = s.id
        WHERE a.user_id = ?
        ORDER BY a.assessment_date DESC
    ''', (user_id,))
    assessments = cursor.fetchall()
    conn.close()
    return assessments

# مدیریت چالش‌ها
def get_skill_challenges(skill_id):
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM practical_challenges WHERE skill_id = ?', (skill_id,))
    challenges = cursor.fetchall()
    conn.close()
    return challenges

# کلیدهای میانبر
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('📚 مهارت‌های زندگی', '🎯 چالش‌های عملی')
    keyboard.row('📊 ارزیابی مهارت‌ها', '🏆 گواهی‌ها')
    keyboard.row('📈 پیشرفت من', '📖 راهنما')
    return keyboard

def create_skills_categories_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("💰 مالی", callback_data="category_financial"),
        InlineKeyboardButton("💬 ارتباطات", callback_data="category_communication")
    )
    keyboard.row(
        InlineKeyboardButton("⏰ مدیریت", callback_data="category_management"),
        InlineKeyboardButton("🏠 زندگی روزمره", callback_data="category_daily")
    )
    keyboard.row(
        InlineKeyboardButton("💻 تکنولوژی", callback_data="category_technology"),
        InlineKeyboardButton("🎯 همه مهارت‌ها", callback_data="category_all")
    )
    return keyboard

def create_skill_keyboard(skill_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📖 مطالعه", callback_data=f"study_skill_{skill_id}"),
        InlineKeyboardButton("🎯 تمرین", callback_data=f"practice_skill_{skill_id}")
    )
    keyboard.row(
        InlineKeyboardButton("📝 ارزیابی", callback_data=f"assess_skill_{skill_id}"),
        InlineKeyboardButton("🏆 گواهی", callback_data=f"certificate_skill_{skill_id}")
    )
    return keyboard

def create_challenge_keyboard(challenge_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🎯 شروع چالش", callback_data=f"start_challenge_{challenge_id}"),
        InlineKeyboardButton("📝 گزارش", callback_data=f"report_challenge_{challenge_id}")
    )
    keyboard.row(
        InlineKeyboardButton("✅ تکمیل", callback_data=f"complete_challenge_{challenge_id}")
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
🎯 سلام {first_name} عزیز!

به ربات مهارت‌های زندگی خوش آمدید! 🌟

این ربات به شما کمک می‌کند تا:
• مهارت‌های عملی زندگی را یاد بگیرید
• چالش‌های واقعی را تجربه کنید
• پیشرفت خود را ارزیابی کنید
• گواهی مهارت دریافت کنید

🎯 مهارت‌های موجود:
• مدیریت مالی شخصی
• مهارت‌های ارتباطی
• مدیریت زمان
• مهارت‌های آشپزی
• مهارت‌های رایانه

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    bot.reply_to(message, welcome_text, reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '📚 مهارت‌های زندگی')
def skills_menu(message):
    skills_text = """
📚 مهارت‌های زندگی

دسته‌بندی‌های مهارت‌ها:

💰 مهارت‌های مالی:
• مدیریت بودجه
• پس‌انداز هوشمند
• سرمایه‌گذاری اولیه

💬 مهارت‌های ارتباطی:
• گوش دادن فعال
• صحبت مؤثر
• حل تعارض

⏰ مهارت‌های مدیریتی:
• مدیریت زمان
• برنامه‌ریزی
• اولویت‌بندی

🏠 مهارت‌های زندگی روزمره:
• آشپزی
• نظافت
• نگهداری خانه

💻 مهارت‌های تکنولوژی:
• کار با رایانه
• اینترنت و ایمیل
• امنیت دیجیتال

لطفاً دسته‌بندی مورد نظر را انتخاب کنید:
    """
    
    bot.reply_to(message, skills_text, reply_markup=create_skills_categories_keyboard())

@bot.message_handler(func=lambda message: message.text == '🎯 چالش‌های عملی')
def challenges_menu(message):
    challenges_text = """
🎯 چالش‌های عملی

چالش‌های موجود برای تمرین مهارت‌ها:

💰 مالی:
• بودجه‌بندی یک ماه
• پس‌انداز هدفمند
• کنترل هزینه‌ها

💬 ارتباطات:
• گفتگو با غریبه
• سخنرانی کوتاه
• حل تعارض

⏰ مدیریت:
• برنامه‌ریزی هفتگی
• مدیریت مهلت‌ها
• تعادل کار و زندگی

🏠 زندگی روزمره:
• پخت غذاهای ساده
• نظافت منظم
• نگهداری لوازم

لطفاً نوع چالش مورد نظر را انتخاب کنید:
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("💰 مالی", callback_data="challenge_financial"),
        InlineKeyboardButton("💬 ارتباطات", callback_data="challenge_communication")
    )
    keyboard.row(
        InlineKeyboardButton("⏰ مدیریت", callback_data="challenge_management"),
        InlineKeyboardButton("🏠 زندگی روزمره", callback_data="challenge_daily")
    )
    keyboard.row(
        InlineKeyboardButton("🎲 چالش تصادفی", callback_data="challenge_random")
    )
    
    bot.reply_to(message, challenges_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📊 ارزیابی مهارت‌ها')
def assessment_menu(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    assessment_text = """
📊 ارزیابی مهارت‌ها

برای ارزیابی مهارت‌های خود، لطفاً مهارت مورد نظر را انتخاب کنید:

📋 مراحل ارزیابی:
1. انتخاب مهارت
2. پاسخ به سوالات
3. دریافت نمره
4. دریافت گواهی

🎯 مهارت‌های قابل ارزیابی:
• مدیریت مالی شخصی
• مهارت‌های ارتباطی
• مدیریت زمان
• مهارت‌های آشپزی
• مهارت‌های رایانه

لطفاً مهارت مورد نظر را انتخاب کنید:
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("💰 مدیریت مالی", callback_data="assess_financial"),
        InlineKeyboardButton("💬 ارتباطات", callback_data="assess_communication")
    )
    keyboard.row(
        InlineKeyboardButton("⏰ مدیریت زمان", callback_data="assess_time"),
        InlineKeyboardButton("🍳 آشپزی", callback_data="assess_cooking")
    )
    keyboard.row(
        InlineKeyboardButton("💻 رایانه", callback_data="assess_computer")
    )
    
    bot.reply_to(message, assessment_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '🏆 گواهی‌ها')
def certificates_menu(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    certificates_text = """
🏆 گواهی‌های مهارت

گواهی‌های موجود:

📜 گواهی مدیریت مالی:
• بودجه‌بندی ماهانه
• کنترل هزینه‌ها
• پس‌انداز هوشمند

📜 گواهی ارتباطات:
• گوش دادن فعال
• صحبت مؤثر
• حل تعارض

📜 گواهی مدیریت زمان:
• برنامه‌ریزی روزانه
• اولویت‌بندی کارها
• مدیریت مهلت‌ها

📜 گواهی مهارت‌های زندگی:
• آشپزی ساده
• نظافت منظم
• نگهداری خانه

برای دریافت گواهی، ابتدا مهارت را کامل کنید و سپس ارزیابی انجام دهید.
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📜 گواهی‌های من", callback_data="my_certificates"),
        InlineKeyboardButton("🏆 درخواست گواهی", callback_data="request_certificate")
    )
    keyboard.row(
        InlineKeyboardButton("📋 شرایط گواهی", callback_data="certificate_requirements")
    )
    
    bot.reply_to(message, certificates_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📈 پیشرفت من')
def my_progress(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    if not user_info:
        bot.reply_to(message, "اطلاعات شما یافت نشد.")
        return
    
    # دریافت پیشرفت کاربر
    conn = sqlite3.connect('life_skills.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.title, up.progress_percentage, up.assessment_score
        FROM user_progress up
        JOIN skills s ON up.skill_id = s.id
        WHERE up.user_id = ?
        ORDER BY up.completion_date DESC
    ''', (user_id,))
    progress_data = cursor.fetchall()
    conn.close()
    
    progress_text = f"""
📈 پیشرفت شما:

👤 نام: {user_info[3]}
📅 تاریخ عضویت: {user_info[5][:10]}
✅ مهارت‌های تکمیل شده: {user_info[6]}
🏆 امتیاز کل: {user_info[7]}

📊 آمار پیشرفت:
    """
    
    if progress_data:
        for skill_title, progress, score in progress_data:
            progress_text += f"• {skill_title}: {progress}%"
            if score:
                progress_text += f" (نمره: {score})"
            progress_text += "\n"
    else:
        progress_text += "هنوز هیچ مهارتی شروع نکرده‌اید."
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📊 نمودار پیشرفت", callback_data="progress_chart"),
        InlineKeyboardButton("📋 گزارش تفصیلی", callback_data="detailed_report")
    )
    keyboard.row(
        InlineKeyboardButton("🎯 هدف‌گذاری", callback_data="set_goals"),
        InlineKeyboardButton("📈 آمار کلی", callback_data="overall_stats")
    )
    
    bot.reply_to(message, progress_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📖 راهنما')
def help_command(message):
    help_text = """
📖 راهنمای ربات مهارت‌های زندگی

📚 مهارت‌های زندگی:
• انتخاب مهارت مورد علاقه
• مطالعه محتوای آموزشی
• انجام تمرین‌های عملی
• ارزیابی مهارت‌ها

🎯 چالش‌های عملی:
• شرکت در چالش‌های واقعی
• تمرین مهارت‌ها در زندگی
• گزارش پیشرفت
• دریافت بازخورد

📊 ارزیابی مهارت‌ها:
• پاسخ به سوالات ارزیابی
• دریافت نمره و بازخورد
• شناسایی نقاط قوت و ضعف
• برنامه بهبود

🏆 گواهی‌ها:
• دریافت گواهی مهارت
• نمایش دستاوردها
• افزایش اعتماد به نفس
• بهبود رزومه

📈 پیشرفت من:
• پیگیری پیشرفت
• مشاهده آمار
• هدف‌گذاری
• برنامه بهبود

💡 نکات مهم:
• هر روز تمرین کنید
• چالش‌ها را جدی بگیرید
• از بازخورد استفاده کنید
• مهارت‌ها را در زندگی به کار ببرید

📞 پشتیبانی:
برای سوالات بیشتر با پشتیبانی تماس بگیرید.
    """
    
    bot.reply_to(message, help_text)

# مدیریت callback ها
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("category_"):
        category = call.data.split("_")[1]
        skills = get_skills_by_category(category)
        
        if not skills:
            bot.answer_callback_query(call.id, "هیچ مهارتی در این دسته‌بندی موجود نیست")
            return
        
        skills_text = f"📚 مهارت‌های {category}:\n\n"
        
        for i, skill in enumerate(skills, 1):
            difficulty_emoji = "🟢" if skill[3] == "آسان" else "🟡" if skill[3] == "متوسط" else "🔴"
            skills_text += f"{i}. {difficulty_emoji} {skill[1]}\n"
            skills_text += f"   📝 {skill[4][:50]}...\n"
            skills_text += f"   ⏰ مدت: {skill[8]} روز\n\n"
        
        keyboard = InlineKeyboardMarkup()
        for i, skill in enumerate(skills[:5], 1):
            keyboard.row(InlineKeyboardButton(f"{i}. {skill[1]}", callback_data=f"skill_{skill[0]}"))
        
        bot.edit_message_text(skills_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
    
    elif call.data.startswith("skill_"):
        skill_id = int(call.data.split("_")[1])
        skill = get_skill_by_id(skill_id)
        
        if not skill:
            bot.answer_callback_query(call.id, "مهارت یافت نشد")
            return
        
        skill_text = f"""
📚 {skill[1]}

📝 توضیحات:
{skill[4]}

🎯 اهداف یادگیری:
{skill[5]}

📋 تمرین‌های عملی:
{skill[6]}

📊 معیارهای ارزیابی:
{skill[7]}

⏰ مدت: {skill[8]} روز
🎯 سطح: {skill[3]}
📂 دسته‌بندی: {skill[2]}
        """
        
        bot.edit_message_text(skill_text, call.message.chat.id, call.message.message_id,
                             reply_markup=create_skill_keyboard(skill_id))

# راه‌اندازی ربات
if __name__ == "__main__":
    init_database()
    insert_sample_skills()
    insert_sample_challenges()
    print("🎯 ربات مهارت‌های زندگی راه‌اندازی شد!")
    print("🌟 آماده برای آموزش مهارت‌های عملی...")
    bot.polling(none_stop=True)