 # ربات کلاس آنلاین
# OnlineClassBot - برگزاری کلاس‌های آنلاین
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
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            role TEXT DEFAULT 'student',
            join_date TEXT
        )
    ''')
    
    # جدول کلاس‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            subject TEXT,
            teacher_id INTEGER,
            description TEXT,
            schedule TEXT,
            duration INTEGER DEFAULT 60,
            max_students INTEGER DEFAULT 30,
            status TEXT DEFAULT 'scheduled',
            created_date TEXT,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')
    
    # جدول جلسات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            class_id INTEGER,
            session_number INTEGER,
            start_time TEXT,
            end_time TEXT,
            status TEXT DEFAULT 'scheduled',
            topic TEXT,
            materials TEXT,
            created_date TEXT,
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')
    
    # جدول حضور و غیاب
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY,
            session_id INTEGER,
            user_id INTEGER,
            status TEXT DEFAULT 'present',
            join_time TEXT,
            leave_time TEXT,
            duration INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # جدول ثبت‌نام دانش‌آموزان
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY,
            class_id INTEGER,
            user_id INTEGER,
            enrollment_date TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (class_id) REFERENCES classes (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # جدول فایل‌های کلاس
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS class_files (
            id INTEGER PRIMARY KEY,
            class_id INTEGER,
            session_id INTEGER,
            file_name TEXT,
            file_id TEXT,
            file_type TEXT,
            uploaded_by INTEGER,
            upload_date TEXT,
            FOREIGN KEY (class_id) REFERENCES classes (id),
            FOREIGN KEY (session_id) REFERENCES sessions (id),
            FOREIGN KEY (uploaded_by) REFERENCES users (id)
        )
    ''')
    
    # جدول چت‌های کلاس
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS class_chats (
            id INTEGER PRIMARY KEY,
            session_id INTEGER,
            user_id INTEGER,
            message TEXT,
            message_type TEXT DEFAULT 'text',
            timestamp TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# مدیریت کاربران
def add_user(user_id, username, first_name, role='student'):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, role, join_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, role, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_info(user_id):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def is_teacher(user_id):
    user_info = get_user_info(user_id)
    return user_info and user_info[4] == 'teacher'

# مدیریت کلاس‌ها
def create_class(title, subject, teacher_id, description, schedule, duration, max_students):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO classes (title, subject, teacher_id, description, schedule, duration, max_students, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, subject, teacher_id, description, schedule, duration, max_students, 
          datetime.datetime.now().isoformat()))
    class_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return class_id

def get_teacher_classes(teacher_id):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM classes WHERE teacher_id = ? ORDER BY created_date DESC', (teacher_id,))
    classes = cursor.fetchall()
    conn.close()
    return classes

def get_student_classes(user_id):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, e.enrollment_date
        FROM classes c
        JOIN enrollments e ON c.id = e.class_id
        WHERE e.user_id = ? AND e.status = 'active'
        ORDER BY c.created_date DESC
    ''', (user_id,))
    classes = cursor.fetchall()
    conn.close()
    return classes

def get_class_by_id(class_id):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM classes WHERE id = ?', (class_id,))
    class_info = cursor.fetchone()
    conn.close()
    return class_info

# مدیریت جلسات
def create_session(class_id, session_number, start_time, topic, materials):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (class_id, session_number, start_time, topic, materials, created_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (class_id, session_number, start_time, topic, materials, 
          datetime.datetime.now().isoformat()))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_class_sessions(class_id):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions WHERE class_id = ? ORDER BY session_number', (class_id,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_session_by_id(session_id):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = cursor.fetchone()
    conn.close()
    return session

# مدیریت حضور و غیاب
def mark_attendance(session_id, user_id, status='present'):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    
    # بررسی حضور قبلی
    cursor.execute('SELECT id FROM attendance WHERE session_id = ? AND user_id = ?', (session_id, user_id))
    existing = cursor.fetchone()
    
    if existing:
        # به‌روزرسانی حضور موجود
        cursor.execute('''
            UPDATE attendance SET status = ?, join_time = ?
            WHERE session_id = ? AND user_id = ?
        ''', (status, datetime.datetime.now().isoformat(), session_id, user_id))
    else:
        # ثبت حضور جدید
        cursor.execute('''
            INSERT INTO attendance (session_id, user_id, status, join_time)
            VALUES (?, ?, ?, ?)
        ''', (session_id, user_id, status, datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_session_attendance(session_id):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, u.first_name
        FROM attendance a
        JOIN users u ON a.user_id = u.user_id
        WHERE a.session_id = ?
        ORDER BY a.join_time
    ''', (session_id,))
    attendance = cursor.fetchall()
    conn.close()
    return attendance

