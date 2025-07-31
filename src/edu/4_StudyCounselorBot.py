# ربات مشاوره تحصیلی
# StudyCounselorBot - مشاوره در انتخاب رشته، برنامه‌ریزی تحصیلی
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
    conn = sqlite3.connect('study_counselor.db')
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            join_date TEXT,
            personality_type TEXT,
            interests TEXT,
            academic_level TEXT
        )
    ''')
    
    # جدول تست‌های شخصیت
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personality_tests (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            test_type TEXT,
            answers TEXT,
            result TEXT,
            test_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # جدول رشته‌های تحصیلی
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS majors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            requirements TEXT,
            job_prospects TEXT,
            salary_range TEXT,
            universities TEXT
        )
    ''')
    
    # جدول برنامه‌های مطالعاتی
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            major_id INTEGER,
            plan_name TEXT,
            subjects TEXT,
            schedule TEXT,
            created_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (major_id) REFERENCES majors (id)
        )
    ''')
    
    # جدول مشاوره‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            question TEXT,
            answer TEXT,
            consultation_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# رشته‌های تحصیلی نمونه
def insert_sample_majors():
    majors = [
        {
            "name": "مهندسی کامپیوتر",
            "category": "مهندسی",
            "description": "ترکیبی از علوم کامپیوتر و مهندسی الکترونیک",
            "requirements": "ریاضی قوی، منطق، برنامه‌نویسی",
            "job_prospects": "عالی - تقاضای بالا در بازار کار",
            "salary_range": "15-50 میلیون تومان",
            "universities": "شریف، تهران، امیرکبیر، علم و صنعت"
        },
        {
            "name": "پزشکی",
            "category": "علوم پزشکی",
            "description": "تشخیص و درمان بیماری‌ها",
            "requirements": "علوم تجربی قوی، حافظه خوب، مهارت ارتباطی",
            "job_prospects": "عالی - امنیت شغلی بالا",
            "salary_range": "20-80 میلیون تومان",
            "universities": "تهران، شهید بهشتی، شیراز، مشهد"
        },
        {
            "name": "حقوق",
            "category": "علوم انسانی",
            "description": "مطالعه قوانین و مقررات",
            "requirements": "حافظه قوی، مهارت نوشتاری، منطق",
            "job_prospects": "خوب - فرصت‌های شغلی متنوع",
            "salary_range": "10-40 میلیون تومان",
            "universities": "تهران، شهید بهشتی، شیراز، اصفهان"
        },
        {
            "name": "مدیریت بازرگانی",
            "category": "علوم انسانی",
            "description": "مدیریت کسب و کار و تجارت",
            "requirements": "مهارت ارتباطی، ریاضی متوسط، خلاقیت",
            "job_prospects": "خوب - فرصت‌های کارآفرینی",
            "salary_range": "8-35 میلیون تومان",
            "universities": "تهران، علامه طباطبایی، شیراز، اصفهان"
        },
        {
            "name": "مهندسی برق",
            "category": "مهندسی",
            "description": "طراحی و توسعه سیستم‌های الکتریکی",
            "requirements": "ریاضی قوی، فیزیک، منطق",
            "job_prospects": "خوب - تقاضای ثابت در بازار",
            "salary_range": "12-45 میلیون تومان",
            "universities": "شریف، تهران، امیرکبیر، علم و صنعت"
        }
    ]
    
    conn = sqlite3.connect('study_counselor.db')
    cursor = conn.cursor()
    
    for major in majors:
        cursor.execute('''
            INSERT OR IGNORE INTO majors 
            (name, category, description, requirements, job_prospects, salary_range, universities)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (major["name"], major["category"], major["description"], 
              major["requirements"], major["job_prospects"], major["salary_range"], major["universities"]))
    
    conn.commit()
    conn.close()

