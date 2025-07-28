 # ربات خلاقیت و هنر
# CreativeArtBot - آموزش هنر، نقاشی، موسیقی
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
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            art_level TEXT DEFAULT 'beginner',
            join_date TEXT,
            total_artworks INTEGER DEFAULT 0,
            total_points INTEGER DEFAULT 0
        )
    ''')
    
    # جدول درس‌های هنری
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS art_lessons (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT,
            difficulty TEXT,
            description TEXT,
            materials TEXT,
            steps TEXT,
            video_url TEXT,
            image_url TEXT,
            created_date TEXT
        )
    ''')
    
    # جدول آثار هنری
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artworks (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            category TEXT,
            file_id TEXT,
            file_type TEXT,
            likes INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            created_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # جدول مسابقات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            start_date TEXT,
            end_date TEXT,
            prize TEXT,
            status TEXT DEFAULT 'active',
            created_date TEXT
        )
    ''')
    
    # جدول شرکت‌کنندگان مسابقه
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS competition_entries (
            id INTEGER PRIMARY KEY,
            competition_id INTEGER,
            user_id INTEGER,
            artwork_id INTEGER,
            score REAL DEFAULT 0,
            rank INTEGER,
            submission_date TEXT,
            FOREIGN KEY (competition_id) REFERENCES competitions (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (artwork_id) REFERENCES artworks (id)
        )
    ''')
    
    # جدول تمرین‌های خلاقیت
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS creative_exercises (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT,
            description TEXT,
            instructions TEXT,
            duration INTEGER,
            difficulty TEXT,
            materials_needed TEXT,
            created_date TEXT
        )
    ''')
    
    # جدول پیشرفت کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            lesson_id INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            score INTEGER DEFAULT 0,
            completion_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_id) REFERENCES art_lessons (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# درس‌های هنری نمونه
def insert_sample_lessons():
    lessons = [
        {
            "title": "نقاشی با آبرنگ - تکنیک‌های پایه",
            "category": "نقاشی",
            "difficulty": "مبتدی",
            "description": "یادگیری تکنیک‌های پایه نقاشی با آبرنگ",
            "materials": "کاغذ آبرنگ، قلم مو، رنگ آبرنگ، پالت",
            "steps": "1. آماده‌سازی مواد\n2. تمرین ضربه‌های قلم مو\n3. ترکیب رنگ‌ها\n4. نقاشی منظره ساده",
            "video_url": "https://example.com/watercolor_basics",
            "image_url": "https://example.com/watercolor_sample.jpg"
        },
        {
            "title": "طراحی چهره - تناسبات",
            "category": "طراحی",
            "difficulty": "متوسط",
            "description": "یادگیری تناسبات صحیح در طراحی چهره",
            "materials": "کاغذ طراحی، مداد، پاک‌کن",
            "steps": "1. ترسیم بیضی سر\n2. تقسیم‌بندی چهره\n3. رسم چشم‌ها\n4. رسم بینی و دهان",
            "video_url": "https://example.com/face_proportions",
            "image_url": "https://example.com/face_sample.jpg"
        },
        {
            "title": "خوشنویسی - حروف الفبا",
            "category": "خوشنویسی",
            "difficulty": "مبتدی",
            "description": "یادگیری اصول خوشنویسی فارسی",
            "materials": "قلم نی، مرکب، کاغذ خوشنویسی",
            "steps": "1. آماده‌سازی قلم\n2. تمرین خطوط پایه\n3. نوشتن حروف الفبا\n4. ترکیب حروف",
            "video_url": "https://example.com/calligraphy_basics",
            "image_url": "https://example.com/calligraphy_sample.jpg"
        }
    ]
    
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    
    for lesson in lessons:
        cursor.execute('''
            INSERT OR IGNORE INTO art_lessons 
            (title, category, difficulty, description, materials, steps, video_url, image_url, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (lesson["title"], lesson["category"], lesson["difficulty"], lesson["description"],
              lesson["materials"], lesson["steps"], lesson["video_url"], lesson["image_url"],
              datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# تمرین‌های خلاقیت نمونه
def insert_sample_exercises():
    exercises = [
        {
            "title": "نقاشی با چشم بسته",
            "category": "خلاقیت",
            "description": "نقاشی کردن بدون نگاه کردن به کاغذ",
            "instructions": "چشم‌های خود را ببندید و یک منظره را نقاشی کنید",
            "duration": 15,
            "difficulty": "آسان",
            "materials_needed": "کاغذ، مداد"
        },
        {
            "title": "ترکیب رنگ‌های تصادفی",
            "category": "رنگ",
            "description": "ایجاد ترکیب‌های رنگی جدید",
            "instructions": "سه رنگ تصادفی انتخاب کنید و ترکیب‌های مختلف بسازید",
            "duration": 20,
            "difficulty": "متوسط",
            "materials_needed": "رنگ، پالت، کاغذ"
        },
        {
            "title": "طراحی با خطوط ساده",
            "category": "طراحی",
            "description": "طراحی با استفاده از خطوط ساده",
            "instructions": "یک موضوع را فقط با خطوط ساده طراحی کنید",
            "duration": 30,
            "difficulty": "آسان",
            "materials_needed": "کاغذ، قلم"
        }
    ]
    
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    
    for exercise in exercises:
        cursor.execute('''
            INSERT OR IGNORE INTO creative_exercises 
            (title, category, description, instructions, duration, difficulty, materials_needed, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (exercise["title"], exercise["category"], exercise["description"], exercise["instructions"],
              exercise["duration"], exercise["difficulty"], exercise["materials_needed"],
              datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# مدیریت کاربران
def add_user(user_id, username, first_name):
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, join_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_info(user_id):
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_points(user_id, points):
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET total_points = total_points + ? WHERE user_id = ?', (points, user_id))
    conn.commit()
    conn.close()

# مدیریت درس‌ها
def get_lessons_by_category(category=None, difficulty=None):
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    
    if category and difficulty:
        cursor.execute('SELECT * FROM art_lessons WHERE category = ? AND difficulty = ?', (category, difficulty))
    elif category:
        cursor.execute('SELECT * FROM art_lessons WHERE category = ?', (category,))
    elif difficulty:
        cursor.execute('SELECT * FROM art_lessons WHERE difficulty = ?', (difficulty,))
    else:
        cursor.execute('SELECT * FROM art_lessons ORDER BY created_date DESC')
    
    lessons = cursor.fetchall()
    conn.close()
    return lessons

def get_lesson_by_id(lesson_id):
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM art_lessons WHERE id = ?', (lesson_id,))
    lesson = cursor.fetchone()
    conn.close()
    return lesson

# مدیریت آثار هنری
def add_artwork(user_id, title, description, category, file_id, file_type):
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO artworks (user_id, title, description, category, file_id, file_type, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, title, description, category, file_id, file_type, datetime.datetime.now().isoformat()))
    
    # افزایش تعداد آثار کاربر
    cursor.execute('UPDATE users SET total_artworks = total_artworks + 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def get_user_artworks(user_id):
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM artworks WHERE user_id = ? ORDER BY created_date DESC', (user_id,))
    artworks = cursor.fetchall()
    conn.close()
    return artworks

def get_artworks_by_category(category, limit=10):
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, u.first_name 
        FROM artworks a
        JOIN users u ON a.user_id = u.user_id
        WHERE a.category = ?
        ORDER BY a.likes DESC, a.created_date DESC
        LIMIT ?
    ''', (category, limit))
    artworks = cursor.fetchall()
    conn.close()
    return artworks

# مدیریت مسابقات
def get_active_competitions():
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM competitions WHERE status = "active" ORDER BY created_date DESC')
    competitions = cursor.fetchall()
    conn.close()
    return competitions

def join_competition(competition_id, user_id, artwork_id):
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO competition_entries (competition_id, user_id, artwork_id, submission_date)
        VALUES (?, ?, ?, ?)
    ''', (competition_id, user_id, artwork_id, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

# مدیریت تمرین‌ها
def get_creative_exercises(category=None):
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    
    if category:
        cursor.execute('SELECT * FROM creative_exercises WHERE category = ?', (category,))
    else:
        cursor.execute('SELECT * FROM creative_exercises ORDER BY RANDOM()')
    
    exercises = cursor.fetchall()
    conn.close()
    return exercises

# کلیدهای میانبر
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('🎨 درس‌های هنری', '🖼️ گالری آثار')
    keyboard.row('🏆 مسابقات', '🎯 تمرین‌های خلاقیت')
    keyboard.row('📤 آپلود اثر', '📊 پروفایل من')
    keyboard.row('📖 راهنما', '⚙️ تنظیمات')
    return keyboard

def create_art_categories_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🎨 نقاشی", callback_data="category_painting"),
        InlineKeyboardButton("✏️ طراحی", callback_data="category_drawing")
    )
    keyboard.row(
        InlineKeyboardButton("✍️ خوشنویسی", callback_data="category_calligraphy"),
        InlineKeyboardButton("🎭 مجسمه‌سازی", callback_data="category_sculpture")
    )
    keyboard.row(
        InlineKeyboardButton("📸 عکاسی", callback_data="category_photography"),
        InlineKeyboardButton("🎵 موسیقی", callback_data="category_music")
    )
    return keyboard

def create_difficulty_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🟢 مبتدی", callback_data="difficulty_beginner"),
        InlineKeyboardButton("🟡 متوسط", callback_data="difficulty_intermediate")
    )
    keyboard.row(
        InlineKeyboardButton("🔴 پیشرفته", callback_data="difficulty_advanced")
    )
    return keyboard

def create_lesson_keyboard(lesson_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📖 مطالعه", callback_data=f"study_lesson_{lesson_id}"),
        InlineKeyboardButton("🎥 ویدیو", callback_data=f"video_lesson_{lesson_id}")
    )
    keyboard.row(
        InlineKeyboardButton("📝 تمرین", callback_data=f"practice_lesson_{lesson_id}"),
        InlineKeyboardButton("✅ تکمیل", callback_data=f"complete_lesson_{lesson_id}")
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
🎨 سلام {first_name} عزیز!

به ربات خلاقیت و هنر خوش آمدید! 🎭

این ربات به شما کمک می‌کند تا:
• هنرهای مختلف را یاد بگیرید
• آثار خود را به اشتراک بگذارید
• در مسابقات هنری شرکت کنید
• خلاقیت خود را تقویت کنید

🎯 ویژگی‌ها:
• درس‌های هنری تعاملی
• گالری آثار هنری
• مسابقات خلاقیت
• تمرین‌های هنری
• سیستم امتیازدهی

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    bot.reply_to(message, welcome_text, reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '🎨 درس‌های هنری')
def art_lessons_menu(message):
    lessons_text = """
🎨 درس‌های هنری

دسته‌بندی‌های موجود:
• 🎨 نقاشی (آبرنگ، رنگ روغن، اکریلیک)
• ✏️ طراحی (چهره، منظره، طبیعت بی‌جان)
• ✍️ خوشنویسی (فارسی، عربی، انگلیسی)
• 🎭 مجسمه‌سازی (گل، گچ، چوب)
• 📸 عکاسی (دیجیتال، آنالوگ)
• 🎵 موسیقی (ساز، آواز، تئوری)

لطفاً دسته‌بندی مورد نظر را انتخاب کنید:
    """
    
    bot.reply_to(message, lessons_text, reply_markup=create_art_categories_keyboard())

@bot.message_handler(func=lambda message: message.text == '🖼️ گالری آثار')
def gallery_menu(message):
    gallery_text = """
🖼️ گالری آثار هنری

آثار برتر در دسته‌بندی‌های مختلف:

🎨 نقاشی:
• منظره‌های زیبا
• پرتره‌های هنرمندانه
• نقاشی‌های انتزاعی

✏️ طراحی:
• طراحی‌های چهره
• طراحی‌های معماری
• طراحی‌های طبیعت

✍️ خوشنویسی:
• خط نستعلیق
• خط شکسته
• خط ثلث

لطفاً دسته‌بندی مورد نظر را انتخاب کنید:
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🎨 نقاشی", callback_data="gallery_painting"),
        InlineKeyboardButton("✏️ طراحی", callback_data="gallery_drawing")
    )
    keyboard.row(
        InlineKeyboardButton("✍️ خوشنویسی", callback_data="gallery_calligraphy"),
        InlineKeyboardButton("📸 عکاسی", callback_data="gallery_photography")
    )
    keyboard.row(
        InlineKeyboardButton("🏆 آثار برتر", callback_data="gallery_best")
    )
    
    bot.reply_to(message, gallery_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '🏆 مسابقات')
def competitions_menu(message):
    competitions = get_active_competitions()
    
    if not competitions:
        competitions_text = "🏆 در حال حاضر هیچ مسابقه فعالی وجود ندارد.\n\nمسابقات جدید به زودی اعلام خواهد شد."
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("📅 تقویم مسابقات", callback_data="competition_calendar"))
    else:
        competitions_text = "🏆 مسابقات فعال:\n\n"
        
        for i, competition in enumerate(competitions, 1):
            competitions_text += f"{i}. 🏆 {competition[1]}\n"
            competitions_text += f"   📝 {competition[2]}\n"
            competitions_text += f"   🎨 {competition[3]}\n"
            competitions_text += f"   💰 جایزه: {competition[6]}\n"
            competitions_text += f"   📅 پایان: {competition[5][:10]}\n\n"
        
        keyboard = InlineKeyboardMarkup()
        for i, competition in enumerate(competitions[:5], 1):
            keyboard.row(InlineKeyboardButton(f"{i}. {competition[1]}", callback_data=f"competition_{competition[0]}"))
    
    bot.reply_to(message, competitions_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '🎯 تمرین‌های خلاقیت')
def creative_exercises_menu(message):
    exercises_text = """
🎯 تمرین‌های خلاقیت

تمرین‌های موجود برای تقویت خلاقیت:

🎨 نقاشی با چشم بسته
🎨 ترکیب رنگ‌های تصادفی
🎨 طراحی با خطوط ساده
🎨 نقاشی با دست غیر غالب
🎨 خلق داستان تصویری
🎨 طراحی از حافظه

لطفاً نوع تمرین مورد نظر را انتخاب کنید:
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🎨 نقاشی", callback_data="exercise_painting"),
        InlineKeyboardButton("🎨 رنگ", callback_data="exercise_color")
    )
    keyboard.row(
        InlineKeyboardButton("✏️ طراحی", callback_data="exercise_drawing"),
        InlineKeyboardButton("🎭 خلاقیت", callback_data="exercise_creativity")
    )
    keyboard.row(
        InlineKeyboardButton("🎲 تصادفی", callback_data="exercise_random")
    )
    
    bot.reply_to(message, exercises_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📤 آپلود اثر')
def upload_artwork(message):
    upload_text = """
📤 آپلود اثر هنری

برای آپلود اثر خود، لطفاً اطلاعات زیر را وارد کنید:

1. عنوان اثر
2. توضیحات
3. دسته‌بندی
4. فایل اثر

لطفاً عنوان اثر خود را وارد کنید:
    """
    
    msg = bot.reply_to(message, upload_text)
    bot.register_next_step_handler(msg, process_artwork_title)

def process_artwork_title(message):
    title = message.text
    msg = bot.reply_to(message, "📝 لطفاً توضیحات اثر را وارد کنید:")
    bot.register_next_step_handler(msg, process_artwork_description, title)

def process_artwork_description(message, title):
    description = message.text
    msg = bot.reply_to(message, "🎨 لطفاً دسته‌بندی اثر را انتخاب کنید:")
    bot.register_next_step_handler(msg, process_artwork_category, title, description)

def process_artwork_category(message, title, description):
    category = message.text
    msg = bot.reply_to(message, "📎 حالا فایل اثر خود را ارسال کنید:")
    bot.register_next_step_handler(msg, process_artwork_file, title, description, category)

def process_artwork_file(message, title, description, category):
    if not message.photo and not message.document:
        bot.reply_to(message, "❌ لطفاً فایل تصویری ارسال کنید.")
        return
    
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    file_type = "photo" if message.photo else "document"
    
    add_artwork(user_id, title, description, category, file_id, file_type)
    
    success_text = f"""
✅ اثر هنری شما با موفقیت آپلود شد!

🎨 عنوان: {title}
📝 توضیحات: {description}
🎨 دسته‌بندی: {category}

اثر شما در گالری قرار گرفت و دیگران می‌توانند آن را مشاهده کنند.
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🖼️ مشاهده در گالری", callback_data="view_gallery"),
        InlineKeyboardButton("📤 آپلود اثر دیگر", callback_data="upload_another")
    )
    
    bot.reply_to(message, success_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📊 پروفایل من')
def my_profile(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    if not user_info:
        bot.reply_to(message, "اطلاعات شما یافت نشد.")
        return
    
    artworks = get_user_artworks(user_id)
    
    profile_text = f"""
📊 پروفایل شما:

👤 نام: {user_info[3]}
🎨 سطح: {user_info[4]}
📅 تاریخ عضویت: {user_info[5][:10]}
🖼️ تعداد آثار: {user_info[6]}
🏆 امتیاز کل: {user_info[7]}

📈 آمار:
• آثار آپلود شده: {len(artworks)}
• لایک‌های دریافت شده: {sum(art[6] for art in artworks)}
• بازدید کل: {sum(art[7] for art in artworks)}
• مسابقات شرکت شده: {get_competition_entries_count(user_id)}
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🖼️ آثار من", callback_data="my_artworks"),
        InlineKeyboardButton("📈 نمودار پیشرفت", callback_data="progress_chart")
    )
    keyboard.row(
        InlineKeyboardButton("🏆 گواهی‌ها", callback_data="certificates"),
        InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="edit_profile")
    )
    
    bot.reply_to(message, profile_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📖 راهنما')
def help_command(message):
    help_text = """
📖 راهنمای ربات خلاقیت و هنر

🎨 درس‌های هنری:
• انتخاب دسته‌بندی مورد علاقه
• مطالعه درس‌های تعاملی
• مشاهده ویدیوهای آموزشی
• انجام تمرین‌های عملی

🖼️ گالری آثار:
• مشاهده آثار برتر
• الهام گرفتن از آثار دیگران
• لایک کردن آثار مورد علاقه
• اشتراک‌گذاری آثار

🏆 مسابقات:
• شرکت در مسابقات هنری
• ارسال آثار برای داوری
• دریافت جایزه و گواهی
• رقابت با هنرمندان دیگر

🎯 تمرین‌های خلاقیت:
• انجام تمرین‌های خلاقانه
• تقویت مهارت‌های هنری
• خلق آثار منحصر به فرد
• توسعه خلاقیت شخصی

📤 آپلود اثر:
• اشتراک‌گذاری آثار خود
• دریافت بازخورد از دیگران
• ساخت پورتفولیو هنری
• افزایش شهرت هنری

📊 پروفایل من:
• مشاهده آمار شخصی
• پیگیری پیشرفت
• دریافت گواهی‌ها
• مدیریت آثار

💡 نکات مهم:
• هر روز تمرین کنید
• از آثار دیگران الهام بگیرید
• در مسابقات شرکت کنید
• آثار خود را به اشتراک بگذارید

📞 پشتیبانی:
برای سوالات بیشتر با پشتیبانی تماس بگیرید.
    """
    
    bot.reply_to(message, help_text)

# توابع کمکی
def get_competition_entries_count(user_id):
    conn = sqlite3.connect('creative_art.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM competition_entries WHERE user_id = ?', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

# مدیریت callback ها
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("category_"):
        category = call.data.split("_")[1]
        lessons = get_lessons_by_category(category)
        
        if not lessons:
            bot.answer_callback_query(call.id, "هیچ درسی در این دسته‌بندی موجود نیست")
            return
        
        lessons_text = f"🎨 درس‌های {category}:\n\n"
        
        for i, lesson in enumerate(lessons[:5], 1):
            difficulty_emoji = "🟢" if lesson[3] == "مبتدی" else "🟡" if lesson[3] == "متوسط" else "🔴"
            lessons_text += f"{i}. {difficulty_emoji} {lesson[1]}\n"
            lessons_text += f"   📝 {lesson[4][:50]}...\n\n"
        
        keyboard = InlineKeyboardMarkup()
        for i, lesson in enumerate(lessons[:5], 1):
            keyboard.row(InlineKeyboardButton(f"{i}. {lesson[1]}", callback_data=f"lesson_{lesson[0]}"))
        
        bot.edit_message_text(lessons_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
    
    elif call.data.startswith("lesson_"):
        lesson_id = int(call.data.split("_")[1])
        lesson = get_lesson_by_id(lesson_id)
        
        if not lesson:
            bot.answer_callback_query(call.id, "درس یافت نشد")
            return
        
        lesson_text = f"""
📖 {lesson[1]}

📝 توضیحات:
{lesson[4]}

🎨 مواد مورد نیاز:
{lesson[5]}

📋 مراحل:
{lesson[6]}

🎯 سطح: {lesson[3]}
📂 دسته‌بندی: {lesson[2]}
        """
        
        bot.edit_message_text(lesson_text, call.message.chat.id, call.message.message_id,
                             reply_markup=create_lesson_keyboard(lesson_id))

# راه‌اندازی ربات
if __name__ == "__main__":
    init_database()
    insert_sample_lessons()
    insert_sample_exercises()
    print("🎨 ربات خلاقیت و هنر راه‌اندازی شد!")
    print("🎭 آماده برای آموزش هنرهای مختلف...")
    bot.polling(none_stop=True)