# مدیریت ثبت‌نام
def enroll_student(class_id, user_id):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    
    # بررسی ثبت‌نام قبلی
    cursor.execute('SELECT id FROM enrollments WHERE class_id = ? AND user_id = ?', (class_id, user_id))
    existing = cursor.fetchone()
    
    if not existing:
        cursor.execute('''
            INSERT INTO enrollments (class_id, user_id, enrollment_date)
            VALUES (?, ?, ?)
        ''', (class_id, user_id, datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_class_students(class_id):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.first_name, e.enrollment_date, e.status
        FROM enrollments e
        JOIN users u ON e.user_id = u.user_id
        WHERE e.class_id = ? AND e.status = 'active'
        ORDER BY e.enrollment_date
    ''', (class_id,))
    students = cursor.fetchall()
    conn.close()
    return students

# مدیریت فایل‌ها
def save_class_file(class_id, session_id, file_name, file_id, file_type, uploaded_by):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO class_files (class_id, session_id, file_name, file_id, file_type, uploaded_by, upload_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (class_id, session_id, file_name, file_id, file_type, uploaded_by, 
          datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_class_files(class_id, session_id=None):
    conn = sqlite3.connect('online_class.db')
    cursor = conn.cursor()
    
    if session_id:
        cursor.execute('''
            SELECT * FROM class_files 
            WHERE class_id = ? AND session_id = ?
            ORDER BY upload_date DESC
        ''', (class_id, session_id))
    else:
        cursor.execute('''
            SELECT * FROM class_files 
            WHERE class_id = ?
            ORDER BY upload_date DESC
        ''', (class_id,))
    
    files = cursor.fetchall()
    conn.close()
    return files

# کلیدهای میانبر
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('📚 کلاس‌های من', '➕ ایجاد کلاس')
    keyboard.row('📅 جلسات', '✅ حضور و غیاب')
    keyboard.row('📁 فایل‌ها', '💬 چت کلاس')
    keyboard.row('📊 گزارش‌ها', '📖 راهنما')
    return keyboard

def create_teacher_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('📚 کلاس‌های من', '➕ ایجاد کلاس جدید')
    keyboard.row('📅 مدیریت جلسات', '✅ حضور و غیاب')
    keyboard.row('👥 مدیریت دانش‌آموزان', '📁 فایل‌ها')
    keyboard.row('📊 گزارش‌ها', '📖 راهنما')
    return keyboard

def create_class_keyboard(class_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📅 جلسات", callback_data=f"class_sessions_{class_id}"),
        InlineKeyboardButton("👥 دانش‌آموزان", callback_data=f"class_students_{class_id}")
    )
    keyboard.row(
        InlineKeyboardButton("📁 فایل‌ها", callback_data=f"class_files_{class_id}"),
        InlineKeyboardButton("💬 چت", callback_data=f"class_chat_{class_id}")
    )
    keyboard.row(
        InlineKeyboardButton("✏️ ویرایش", callback_data=f"edit_class_{class_id}"),
        InlineKeyboardButton("❌ حذف", callback_data=f"delete_class_{class_id}")
    )
    return keyboard

def create_session_keyboard(session_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("✅ شروع جلسه", callback_data=f"start_session_{session_id}"),
        InlineKeyboardButton("⏹️ پایان جلسه", callback_data=f"end_session_{session_id}")
    )
    keyboard.row(
        InlineKeyboardButton("📁 فایل‌ها", callback_data=f"session_files_{session_id}"),
        InlineKeyboardButton("📊 حضور و غیاب", callback_data=f"session_attendance_{session_id}")
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
📚 سلام {first_name} عزیز!

به ربات کلاس آنلاین خوش آمدید! 🎓

این ربات به شما کمک می‌کند تا:
• کلاس‌های آنلاین برگزار کنید
• جلسات را مدیریت کنید
• حضور و غیاب ثبت کنید
• فایل‌ها را به اشتراک بگذارید

🎯 ویژگی‌ها:
• مدیریت کلاس‌های آنلاین
• ثبت حضور و غیاب
• اشتراک‌گذاری فایل
• چت کلاسی
• گزارش‌گیری دقیق

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    if is_teacher(user_id):
        bot.reply_to(message, welcome_text, reply_markup=create_teacher_keyboard())
    else:
        bot.reply_to(message, welcome_text, reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '📚 کلاس‌های من')
def my_classes(message):
    user_id = message.from_user.id
    
    if is_teacher(user_id):
        classes = get_teacher_classes(user_id)
        role = "استاد"
    else:
        classes = get_student_classes(user_id)
        role = "دانش‌آموز"
    
    if not classes:
        bot.reply_to(message, f"شما هنوز هیچ کلاسی {role} نیستید.")
        return
    
    classes_text = f"📚 کلاس‌های شما ({role}):\n\n"
    
    for i, class_info in enumerate(classes, 1):
        status_emoji = "🟢" if class_info[8] == 'active' else "🔴"
        classes_text += f"{i}. {status_emoji} {class_info[1]}\n"
        classes_text += f"   📖 موضوع: {class_info[2]}\n"
        classes_text += f"   📅 برنامه: {class_info[5]}\n"
        classes_text += f"   ⏰ مدت: {class_info[6]} دقیقه\n"
        classes_text += f"   👥 حداکثر: {class_info[7]} نفر\n\n"
    
    keyboard = InlineKeyboardMarkup()
    for i, class_info in enumerate(classes[:5], 1):
        keyboard.row(InlineKeyboardButton(f"{i}. {class_info[1]}", callback_data=f"class_{class_info[0]}"))
    
    bot.reply_to(message, classes_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '➕ ایجاد کلاس')
def create_new_class(message):
    if not is_teacher(message.from_user.id):
        bot.reply_to(message, "فقط استادان می‌توانند کلاس جدید ایجاد کنند.")
        return
    
    msg = bot.reply_to(message, "📚 لطفاً عنوان کلاس را وارد کنید:")
    bot.register_next_step_handler(msg, process_class_title)

def process_class_title(message):
    title = message.text
    msg = bot.reply_to(message, "📖 لطفاً موضوع کلاس را وارد کنید:")
    bot.register_next_step_handler(msg, process_class_subject, title)

def process_class_subject(message, title):
    subject = message.text
    msg = bot.reply_to(message, "📝 لطفاً توضیحات کلاس را وارد کنید:")
    bot.register_next_step_handler(msg, process_class_description, title, subject)

def process_class_description(message, title, subject):
    description = message.text
    msg = bot.reply_to(message, "📅 لطفاً برنامه کلاس را وارد کنید (مثال: دوشنبه‌ها ساعت 10:00):")
    bot.register_next_step_handler(msg, process_class_schedule, title, subject, description)

def process_class_schedule(message, title, subject, description):
    schedule = message.text
    msg = bot.reply_to(message, "⏰ لطفاً مدت کلاس را به دقیقه وارد کنید:")
    bot.register_next_step_handler(msg, process_class_duration, title, subject, description, schedule)

def process_class_duration(message, title, subject, description, schedule):
    try:
        duration = int(message.text)
        msg = bot.reply_to(message, "👥 لطفاً حداکثر تعداد دانش‌آموزان را وارد کنید:")
        bot.register_next_step_handler(msg, process_class_max_students, title, subject, description, schedule, duration)
    except ValueError:
        bot.reply_to(message, "لطفاً عدد صحیح وارد کنید.")
        return

def process_class_max_students(message, title, subject, description, schedule, duration):
    try:
        max_students = int(message.text)
        teacher_id = message.from_user.id
        
        class_id = create_class(title, subject, teacher_id, description, schedule, duration, max_students)
        
        success_text = f"""
✅ کلاس جدید با موفقیت ایجاد شد!

📚 عنوان: {title}
📖 موضوع: {subject}
📝 توضیحات: {description}
📅 برنامه: {schedule}
⏰ مدت: {duration} دقیقه
👥 حداکثر دانش‌آموز: {max_students}

حالا می‌توانید جلسات را برنامه‌ریزی کنید.
        """
        
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("📅 ایجاد جلسه", callback_data=f"create_session_{class_id}"),
            InlineKeyboardButton("👥 مدیریت دانش‌آموزان", callback_data=f"manage_students_{class_id}")
        )
        
        bot.reply_to(message, success_text, reply_markup=keyboard)
    except ValueError:
        bot.reply_to(message, "لطفاً عدد صحیح وارد کنید.")

@bot.message_handler(func=lambda message: message.text == '📅 جلسات')
def sessions_menu(message):
    user_id = message.from_user.id
    
    if is_teacher(user_id):
        classes = get_teacher_classes(user_id)
    else:
        classes = get_student_classes(user_id)
    
    if not classes:
        bot.reply_to(message, "شما در هیچ کلاسی عضو نیستید.")
        return
    
    sessions_text = "📅 جلسات کلاس‌های شما:\n\n"
    
    for class_info in classes:
        sessions = get_class_sessions(class_info[0])
        if sessions:
            sessions_text += f"📚 {class_info[1]}:\n"
            for session in sessions[:3]:  # فقط 3 جلسه آخر
                status_emoji = "🟢" if session[5] == 'active' else "🔴"
                sessions_text += f"  {status_emoji} جلسه {session[2]}: {session[6]}\n"
                sessions_text += f"  📅 {session[3][:10]} ساعت {session[3][11:16]}\n"
            sessions_text += "\n"
    
    if not any(get_class_sessions(c[0]) for c in classes):
        sessions_text = "هنوز هیچ جلسه‌ای برنامه‌ریزی نشده است."
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📅 برنامه‌ریزی جلسه", callback_data="schedule_session"),
        InlineKeyboardButton("📊 گزارش جلسات", callback_data="sessions_report")
    )
    
    bot.reply_to(message, sessions_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '✅ حضور و غیاب')
def attendance_menu(message):
    user_id = message.from_user.id
    
    if not is_teacher(user_id):
        bot.reply_to(message, "فقط استادان می‌توانند حضور و غیاب را مدیریت کنند.")
        return
    
    classes = get_teacher_classes(user_id)
    
    if not classes:
        bot.reply_to(message, "شما هیچ کلاسی ندارید.")
        return
    
    attendance_text = "✅ مدیریت حضور و غیاب\n\n"
    attendance_text += "لطفاً کلاس مورد نظر را انتخاب کنید:\n\n"
    
    for i, class_info in enumerate(classes, 1):
        attendance_text += f"{i}. 📚 {class_info[1]}\n"
    
    keyboard = InlineKeyboardMarkup()
    for i, class_info in enumerate(classes[:5], 1):
        keyboard.row(InlineKeyboardButton(f"{i}. {class_info[1]}", callback_data=f"attendance_class_{class_info[0]}"))
    
    bot.reply_to(message, attendance_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📁 فایل‌ها')
def files_menu(message):
    user_id = message.from_user.id
    
    if is_teacher(user_id):
        classes = get_teacher_classes(user_id)
    else:
        classes = get_student_classes(user_id)
    
    if not classes:
        bot.reply_to(message, "شما در هیچ کلاسی عضو نیستید.")
        return
    
    files_text = "📁 فایل‌های کلاس‌های شما:\n\n"
    
    for class_info in classes:
        files = get_class_files(class_info[0])
        if files:
            files_text += f"📚 {class_info[1]}:\n"
            for file in files[:3]:  # فقط 3 فایل آخر
                files_text += f"  📄 {file[3]}\n"
                files_text += f"  👤 آپلود شده توسط: {get_user_info(file[6])[3]}\n"
                files_text += f"  📅 {file[7][:10]}\n"
            files_text += "\n"
    
    if not any(get_class_files(c[0]) for c in classes):
        files_text = "هنوز هیچ فایلی آپلود نشده است."
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📤 آپلود فایل", callback_data="upload_file"),
        InlineKeyboardButton("📥 دانلود فایل", callback_data="download_file")
    )
    keyboard.row(
        InlineKeyboardButton("📋 لیست فایل‌ها", callback_data="list_files")
    )
    
    bot.reply_to(message, files_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '💬 چت کلاس')
def chat_menu(message):
    user_id = message.from_user.id
    
    if is_teacher(user_id):
        classes = get_teacher_classes(user_id)
    else:
        classes = get_student_classes(user_id)
    
    if not classes:
        bot.reply_to(message, "شما در هیچ کلاسی عضو نیستید.")
        return
    
    chat_text = "💬 چت کلاس‌های شما:\n\n"
    
    for i, class_info in enumerate(classes, 1):
        chat_text += f"{i}. 📚 {class_info[1]}\n"
        chat_text += f"   👥 {len(get_class_students(class_info[0]))} دانش‌آموز\n"
        chat_text += f"   💬 چت فعال\n\n"
    
    keyboard = InlineKeyboardMarkup()
    for i, class_info in enumerate(classes[:5], 1):
        keyboard.row(InlineKeyboardButton(f"{i}. {class_info[1]}", callback_data=f"chat_class_{class_info[0]}"))
    
    bot.reply_to(message, chat_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📊 گزارش‌ها')
def reports_menu(message):
    reports_text = """
📊 گزارش‌های موجود:

📈 گزارش حضور و غیاب
📅 گزارش جلسات
👥 گزارش دانش‌آموزان
📁 گزارش فایل‌ها
⏰ گزارش زمانی
📊 گزارش کلی

لطفاً نوع گزارش مورد نظر را انتخاب کنید:
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📈 حضور و غیاب", callback_data="report_attendance"),
        InlineKeyboardButton("📅 جلسات", callback_data="report_sessions")
    )
    keyboard.row(
        InlineKeyboardButton("👥 دانش‌آموزان", callback_data="report_students"),
        InlineKeyboardButton("📁 فایل‌ها", callback_data="report_files")
    )
    keyboard.row(
        InlineKeyboardButton("⏰ زمانی", callback_data="report_time"),
        InlineKeyboardButton("📊 کلی", callback_data="report_overall")
    )
    
    bot.reply_to(message, reports_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📖 راهنما')
def help_command(message):
    help_text = """
📖 راهنمای ربات کلاس آنلاین

📚 کلاس‌های من:
• مشاهده کلاس‌های عضو شده
• دسترسی به جزئیات کلاس
• مدیریت جلسات و فایل‌ها

➕ ایجاد کلاس:
• ایجاد کلاس جدید (فقط استادان)
• تعیین عنوان و موضوع
• تنظیم برنامه و مدت

📅 جلسات:
• برنامه‌ریزی جلسات
• مدیریت زمان‌بندی
• شروع و پایان جلسات

✅ حضور و غیاب:
• ثبت حضور دانش‌آموزان
• گزارش حضور و غیاب
• پیگیری غیبت‌ها

📁 فایل‌ها:
• آپلود فایل‌های کلاس
• دانلود فایل‌های مشترک
• مدیریت مستندات

💬 چت کلاس:
• چت گروهی کلاس
• پرسش و پاسخ
• اشتراک‌گذاری مطالب

📊 گزارش‌ها:
• گزارش حضور و غیاب
• گزارش جلسات
• گزارش دانش‌آموزان

💡 نکات مهم:
• جلسات را منظم برگزار کنید
• حضور و غیاب را ثبت کنید
• فایل‌ها را به اشتراک بگذارید
• با دانش‌آموزان تعامل کنید

📞 پشتیبانی:
برای سوالات بیشتر با پشتیبانی تماس بگیرید.
    """
    
    bot.reply_to(message, help_text)

# مدیریت callback ها
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("class_"):
        class_id = int(call.data.split("_")[1])
        class_info = get_class_by_id(class_id)
        
        if not class_info:
            bot.answer_callback_query(call.id, "کلاس یافت نشد")
            return
        
        class_text = f"""
📚 {class_info[1]}

📖 موضوع: {class_info[2]}
📝 توضیحات: {class_info[4]}
📅 برنامه: {class_info[5]}
⏰ مدت: {class_info[6]} دقیقه
👥 حداکثر دانش‌آموز: {class_info[7]}
📊 وضعیت: {class_info[8]}
📅 تاریخ ایجاد: {class_info[9][:10]}
        """
        
        bot.edit_message_text(class_text, call.message.chat.id, call.message.message_id,
                             reply_markup=create_class_keyboard(class_id))
    
    elif call.data.startswith("start_session_"):
        session_id = int(call.data.split("_")[2])
        # شروع جلسه
        bot.answer_callback_query(call.id, "جلسه شروع شد!")
        bot.edit_message_text("🟢 جلسه فعال است. دانش‌آموزان می‌توانند وارد شوند.", 
                             call.message.chat.id, call.message.message_id)

# راه‌اندازی ربات
if __name__ == "__main__":
    init_database()
    print("📚 ربات کلاس آنلاین راه‌اندازی شد!")
    print("🎓 آماده برای برگزاری کلاس‌های آنلاین...")
    bot.polling(none_stop=True)