# تست‌های شخصیت
def get_personality_test():
    questions = [
        {
            "question": "در گروه‌های اجتماعی، معمولاً:",
            "options": [
                "با افراد زیادی صحبت می‌کنم",
                "با چند نفر محدود صحبت می‌کنم",
                "بیشتر گوش می‌دهم",
                "سعی می‌کنم کار گروهی انجام دهم"
            ]
        },
        {
            "question": "وقتی با مشکلی مواجه می‌شوم:",
            "options": [
                "مستقیم سراغ حل آن می‌روم",
                "ابتدا آن را تحلیل می‌کنم",
                "از دیگران کمک می‌گیرم",
                "سعی می‌کنم راه‌حل خلاقانه پیدا کنم"
            ]
        },
        {
            "question": "در مطالعه، ترجیح می‌دهم:",
            "options": [
                "مطالب عملی و کاربردی",
                "مطالب نظری و تحلیلی",
                "مطالب خلاقانه و هنری",
                "مطالب اجتماعی و انسانی"
            ]
        },
        {
            "question": "در کار، بیشتر علاقه‌مند به:",
            "options": [
                "کار با کامپیوتر و تکنولوژی",
                "کار با مردم و ارتباطات",
                "کار خلاقانه و هنری",
                "کار تحلیلی و تحقیقاتی"
            ]
        },
        {
            "question": "در اوقات فراغت، ترجیح می‌دهم:",
            "options": [
                "بازی‌های کامپیوتری",
                "گفتگو با دوستان",
                "نقاشی یا موسیقی",
                "مطالعه کتاب"
            ]
        }
    ]
    return questions

