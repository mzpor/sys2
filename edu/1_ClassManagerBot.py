 # ربات مدیریت کلاس درس
# ClassManagerBot - مدیریت حضور و غیاب، تکالیف، نمرات
# توسعه‌دهنده: محمد زارع‌پور

import telebot
import json
import datetime
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# تنظیمات اولیه
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(BOT_TOKEN)

# دیتابیس
def init_database():
    conn = sqlite3.connect('class_manager.db')
    cursor = conn.cursor()
    
    # جدول کلاس‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            description TEXT,
            created_date TEXT
        )
    ''')
    
    # جدول دانش‌آموزان
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            name TEXT NOT NULL,
            class_id INTEGER,
            join_date TEXT,
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')
    
    # جدول حضور و غیاب
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY,
            student_id INTEGER,
            class_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')
    
    # جدول تکالیف
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS homework (
            id INTEGER PRIMARY KEY,
            class_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            created_date TEXT,
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')
    
    # جدول نمرات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY,
            student_id INTEGER,
            homework_id INTEGER,
            grade REAL,
            comment TEXT,
            date TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (homework_id) REFERENCES homework (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# کلیدهای میانبر
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('📚 کلاس‌های من', '👥 دانش‌آموزان')
    keyboard.row('📝 تکالیف', '📊 نمرات')
    keyboard.row('✅ حضور و غیاب', '📈 گزارش‌ها')
    keyboard.row('⚙️ تنظیمات', '❓ راهنما')
    return keyboard

def create_teacher_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('➕ ایجاد کلاس جدید', '📚 کلاس‌های من')
    keyboard.row('👥 مدیریت دانش‌آموزان', '📝 مدیریت تکالیف')
    keyboard.row('📊 مدیریت نمرات', '📈 گزارش‌ها')
    keyboard.row('⚙️ تنظیمات', '❓ راهنما')
    return keyboard

# مدیریت کلاس‌ها
def create_class(teacher_id, name, description):
    conn = sqlite3.connect('class_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO classes (name, teacher_id, description, created_date)
        VALUES (?, ?, ?, ?)
    ''', (name, teacher_id, description, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_teacher_classes(teacher_id):
    conn = sqlite3.connect('class_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM classes WHERE teacher_id = ?', (teacher_id,))
    classes = cursor.fetchall()
    conn.close()
    return classes

# مدیریت دانش‌آموزان
def add_student(user_id, name, class_id):
    conn = sqlite3.connect('class_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO students (user_id, name, class_id, join_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, name, class_id, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_class_students(class_id):
    conn = sqlite3.connect('class_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE class_id = ?', (class_id,))
    students = cursor.fetchall()
    conn.close()
    return students

# مدیریت حضور و غیاب
def mark_attendance(student_id, class_id, status):
    conn = sqlite3.connect('class_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO attendance (student_id, class_id, date, status)
        VALUES (?, ?, ?, ?)
    ''', (student_id, class_id, datetime.datetime.now().date().isoformat(), status))
    conn.commit()
    conn.close()

def get_attendance_report(class_id, date):
    conn = sqlite3.connect('class_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.name, a.status 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id 
        WHERE a.class_id = ? AND a.date = ?
    ''', (class_id, date))
    attendance = cursor.fetchall()
    conn.close()
    return attendance

# مدیریت تکالیف
def create_homework(class_id, title, description, due_date):
    conn = sqlite3.connect('class_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO homework (class_id, title, description, due_date, created_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (class_id, title, description, due_date, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_class_homework(class_id):
    conn = sqlite3.connect('class_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM homework WHERE class_id = ? ORDER BY created_date DESC', (class_id,))
    homework = cursor.fetchall()
    conn.close()
    return homework

# مدیریت نمرات
def add_grade(student_id, homework_id, grade, comment):
    conn = sqlite3.connect('class_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO grades (student_id, homework_id, grade, comment, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (student_id, homework_id, grade, comment, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_student_grades(student_id):
    conn = sqlite3.connect('class_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT h.title, g.grade, g.comment, g.date
        FROM grades g
        JOIN homework h ON g.homework_id = h.id
        WHERE g.student_id = ?
        ORDER BY g.date DESC
    ''', (student_id,))
    grades = cursor.fetchall()
    conn.close()
    return grades

# دستورات ربات
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    welcome_text = f"""
🎓 سلام {user_name} عزیز!

به ربات مدیریت کلاس درس خوش آمدید! 📚

این ربات به شما کمک می‌کند تا:
• کلاس‌های خود را مدیریت کنید
• حضور و غیاب دانش‌آموزان را ثبت کنید
• تکالیف را مدیریت کنید
• نمرات را ثبت و پیگیری کنید
• گزارش‌های دقیق دریافت کنید

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    bot.reply_to(message, welcome_text, reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '➕ ایجاد کلاس جدید')
def create_new_class(message):
    msg = bot.reply_to(message, "لطفاً نام کلاس را وارد کنید:")
    bot.register_next_step_handler(msg, process_class_name)

def process_class_name(message):
    class_name = message.text
    msg = bot.reply_to(message, "لطفاً توضیحات کلاس را وارد کنید:")
    bot.register_next_step_handler(msg, process_class_description, class_name)

def process_class_description(message, class_name):
    description = message.text
    teacher_id = message.from_user.id
    
    create_class(teacher_id, class_name, description)
    
    success_text = f"""
✅ کلاس جدید با موفقیت ایجاد شد!

📚 نام کلاس: {class_name}
📝 توضیحات: {description}

حالا می‌توانید دانش‌آموزان را به کلاس اضافه کنید.
    """
    
    bot.reply_to(message, success_text, reply_markup=create_teacher_keyboard())

@bot.message_handler(func=lambda message: message.text == '📚 کلاس‌های من')
def show_my_classes(message):
    teacher_id = message.from_user.id
    classes = get_teacher_classes(teacher_id)
    
    if not classes:
        bot.reply_to(message, "هنوز هیچ کلاسی ایجاد نکرده‌اید.")
        return
    
    classes_text = "📚 کلاس‌های شما:\n\n"
    for i, class_info in enumerate(classes, 1):
        classes_text += f"{i}. {class_info[1]}\n"
        classes_text += f"   📝 {class_info[3]}\n"
        classes_text += f"   📅 تاریخ ایجاد: {class_info[4][:10]}\n\n"
    
    bot.reply_to(message, classes_text)

@bot.message_handler(func=lambda message: message.text == '✅ حضور و غیاب')
def attendance_menu(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📝 ثبت حضور", callback_data="mark_attendance"),
        InlineKeyboardButton("📊 گزارش حضور", callback_data="attendance_report")
    )
    keyboard.row(
        InlineKeyboardButton("📈 آمار حضور", callback_data="attendance_stats")
    )
    
    bot.reply_to(message, "🎯 مدیریت حضور و غیاب\n\nلطفاً گزینه مورد نظر را انتخاب کنید:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📝 تکالیف')
def homework_menu(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("➕ تکلیف جدید", callback_data="new_homework"),
        InlineKeyboardButton("📚 لیست تکالیف", callback_data="list_homework")
    )
    keyboard.row(
        InlineKeyboardButton("📊 نمره‌دهی", callback_data="grade_homework")
    )
    
    bot.reply_to(message, "📝 مدیریت تکالیف\n\nلطفاً گزینه مورد نظر را انتخاب کنید:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📊 نمرات')
def grades_menu(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📈 گزارش نمرات", callback_data="grades_report"),
        InlineKeyboardButton("📊 آمار کلاس", callback_data="class_stats")
    )
    keyboard.row(
        InlineKeyboardButton("📋 کارنامه", callback_data="student_report_card")
    )
    
    bot.reply_to(message, "📊 مدیریت نمرات\n\nلطفاً گزینه مورد نظر را انتخاب کنید:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📈 گزارش‌ها')
def reports_menu(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📊 گزارش کلاس", callback_data="class_report"),
        InlineKeyboardButton("👥 گزارش دانش‌آموز", callback_data="student_report")
    )
    keyboard.row(
        InlineKeyboardButton("📈 گزارش پیشرفت", callback_data="progress_report"),
        InlineKeyboardButton("📋 گزارش جامع", callback_data="comprehensive_report")
    )
    
    bot.reply_to(message, "📈 گزارش‌ها\n\nلطفاً نوع گزارش مورد نظر را انتخاب کنید:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '❓ راهنما')
def help_command(message):
    help_text = """
❓ راهنمای استفاده از ربات مدیریت کلاس

🎯 قابلیت‌های اصلی:
• ایجاد و مدیریت کلاس‌ها
• ثبت حضور و غیاب دانش‌آموزان
• مدیریت تکالیف و نمرات
• تولید گزارش‌های مختلف

📚 دستورات مهم:
/start - شروع ربات
/help - نمایش راهنما
/classes - مشاهده کلاس‌ها
/students - لیست دانش‌آموزان
/homework - مدیریت تکالیف
/grades - مدیریت نمرات
/reports - گزارش‌ها

💡 نکات مهم:
• ابتدا کلاس ایجاد کنید
• دانش‌آموزان را به کلاس اضافه کنید
• تکالیف را منظم ارسال کنید
• نمرات را به موقع ثبت کنید
• گزارش‌ها را بررسی کنید

📞 پشتیبانی:
برای سوالات بیشتر با پشتیبانی تماس بگیرید.
    """
    
    bot.reply_to(message, help_text)

# مدیریت callback ها
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "mark_attendance":
        bot.answer_callback_query(call.id, "لطفاً دانش‌آموز و وضعیت حضور را انتخاب کنید")
        # کد مربوط به ثبت حضور
        
    elif call.data == "attendance_report":
        bot.answer_callback_query(call.id, "گزارش حضور در حال تهیه...")
        # کد مربوط به گزارش حضور
        
    elif call.data == "new_homework":
        bot.answer_callback_query(call.id, "لطفاً اطلاعات تکلیف را وارد کنید")
        # کد مربوط به ایجاد تکلیف جدید

# راه‌اندازی ربات
if __name__ == "__main__":
    init_database()
    print("🤖 ربات مدیریت کلاس درس راه‌اندازی شد!")
    print("📚 آماده برای مدیریت کلاس‌های شما...")
    bot.polling(none_stop=True)