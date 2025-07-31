 # ربات مسابقات علمی
# ScienceQuizBot - برگزاری مسابقات علمی، پرسش و پاسخ
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
    conn = sqlite3.connect('science_quiz.db')
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            score INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            join_date TEXT
        )
    ''')
    
    # جدول سوالات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            category TEXT,
            question TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer TEXT,
            explanation TEXT,
            difficulty TEXT,
            created_date TEXT
        )
    ''')
    
    # جدول مسابقات روزانه
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_quizzes (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            question_id INTEGER,
            user_answer TEXT,
            is_correct BOOLEAN,
            quiz_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')
    
    # جدول رتبه‌بندی
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            score INTEGER,
            rank INTEGER,
            update_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# سوالات نمونه
def insert_sample_questions():
    questions = [
        {
            "category": "فیزیک",
            "question": "کدام یک از موارد زیر واحد اندازه‌گیری نیرو است؟",
            "option_a": "وات",
            "option_b": "نیوتن",
            "option_c": "ژول",
            "option_d": "پاسکال",
            "correct_answer": "B",
            "explanation": "نیوتن واحد اندازه‌گیری نیرو در سیستم SI است.",
            "difficulty": "متوسط"
        },
        {
            "category": "شیمی",
            "question": "فرمول شیمیایی آب چیست؟",
            "option_a": "H2O",
            "option_b": "CO2",
            "option_c": "O2",
            "option_d": "N2",
            "correct_answer": "A",
            "explanation": "فرمول شیمیایی آب H2O است که از دو اتم هیدروژن و یک اتم اکسیژن تشکیل شده است.",
            "difficulty": "آسان"
        },
        {
            "category": "زیست‌شناسی",
            "question": "کدام اندام مسئول پمپاژ خون در بدن است؟",
            "option_a": "کبد",
            "option_b": "قلب",
            "option_c": "ریه",
            "option_d": "مغز",
            "correct_answer": "B",
            "explanation": "قلب مسئول پمپاژ خون در سراسر بدن است.",
            "difficulty": "آسان"
        },
        {
            "category": "ریاضی",
            "question": "حاصل ضرب 7 × 8 برابر است با:",
            "option_a": "54",
            "option_b": "56",
            "option_c": "58",
            "option_d": "60",
            "correct_answer": "B",
            "explanation": "7 × 8 = 56",
            "difficulty": "آسان"
        },
        {
            "category": "نجوم",
            "question": "نزدیک‌ترین سیاره به خورشید کدام است؟",
            "option_a": "زهره",
            "option_b": "عطارد",
            "option_c": "زمین",
            "option_d": "مریخ",
            "correct_answer": "B",
            "explanation": "عطارد نزدیک‌ترین سیاره به خورشید است.",
            "difficulty": "متوسط"
        }
    ]
    
    conn = sqlite3.connect('science_quiz.db')
    cursor = conn.cursor()
    
    for q in questions:
        cursor.execute('''
            INSERT OR IGNORE INTO questions 
            (category, question, option_a, option_b, option_c, option_d, 
             correct_answer, explanation, difficulty, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (q['category'], q['question'], q['option_a'], q['option_b'], 
              q['option_c'], q['option_d'], q['correct_answer'], q['explanation'],
              q['difficulty'], datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# مدیریت کاربران
def add_user(user_id, username, first_name):
    conn = sqlite3.connect('science_quiz.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, join_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect('science_quiz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_score(user_id, points):
    conn = sqlite3.connect('science_quiz.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET score = score + ? WHERE user_id = ?', (points, user_id))
    conn.commit()
    conn.close()

# مدیریت سوالات
def get_random_question(category=None):
    conn = sqlite3.connect('science_quiz.db')
    cursor = conn.cursor()
    
    if category:
        cursor.execute('SELECT * FROM questions WHERE category = ? ORDER BY RANDOM() LIMIT 1', (category,))
    else:
        cursor.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT 1')
    
    question = cursor.fetchone()
    conn.close()
    return question

def get_questions_by_category(category):
    conn = sqlite3.connect('science_quiz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions WHERE category = ?', (category,))
    questions = cursor.fetchall()
    conn.close()
    return questions

# مدیریت مسابقات
def record_quiz_result(user_id, question_id, user_answer, is_correct):
    conn = sqlite3.connect('science_quiz.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO daily_quizzes (user_id, question_id, user_answer, is_correct, quiz_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, question_id, user_answer, is_correct, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

# رتبه‌بندی
def update_leaderboard():
    conn = sqlite3.connect('science_quiz.db')
    cursor = conn.cursor()
    
    # حذف رتبه‌بندی قبلی
    cursor.execute('DELETE FROM leaderboard')
    
    # دریافت کاربران بر اساس امتیاز
    cursor.execute('SELECT user_id, score FROM users ORDER BY score DESC')
    users = cursor.fetchall()
    
    # ثبت رتبه‌بندی جدید
    for rank, (user_id, score) in enumerate(users, 1):
        cursor.execute('''
            INSERT INTO leaderboard (user_id, score, rank, update_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, score, rank, datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_leaderboard(limit=10):
    conn = sqlite3.connect('science_quiz.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.first_name, l.score, l.rank
        FROM leaderboard l
        JOIN users u ON l.user_id = u.user_id
        ORDER BY l.rank
        LIMIT ?
    ''', (limit,))
    leaderboard = cursor.fetchall()
    conn.close()
    return leaderboard

# کلیدهای میانبر
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('🎯 مسابقه روزانه', '📚 دسته‌بندی‌ها')
    keyboard.row('🏆 رتبه‌بندی', '📊 آمار من')
    keyboard.row('📖 راهنما', '⚙️ تنظیمات')
    return keyboard

def create_category_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🔬 فیزیک", callback_data="category_physics"),
        InlineKeyboardButton("🧪 شیمی", callback_data="category_chemistry")
    )
    keyboard.row(
        InlineKeyboardButton("🌱 زیست‌شناسی", callback_data="category_biology"),
        InlineKeyboardButton("🔢 ریاضی", callback_data="category_math")
    )
    keyboard.row(
        InlineKeyboardButton("🌌 نجوم", callback_data="category_astronomy"),
        InlineKeyboardButton("🔬 همه", callback_data="category_all")
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
🔬 سلام {first_name} عزیز!

به ربات مسابقات علمی خوش آمدید! 🎯

این ربات به شما کمک می‌کند تا:
• در مسابقات علمی شرکت کنید
• دانش خود را محک بزنید
• با دیگران رقابت کنید
• امتیاز جمع کنید و رتبه کسب کنید

🎯 ویژگی‌ها:
• سوالات روزانه
• دسته‌بندی‌های مختلف
• سیستم امتیازدهی
• رتبه‌بندی جهانی

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    bot.reply_to(message, welcome_text, reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '🎯 مسابقه روزانه')
def daily_quiz(message):
    user_id = message.from_user.id
    question = get_random_question()
    
    if not question:
        bot.reply_to(message, "متأسفانه سوالی موجود نیست. لطفاً بعداً تلاش کنید.")
        return
    
    question_text = f"""
🔬 سوال روزانه:

{question[2]}

A) {question[3]}
B) {question[4]}
C) {question[5]}
D) {question[6]}

📚 دسته‌بندی: {question[1]}
🎯 سطح: {question[9]}
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("A", callback_data=f"answer_{question[0]}_A"),
        InlineKeyboardButton("B", callback_data=f"answer_{question[0]}_B"),
        InlineKeyboardButton("C", callback_data=f"answer_{question[0]}_C"),
        InlineKeyboardButton("D", callback_data=f"answer_{question[0]}_D")
    )
    
    bot.reply_to(message, question_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📚 دسته‌بندی‌ها')
def categories_menu(message):
    bot.reply_to(message, "📚 دسته‌بندی‌های علمی\n\nلطفاً دسته‌بندی مورد نظر را انتخاب کنید:", 
                 reply_markup=create_category_keyboard())

@bot.message_handler(func=lambda message: message.text == '🏆 رتبه‌بندی')
def show_leaderboard(message):
    update_leaderboard()
    leaderboard = get_leaderboard()
    
    if not leaderboard:
        bot.reply_to(message, "هنوز هیچ امتیازی ثبت نشده است.")
        return
    
    leaderboard_text = "🏆 رتبه‌بندی برترین‌ها:\n\n"
    
    for i, (name, score, rank) in enumerate(leaderboard, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
        leaderboard_text += f"{medal} رتبه {rank}: {name} - {score} امتیاز\n"
    
    bot.reply_to(message, leaderboard_text)

@bot.message_handler(func=lambda message: message.text == '📊 آمار من')
def show_my_stats(message):
    user_id = message.from_user.id
    user_stats = get_user_stats(user_id)
    
    if not user_stats:
        bot.reply_to(message, "اطلاعات شما یافت نشد.")
        return
    
    stats_text = f"""
📊 آمار شما:

👤 نام: {user_stats[3]}
🏆 امتیاز کل: {user_stats[4]}
📝 تعداد سوالات: {user_stats[5]}
✅ پاسخ‌های صحیح: {user_stats[6]}
📈 درصد موفقیت: {(user_stats[6]/user_stats[5]*100) if user_stats[5] > 0 else 0:.1f}%
📅 تاریخ عضویت: {user_stats[7][:10]}
    """
    
    bot.reply_to(message, stats_text)

@bot.message_handler(func=lambda message: message.text == '📖 راهنما')
def help_command(message):
    help_text = """
📖 راهنمای ربات مسابقات علمی

🎯 نحوه استفاده:
• مسابقه روزانه: هر روز سوال جدید
• دسته‌بندی‌ها: انتخاب موضوع مورد علاقه
• رتبه‌بندی: مشاهده برترین‌ها
• آمار من: مشاهده پیشرفت شخصی

🏆 سیستم امتیازدهی:
• پاسخ صحیح: +10 امتیاز
• پاسخ نادرست: +1 امتیاز (برای تلاش)
• مسابقه روزانه: +5 امتیاز اضافی

📚 دسته‌بندی‌ها:
• فیزیک: قوانین طبیعت
• شیمی: ترکیبات و واکنش‌ها
• زیست‌شناسی: موجودات زنده
• ریاضی: محاسبات و منطق
• نجوم: اجرام آسمانی

💡 نکات مهم:
• هر روز می‌توانید در مسابقه شرکت کنید
• سوالات متنوع و جذاب
• رقابت سالم و دوستانه
• یادگیری همراه با سرگرمی

📞 پشتیبانی:
برای سوالات بیشتر با پشتیبانی تماس بگیرید.
    """
    
    bot.reply_to(message, help_text)

# مدیریت callback ها
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("answer_"):
        parts = call.data.split("_")
        question_id = int(parts[1])
        user_answer = parts[2]
        
        # بررسی پاسخ صحیح
        conn = sqlite3.connect('science_quiz.db')
        cursor = conn.cursor()
        cursor.execute('SELECT correct_answer FROM questions WHERE id = ?', (question_id,))
        correct_answer = cursor.fetchone()[0]
        conn.close()
        
        is_correct = user_answer == correct_answer
        points = 10 if is_correct else 1
        
        # ثبت نتیجه
        record_quiz_result(call.from_user.id, question_id, user_answer, is_correct)
        update_user_score(call.from_user.id, points)
        
        # نمایش نتیجه
        result_text = f"""
{'✅ پاسخ صحیح!' if is_correct else '❌ پاسخ نادرست!'}

🎯 امتیاز کسب شده: {points}
📊 امتیاز کل شما: {get_user_stats(call.from_user.id)[4] + points}

💡 توضیح:
{get_question_explanation(question_id)}
        """
        
        bot.answer_callback_query(call.id, "پاسخ ثبت شد!")
        bot.edit_message_text(result_text, call.message.chat.id, call.message.message_id)
        
    elif call.data.startswith("category_"):
        category = call.data.split("_")[1]
        if category == "all":
            question = get_random_question()
        else:
            question = get_random_question(category)
        
        if question:
            question_text = f"""
🔬 سوال {category}:

{question[2]}

A) {question[3]}
B) {question[4]}
C) {question[5]}
D) {question[6]}

📚 دسته‌بندی: {question[1]}
🎯 سطح: {question[9]}
            """
            
            keyboard = InlineKeyboardMarkup()
            keyboard.row(
                InlineKeyboardButton("A", callback_data=f"answer_{question[0]}_A"),
                InlineKeyboardButton("B", callback_data=f"answer_{question[0]}_B"),
                InlineKeyboardButton("C", callback_data=f"answer_{question[0]}_C"),
                InlineKeyboardButton("D", callback_data=f"answer_{question[0]}_D")
            )
            
            bot.edit_message_text(question_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        else:
            bot.answer_callback_query(call.id, "سوالی در این دسته‌بندی موجود نیست")

def get_question_explanation(question_id):
    conn = sqlite3.connect('science_quiz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT explanation FROM questions WHERE id = ?', (question_id,))
    explanation = cursor.fetchone()[0]
    conn.close()
    return explanation

# راه‌اندازی ربات
if __name__ == "__main__":
    init_database()
    insert_sample_questions()
    print("🔬 ربات مسابقات علمی راه‌اندازی شد!")
    print("🎯 آماده برای برگزاری مسابقات علمی...")
    bot.polling(none_stop=True)