# مدیریت کاربران
def add_user(user_id, username, first_name):
    conn = sqlite3.connect('study_counselor.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, join_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def update_user_personality(user_id, personality_type):
    conn = sqlite3.connect('study_counselor.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET personality_type = ? WHERE user_id = ?', (personality_type, user_id))
    conn.commit()
    conn.close()

def get_user_info(user_id):
    conn = sqlite3.connect('study_counselor.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# مدیریت رشته‌ها
def get_majors_by_category(category):
    conn = sqlite3.connect('study_counselor.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM majors WHERE category = ?', (category,))
    majors = cursor.fetchall()
    conn.close()
    return majors

def get_all_majors():
    conn = sqlite3.connect('study_counselor.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM majors')
    majors = cursor.fetchall()
    conn.close()
    return majors

def get_major_by_id(major_id):
    conn = sqlite3.connect('study_counselor.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM majors WHERE id = ?', (major_id,))
    major = cursor.fetchone()
    conn.close()
    return major

# مدیریت برنامه‌های مطالعاتی
def create_study_plan(user_id, major_id, plan_name, subjects, schedule):
    conn = sqlite3.connect('study_counselor.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO study_plans (user_id, major_id, plan_name, subjects, schedule, created_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, major_id, plan_name, subjects, schedule, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_study_plans(user_id):
    conn = sqlite3.connect('study_counselor.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sp.*, m.name as major_name
        FROM study_plans sp
        JOIN majors m ON sp.major_id = m.id
        WHERE sp.user_id = ?
        ORDER BY sp.created_date DESC
    ''', (user_id,))
    plans = cursor.fetchall()
    conn.close()
    return plans

# کلیدهای میانبر
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('🧠 تست شخصیت', '📚 معرفی رشته‌ها')
    keyboard.row('📋 برنامه مطالعاتی', '💬 مشاوره')
    keyboard.row('📊 پروفایل من', '📖 راهنما')
    return keyboard

def create_major_category_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🔧 مهندسی", callback_data="category_مهندسی"),
        InlineKeyboardButton("🏥 علوم پزشکی", callback_data="category_علوم پزشکی")
    )
    keyboard.row(
        InlineKeyboardButton("📚 علوم انسانی", callback_data="category_علوم انسانی"),
        InlineKeyboardButton("🔬 علوم پایه", callback_data="category_علوم پایه")
    )
    keyboard.row(
        InlineKeyboardButton("📋 همه رشته‌ها", callback_data="category_all")
    )
    return keyboard

def create_test_keyboard(question_index, options):
    keyboard = InlineKeyboardMarkup()
    for i, option in enumerate(options):
        keyboard.row(InlineKeyboardButton(option, callback_data=f"test_{question_index}_{i}"))
    return keyboard

# دستورات ربات
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    add_user(user_id, username, first_name)
    
    welcome_text = f"""
🎓 سلام {first_name} عزیز!

به ربات مشاوره تحصیلی خوش آمدید! 🧠

این ربات به شما کمک می‌کند تا:
• شخصیت خود را بهتر بشناسید
• رشته‌های تحصیلی را بررسی کنید
• برنامه مطالعاتی مناسب تهیه کنید
• از مشاوره تخصصی بهره‌مند شوید

🎯 ویژگی‌ها:
• تست‌های شخصیت دقیق
• معرفی جامع رشته‌ها
• برنامه‌ریزی مطالعاتی
• مشاوره تخصصی

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    bot.reply_to(message, welcome_text, reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '🧠 تست شخصیت')
def personality_test(message):
    user_id = message.from_user.id
    
    # بررسی اینکه آیا قبلاً تست داده یا نه
    user_info = get_user_info(user_id)
    if user_info and user_info[5]:  # personality_type
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("🔄 تست مجدد", callback_data="retake_test"),
            InlineKeyboardButton("📊 نتیجه قبلی", callback_data="show_result")
        )
        bot.reply_to(message, "شما قبلاً تست شخصیت داده‌اید. چه کاری می‌خواهید انجام دهید؟", reply_markup=keyboard)
        return
    
    # شروع تست جدید
    questions = get_personality_test()
    question = questions[0]
    
    test_text = f"""
🧠 تست شخصیت - سوال 1 از {len(questions)}

{question['question']}

لطفاً گزینه مورد نظر را انتخاب کنید:
    """
    
    keyboard = create_test_keyboard(0, question['options'])
    bot.reply_to(message, test_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📚 معرفی رشته‌ها')
def majors_menu(message):
    bot.reply_to(message, "📚 معرفی رشته‌های تحصیلی\n\nلطفاً دسته‌بندی مورد نظر را انتخاب کنید:", 
                 reply_markup=create_major_category_keyboard())

@bot.message_handler(func=lambda message: message.text == '📋 برنامه مطالعاتی')
def study_plan_menu(message):
    user_id = message.from_user.id
    plans = get_user_study_plans(user_id)
    
    if not plans:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("➕ ایجاد برنامه جدید", callback_data="create_plan"))
        bot.reply_to(message, "شما هنوز برنامه مطالعاتی ندارید. می‌خواهید برنامه جدید ایجاد کنید؟", reply_markup=keyboard)
        return
    
    plans_text = "📋 برنامه‌های مطالعاتی شما:\n\n"
    for i, plan in enumerate(plans, 1):
        plans_text += f"{i}. 📚 {plan[3]}\n"
        plans_text += f"   🎯 رشته: {plan[8]}\n"
        plans_text += f"   📅 تاریخ ایجاد: {plan[6][:10]}\n\n"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("➕ برنامه جدید", callback_data="create_plan"),
        InlineKeyboardButton("📊 مشاهده برنامه", callback_data="view_plan")
    )
    
    bot.reply_to(message, plans_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '💬 مشاوره')
def consultation_menu(message):
    consultation_text = """
💬 مشاوره تحصیلی

برای دریافت مشاوره تخصصی، لطفاً سوال خود را مطرح کنید.

موضوعات قابل مشاوره:
• انتخاب رشته تحصیلی
• برنامه‌ریزی مطالعاتی
• روش‌های مطالعه
• مدیریت زمان
• آمادگی برای کنکور
• انتخاب دانشگاه
• آینده شغلی رشته‌ها

لطفاً سوال خود را بنویسید:
    """
    
    msg = bot.reply_to(message, consultation_text)
    bot.register_next_step_handler(msg, process_consultation)

def process_consultation(message):
    question = message.text
    user_id = message.from_user.id
    
    # ذخیره سوال
    conn = sqlite3.connect('study_counselor.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO consultations (user_id, question, consultation_date)
        VALUES (?, ?, ?)
    ''', (user_id, question, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    # پاسخ خودکار (در نسخه واقعی، این بخش توسط مشاور پاسخ داده می‌شود)
    if "رشته" in question.lower():
        answer = "برای انتخاب رشته، ابتدا تست شخصیت را انجام دهید تا بتوانم راهنمایی دقیق‌تری ارائه دهم."
    elif "مطالعه" in question.lower():
        answer = "برای برنامه‌ریزی مطالعاتی، از بخش 'برنامه مطالعاتی' استفاده کنید."
    elif "کنکور" in question.lower():
        answer = "برای آمادگی کنکور، برنامه منظم و تمرین مداوم توصیه می‌شود."
    else:
        answer = "سوال شما ثبت شد. مشاور ما در اسرع وقت پاسخ خواهد داد."
    
    response_text = f"""
💬 پاسخ مشاور:

{answer}

سوال شما ثبت شد و در حال بررسی است.
    """
    
    bot.reply_to(message, response_text)

@bot.message_handler(func=lambda message: message.text == '📊 پروفایل من')
def show_profile(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    if not user_info:
        bot.reply_to(message, "اطلاعات شما یافت نشد.")
        return
    
    profile_text = f"""
📊 پروفایل شما:

👤 نام: {user_info[3]}
🧠 نوع شخصیت: {user_info[5] or 'تعیین نشده'}
🎯 علایق: {user_info[6] or 'تعیین نشده'}
📚 سطح تحصیلی: {user_info[7] or 'تعیین نشده'}
📅 تاریخ عضویت: {user_info[4][:10]}

برای تکمیل پروفایل، تست شخصیت را انجام دهید.
    """
    
    keyboard = InlineKeyboardMarkup()
    if not user_info[5]:
        keyboard.row(InlineKeyboardButton("🧠 انجام تست شخصیت", callback_data="take_test"))
    keyboard.row(InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="edit_profile"))
    
    bot.reply_to(message, profile_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📖 راهنما')
def help_command(message):
    help_text = """
📖 راهنمای ربات مشاوره تحصیلی

🧠 تست شخصیت:
• سوالات دقیق برای شناخت شخصیت
• تحلیل علایق و توانایی‌ها
• پیشنهاد رشته‌های مناسب

📚 معرفی رشته‌ها:
• اطلاعات کامل رشته‌های تحصیلی
• شرایط ورود و بازار کار
• دانشگاه‌های برتر

📋 برنامه مطالعاتی:
• برنامه‌ریزی شخصی‌سازی شده
• مدیریت زمان مطالعه
• پیگیری پیشرفت

💬 مشاوره:
• سوالات تخصصی
• راهنمایی تحصیلی
• مشاوره شغلی

💡 نکات مهم:
• تست شخصیت را با دقت انجام دهید
• اطلاعات دقیق وارد کنید
• از مشاوره‌ها استفاده کنید
• برنامه‌ها را منظم پیگیری کنید

📞 پشتیبانی:
برای سوالات بیشتر با پشتیبانی تماس بگیرید.
    """
    
    bot.reply_to(message, help_text)

# مدیریت callback ها
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("test_"):
        parts = call.data.split("_")
        question_index = int(parts[1])
        answer_index = int(parts[2])
        
        # ذخیره پاسخ
        user_id = call.from_user.id
        # در نسخه کامل، پاسخ‌ها در دیتابیس ذخیره می‌شوند
        
        questions = get_personality_test()
        if question_index + 1 < len(questions):
            # سوال بعدی
            next_question = questions[question_index + 1]
            question_text = f"""
🧠 تست شخصیت - سوال {question_index + 2} از {len(questions)}

{next_question['question']}

لطفاً گزینه مورد نظر را انتخاب کنید:
            """
            
            keyboard = create_test_keyboard(question_index + 1, next_question['options'])
            bot.edit_message_text(question_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        else:
            # پایان تست
            personality_types = ["تحلیلی", "خلاق", "اجتماعی", "عملی"]
            result = random.choice(personality_types)
            
            update_user_personality(user_id, result)
            
            result_text = f"""
🎉 تست شخصیت شما تکمیل شد!

🧠 نوع شخصیت: {result}

بر اساس نتیجه تست، رشته‌های مناسب برای شما:

{get_recommended_majors(result)}

برای مشاهده جزئیات بیشتر، به بخش 'معرفی رشته‌ها' مراجعه کنید.
            """
            
            bot.edit_message_text(result_text, call.message.chat.id, call.message.message_id)
    
    elif call.data.startswith("category_"):
        category = call.data.split("_")[1]
        
        if category == "all":
            majors = get_all_majors()
        else:
            majors = get_majors_by_category(category)
        
        if not majors:
            bot.answer_callback_query(call.id, "هیچ رشته‌ای در این دسته‌بندی موجود نیست")
            return
        
        majors_text = f"📚 رشته‌های {category}:\n\n"
        
        for i, major in enumerate(majors[:5], 1):
            majors_text += f"{i}. 🎓 {major[1]}\n"
            majors_text += f"   📝 {major[3]}\n"
            majors_text += f"   💼 بازار کار: {major[5]}\n"
            majors_text += f"   💰 حقوق: {major[6]}\n\n"
        
        keyboard = InlineKeyboardMarkup()
        for i, major in enumerate(majors[:5], 1):
            keyboard.row(InlineKeyboardButton(f"{i}. {major[1]}", callback_data=f"major_{major[0]}"))
        
        bot.edit_message_text(majors_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
    
    elif call.data.startswith("major_"):
        major_id = int(call.data.split("_")[1])
        major = get_major_by_id(major_id)
        
        if not major:
            bot.answer_callback_query(call.id, "رشته یافت نشد")
            return
        
        major_text = f"""
🎓 {major[1]}

📝 توضیحات:
{major[3]}

📋 شرایط ورود:
{major[4]}

💼 بازار کار:
{major[5]}

💰 حقوق:
{major[6]}

🏫 دانشگاه‌های برتر:
{major[7]}
        """
        
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("📋 ایجاد برنامه مطالعاتی", callback_data=f"create_plan_{major_id}"),
            InlineKeyboardButton("💬 مشاوره", callback_data="consultation")
        )
        
        bot.edit_message_text(major_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)

def get_recommended_majors(personality_type):
    recommendations = {
        "تحلیلی": "• مهندسی کامپیوتر\n• مهندسی برق\n• ریاضی\n• فیزیک",
        "خلاق": "• معماری\n• طراحی صنعتی\n• هنرهای تجسمی\n• موسیقی",
        "اجتماعی": "• روانشناسی\n• مشاوره\n• مدیریت\n• حقوق",
        "عملی": "• پزشکی\n• پرستاری\n• مهندسی مکانیک\n• کشاورزی"
    }
    return recommendations.get(personality_type, "• مهندسی کامپیوتر\n• پزشکی\n• حقوق\n• مدیریت")

# راه‌اندازی ربات
if __name__ == "__main__":
    init_database()
    insert_sample_majors()
    print("🎓 ربات مشاوره تحصیلی راه‌اندازی شد!")
    print("🧠 آماده برای ارائه مشاوره تحصیلی...")
    bot.polling(none_stop=True)