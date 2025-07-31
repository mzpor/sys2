 # ربات یادگیری زبان
# LanguageLearningBot - آموزش زبان‌های مختلف
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
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            join_date TEXT,
            current_language TEXT DEFAULT 'english',
            level TEXT DEFAULT 'beginner',
            streak_days INTEGER DEFAULT 0,
            total_points INTEGER DEFAULT 0,
            last_study_date TEXT
        )
    ''')
    
    # جدول درس‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY,
            language TEXT,
            level TEXT,
            lesson_number INTEGER,
            title TEXT,
            content TEXT,
            vocabulary TEXT,
            grammar TEXT,
            exercises TEXT
        )
    ''')
    
    # جدول کلمات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY,
            language TEXT,
            word TEXT,
            translation TEXT,
            part_of_speech TEXT,
            example TEXT,
            difficulty TEXT
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
            FOREIGN KEY (lesson_id) REFERENCES lessons (id)
        )
    ''')
    
    # جدول چت‌های هوش مصنوعی
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_chats (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            language TEXT,
            message TEXT,
            response TEXT,
            chat_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# درس‌های نمونه
def insert_sample_lessons():
    lessons = [
        {
            "language": "english",
            "level": "beginner",
            "lesson_number": 1,
            "title": "سلام و احوالپرسی",
            "content": "در این درس یاد می‌گیریم چگونه سلام کنیم و احوالپرسی کنیم.",
            "vocabulary": "Hello, Hi, Good morning, Good afternoon, Good evening, How are you?, I'm fine, Thank you",
            "grammar": "استفاده از فعل 'to be' در جملات ساده",
            "exercises": "تمرین 1: سلام کردن\nتمرین 2: احوالپرسی\nتمرین 3: معرفی خود"
        },
        {
            "language": "english",
            "level": "beginner",
            "lesson_number": 2,
            "title": "اعداد و شمارش",
            "content": "یادگیری اعداد از 1 تا 100 و نحوه شمارش.",
            "vocabulary": "One, Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten",
            "grammar": "اعداد ترتیبی و کاردینال",
            "exercises": "تمرین 1: شمارش\nتمرین 2: نوشتن اعداد\nتمرین 3: محاسبات ساده"
        },
        {
            "language": "english",
            "level": "intermediate",
            "lesson_number": 1,
            "title": "زمان حال ساده",
            "content": "یادگیری زمان حال ساده و کاربردهای آن.",
            "vocabulary": "Work, Study, Play, Read, Write, Speak, Listen, Watch",
            "grammar": "Present Simple Tense - ساختار و کاربرد",
            "exercises": "تمرین 1: ساخت جملات\nتمرین 2: منفی کردن\nتمرین 3: سوالی کردن"
        }
    ]
    
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    for lesson in lessons:
        cursor.execute('''
            INSERT OR IGNORE INTO lessons 
            (language, level, lesson_number, title, content, vocabulary, grammar, exercises)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (lesson["language"], lesson["level"], lesson["lesson_number"], 
              lesson["title"], lesson["content"], lesson["vocabulary"], 
              lesson["grammar"], lesson["exercises"]))
    
    conn.commit()
    conn.close()

# کلمات نمونه
def insert_sample_vocabulary():
    vocabulary = [
        ("english", "hello", "سلام", "interjection", "Hello, how are you?", "beginner"),
        ("english", "goodbye", "خداحافظ", "interjection", "Goodbye, see you later!", "beginner"),
        ("english", "thank you", "متشکرم", "phrase", "Thank you for your help.", "beginner"),
        ("english", "please", "لطفاً", "adverb", "Please help me.", "beginner"),
        ("english", "sorry", "متأسفم", "adjective", "I'm sorry for being late.", "beginner"),
        ("english", "beautiful", "زیبا", "adjective", "She is beautiful.", "intermediate"),
        ("english", "important", "مهم", "adjective", "This is an important meeting.", "intermediate"),
        ("english", "difficult", "سخت", "adjective", "This exercise is difficult.", "intermediate")
    ]
    
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    for word in vocabulary:
        cursor.execute('''
            INSERT OR IGNORE INTO vocabulary 
            (language, word, translation, part_of_speech, example, difficulty)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', word)
    
    conn.commit()
    conn.close()

# مدیریت کاربران
def add_user(user_id, username, first_name):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, join_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_info(user_id):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_progress(user_id, points=0, streak_increment=0):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    if points > 0:
        cursor.execute('UPDATE users SET total_points = total_points + ? WHERE user_id = ?', (points, user_id))
    
    if streak_increment > 0:
        cursor.execute('UPDATE users SET streak_days = streak_days + ? WHERE user_id = ?', (streak_increment, user_id))
    
    cursor.execute('UPDATE users SET last_study_date = ? WHERE user_id = ?', (datetime.datetime.now().isoformat(), user_id))
    
    conn.commit()
    conn.close()

# مدیریت درس‌ها
def get_lesson(language, level, lesson_number):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM lessons 
        WHERE language = ? AND level = ? AND lesson_number = ?
    ''', (language, level, lesson_number))
    lesson = cursor.fetchone()
    conn.close()
    return lesson

def get_user_lessons(user_id, language, level):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.*, up.completed, up.score
        FROM lessons l
        LEFT JOIN user_progress up ON l.id = up.lesson_id AND up.user_id = ?
        WHERE l.language = ? AND l.level = ?
        ORDER BY l.lesson_number
    ''', (user_id, language, level))
    lessons = cursor.fetchall()
    conn.close()
    return lessons

def mark_lesson_completed(user_id, lesson_id, score):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_progress (user_id, lesson_id, completed, score, completion_date)
        VALUES (?, ?, TRUE, ?, ?)
    ''', (user_id, lesson_id, score, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

# مدیریت کلمات
def get_daily_vocabulary(language, difficulty, limit=5):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM vocabulary 
        WHERE language = ? AND difficulty = ?
        ORDER BY RANDOM() 
        LIMIT ?
    ''', (language, difficulty, limit))
    words = cursor.fetchall()
    conn.close()
    return words

def get_word_by_id(word_id):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vocabulary WHERE id = ?', (word_id,))
    word = cursor.fetchone()
    conn.close()
    return word

# مدیریت چت هوش مصنوعی
def save_ai_chat(user_id, language, message, response):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ai_chats (user_id, language, message, response, chat_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, language, message, response, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def generate_ai_response(message, language, level):
    """شبیه‌سازی پاسخ هوش مصنوعی"""
    responses = {
        "english": {
            "beginner": [
                "That's a great question! Let me help you with that.",
                "I understand what you're asking. Here's the answer:",
                "Good question! Here's what you need to know:"
            ],
            "intermediate": [
                "Excellent question! Let me explain this in detail.",
                "I see what you're getting at. Here's a comprehensive answer:",
                "Great inquiry! Let me break this down for you:"
            ]
        }
    }
    
    base_responses = responses.get(language, {}).get(level, ["I understand your question."])
    return random.choice(base_responses) + " This is a simulated AI response for demonstration purposes."

# کلیدهای میانبر
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('📚 درس روزانه', '📖 درس‌های من')
    keyboard.row('📝 تمرین', '💬 چت با AI')
    keyboard.row('📚 کلمات روزانه', '📊 پیشرفت من')
    keyboard.row('⚙️ تنظیمات', '📖 راهنما')
    return keyboard

def create_language_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🇺🇸 انگلیسی", callback_data="language_english"),
        InlineKeyboardButton("🇫🇷 فرانسوی", callback_data="language_french")
    )
    keyboard.row(
        InlineKeyboardButton("🇩🇪 آلمانی", callback_data="language_german"),
        InlineKeyboardButton("🇪🇸 اسپانیایی", callback_data="language_spanish")
    )
    return keyboard

def create_level_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🟢 مبتدی", callback_data="level_beginner"),
        InlineKeyboardButton("🟡 متوسط", callback_data="level_intermediate")
    )
    keyboard.row(
        InlineKeyboardButton("🔴 پیشرفته", callback_data="level_advanced")
    )
    return keyboard

def create_lesson_keyboard(lesson_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📖 مطالعه", callback_data=f"study_lesson_{lesson_id}"),
        InlineKeyboardButton("📝 تمرین", callback_data=f"exercise_lesson_{lesson_id}")
    )
    keyboard.row(
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
🌍 سلام {first_name} عزیز!

به ربات یادگیری زبان خوش آمدید! 📚

این ربات به شما کمک می‌کند تا:
• زبان‌های مختلف را یاد بگیرید
• درس‌های روزانه دریافت کنید
• با هوش مصنوعی تمرین کنید
• پیشرفت خود را پیگیری کنید

🎯 ویژگی‌ها:
• درس‌های تعاملی
• تمرین‌های متنوع
• چت با هوش مصنوعی
• سیستم امتیازدهی
• پیگیری پیشرفت

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    bot.reply_to(message, welcome_text, reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '📚 درس روزانه')
def daily_lesson(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    if not user_info:
        bot.reply_to(message, "لطفاً ابتدا زبان و سطح خود را انتخاب کنید.")
        return
    
    language = user_info[5] or 'english'
    level = user_info[6] or 'beginner'
    
    # دریافت درس تصادفی
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM lessons 
        WHERE language = ? AND level = ?
        ORDER BY RANDOM() 
        LIMIT 1
    ''', (language, level))
    lesson = cursor.fetchone()
    conn.close()
    
    if not lesson:
        bot.reply_to(message, "متأسفانه درس‌ای برای سطح شما موجود نیست.")
        return
    
    lesson_text = f"""
📚 درس روزانه:

📖 عنوان: {lesson[4]}
📝 محتوا: {lesson[5]}
📚 کلمات جدید: {lesson[6]}
📖 گرامر: {lesson[7]}
📝 تمرین‌ها: {lesson[8]}

🎯 سطح: {lesson[2]}
🌍 زبان: {lesson[1]}
    """
    
    keyboard = create_lesson_keyboard(lesson[0])
    bot.reply_to(message, lesson_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📖 درس‌های من')
def my_lessons(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    if not user_info:
        bot.reply_to(message, "لطفاً ابتدا زبان و سطح خود را انتخاب کنید.")
        return
    
    language = user_info[5] or 'english'
    level = user_info[6] or 'beginner'
    
    lessons = get_user_lessons(user_id, language, level)
    
    if not lessons:
        bot.reply_to(message, "هنوز هیچ درسی برای شما موجود نیست.")
        return
    
    lessons_text = f"📖 درس‌های شما ({language} - {level}):\n\n"
    
    for i, lesson in enumerate(lessons, 1):
        status = "✅ تکمیل شده" if lesson[9] else "⏳ در انتظار"
        score = f" - امتیاز: {lesson[10]}" if lesson[10] else ""
        lessons_text += f"{i}. {lesson[4]} {status}{score}\n"
    
    keyboard = InlineKeyboardMarkup()
    for i, lesson in enumerate(lessons[:5], 1):
        keyboard.row(InlineKeyboardButton(f"{i}. {lesson[4]}", callback_data=f"lesson_{lesson[0]}"))
    
    bot.reply_to(message, lessons_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📝 تمرین')
def exercises_menu(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    if not user_info:
        bot.reply_to(message, "لطفاً ابتدا زبان و سطح خود را انتخاب کنید.")
        return
    
    exercise_text = """
📝 تمرین‌های موجود:

1. 📚 تمرین کلمات
2. 📖 تمرین گرامر
3. 🎧 تمرین شنیداری
4. ✍️ تمرین نوشتاری
5. 💬 تمرین گفتاری

لطفاً نوع تمرین مورد نظر را انتخاب کنید:
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📚 کلمات", callback_data="exercise_vocabulary"),
        InlineKeyboardButton("📖 گرامر", callback_data="exercise_grammar")
    )
    keyboard.row(
        InlineKeyboardButton("🎧 شنیداری", callback_data="exercise_listening"),
        InlineKeyboardButton("✍️ نوشتاری", callback_data="exercise_writing")
    )
    keyboard.row(
        InlineKeyboardButton("💬 گفتاری", callback_data="exercise_speaking")
    )
    
    bot.reply_to(message, exercise_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '💬 چت با AI')
def ai_chat(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    if not user_info:
        bot.reply_to(message, "لطفاً ابتدا زبان و سطح خود را انتخاب کنید.")
        return
    
    language = user_info[5] or 'english'
    level = user_info[6] or 'beginner'
    
    chat_text = f"""
💬 چت با هوش مصنوعی

🌍 زبان: {language}
🎯 سطح: {level}

می‌توانید سوالات خود را به زبان {language} بپرسید و پاسخ دریافت کنید.

لطفاً سوال خود را بنویسید:
    """
    
    msg = bot.reply_to(message, chat_text)
    bot.register_next_step_handler(msg, process_ai_chat, language, level)

def process_ai_chat(message, language, level):
    user_id = message.from_user.id
    user_question = message.text
    
    # تولید پاسخ هوش مصنوعی
    ai_response = generate_ai_response(user_question, language, level)
    
    # ذخیره چت
    save_ai_chat(user_id, language, user_question, ai_response)
    
    response_text = f"""
🤖 پاسخ هوش مصنوعی:

{ai_response}

💡 نکته: این پاسخ شبیه‌سازی شده است. در نسخه واقعی، از هوش مصنوعی پیشرفته استفاده می‌شود.
    """
    
    bot.reply_to(message, response_text)

@bot.message_handler(func=lambda message: message.text == '📚 کلمات روزانه')
def daily_vocabulary(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    if not user_info:
        bot.reply_to(message, "لطفاً ابتدا زبان و سطح خود را انتخاب کنید.")
        return
    
    language = user_info[5] or 'english'
    level = user_info[6] or 'beginner'
    
    words = get_daily_vocabulary(language, level, 5)
    
    if not words:
        bot.reply_to(message, "متأسفانه کلمه‌ای برای سطح شما موجود نیست.")
        return
    
    vocabulary_text = f"📚 کلمات روزانه ({language}):\n\n"
    
    for i, word in enumerate(words, 1):
        vocabulary_text += f"{i}. {word[2]} = {word[3]}\n"
        vocabulary_text += f"   📖 نوع: {word[4]}\n"
        vocabulary_text += f"   💡 مثال: {word[5]}\n\n"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📝 تمرین کلمات", callback_data="vocab_exercise"),
        InlineKeyboardButton("💾 ذخیره", callback_data="save_vocab")
    )
    
    bot.reply_to(message, vocabulary_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📊 پیشرفت من')
def my_progress(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    if not user_info:
        bot.reply_to(message, "اطلاعات شما یافت نشد.")
        return
    
    progress_text = f"""
📊 پیشرفت شما:

👤 نام: {user_info[3]}
🌍 زبان: {user_info[5] or 'تعیین نشده'}
🎯 سطح: {user_info[6] or 'تعیین نشده'}
🏆 امتیاز کل: {user_info[8]}
🔥 روزهای متوالی: {user_info[7]}
📅 آخرین مطالعه: {user_info[9][:10] if user_info[9] else 'هیچ'}

📈 آمار:
• درس‌های تکمیل شده: {get_completed_lessons_count(user_id)}
• کلمات یاد گرفته: {get_learned_words_count(user_id)}
• چت‌های انجام شده: {get_chat_count(user_id)}
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📊 نمودار پیشرفت", callback_data="progress_chart"),
        InlineKeyboardButton("🏆 گواهی", callback_data="certificate")
    )
    
    bot.reply_to(message, progress_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📖 راهنما')
def help_command(message):
    help_text = """
📖 راهنمای ربات یادگیری زبان

📚 درس روزانه:
• هر روز درس جدید دریافت کنید
• محتوا، کلمات و گرامر یاد بگیرید
• تمرین‌های مربوطه را انجام دهید

📖 درس‌های من:
• مشاهده تمام درس‌های موجود
• پیگیری پیشرفت در هر درس
• تکمیل درس‌های ناتمام

📝 تمرین:
• تمرین کلمات جدید
• تمرین گرامر
• تمرین‌های شنیداری و گفتاری

💬 چت با AI:
• سوالات خود را بپرسید
• با هوش مصنوعی تمرین کنید
• مهارت‌های گفتاری را تقویت کنید

📚 کلمات روزانه:
• یادگیری کلمات جدید
• تمرین کلمات
• ذخیره کلمات مورد علاقه

📊 پیشرفت من:
• مشاهده آمار یادگیری
• نمودار پیشرفت
• دریافت گواهی

💡 نکات مهم:
• هر روز مطالعه کنید
• تمرین‌ها را منظم انجام دهید
• با AI تمرین کنید
• پیشرفت خود را پیگیری کنید

📞 پشتیبانی:
برای سوالات بیشتر با پشتیبانی تماس بگیرید.
    """
    
    bot.reply_to(message, help_text)

# توابع کمکی
def get_completed_lessons_count(user_id):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM user_progress WHERE user_id = ? AND completed = TRUE', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_learned_words_count(user_id):
    # شبیه‌سازی - در نسخه واقعی از دیتابیس خوانده می‌شود
    return random.randint(50, 200)

def get_chat_count(user_id):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM ai_chats WHERE user_id = ?', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

# مدیریت callback ها
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("language_"):
        language = call.data.split("_")[1]
        bot.edit_message_text("لطفاً سطح خود را انتخاب کنید:", 
                             call.message.chat.id, call.message.message_id,
                             reply_markup=create_level_keyboard())
        
    elif call.data.startswith("level_"):
        level = call.data.split("_")[1]
        user_id = call.from_user.id
        
        # به‌روزرسانی زبان و سطح کاربر
        conn = sqlite3.connect('language_learning.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET current_language = ?, level = ? WHERE user_id = ?', 
                      (language, level, user_id))
        conn.commit()
        conn.close()
        
        bot.edit_message_text(f"✅ زبان و سطح شما تنظیم شد!\n\n🌍 زبان: {language}\n🎯 سطح: {level}")

# راه‌اندازی ربات
if __name__ == "__main__":
    init_database()
    insert_sample_lessons()
    insert_sample_vocabulary()
    print("🌍 ربات یادگیری زبان راه‌اندازی شد!")
    print("📚 آماده برای آموزش زبان‌های مختلف...")
    bot.polling(none_stop=True)