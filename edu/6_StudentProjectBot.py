 # ربات مدیریت پروژه‌های دانش‌آموزی
# StudentProjectBot - مدیریت پروژه‌های علمی و تحقیقاتی
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
    conn = sqlite3.connect('student_projects.db')
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
    
    # جدول پروژه‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            supervisor_id INTEGER,
            status TEXT DEFAULT 'active',
            start_date TEXT,
            end_date TEXT,
            created_date TEXT,
            FOREIGN KEY (supervisor_id) REFERENCES users (id)
        )
    ''')
    
    # جدول اعضای پروژه
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_members (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            user_id INTEGER,
            role TEXT DEFAULT 'member',
            join_date TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # جدول وظایف
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            assigned_to INTEGER,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'medium',
            due_date TEXT,
            created_date TEXT,
            completed_date TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (assigned_to) REFERENCES users (id)
        )
    ''')
    
    # جدول پیشرفت
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            task_id INTEGER,
            user_id INTEGER,
            progress_percentage INTEGER DEFAULT 0,
            notes TEXT,
            update_date TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (task_id) REFERENCES tasks (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # جدول فایل‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_files (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            file_name TEXT,
            file_id TEXT,
            file_type TEXT,
            uploaded_by INTEGER,
            upload_date TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (uploaded_by) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# مدیریت کاربران
def add_user(user_id, username, first_name, role='student'):
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, role, join_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, role, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_info(user_id):
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def is_supervisor(user_id):
    user_info = get_user_info(user_id)
    return user_info and user_info[4] == 'supervisor'

# مدیریت پروژه‌ها
def create_project(title, description, category, supervisor_id):
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO projects (title, description, category, supervisor_id, start_date, created_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, description, category, supervisor_id, datetime.datetime.now().isoformat(), 
          datetime.datetime.now().isoformat()))
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id

def get_user_projects(user_id):
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, pm.role as member_role
        FROM projects p
        JOIN project_members pm ON p.id = pm.project_id
        WHERE pm.user_id = ?
        ORDER BY p.created_date DESC
    ''', (user_id,))
    projects = cursor.fetchall()
    conn.close()
    return projects

def get_project_by_id(project_id):
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    conn.close()
    return project

def get_project_members(project_id):
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.first_name, pm.role
        FROM project_members pm
        JOIN users u ON pm.user_id = u.user_id
        WHERE pm.project_id = ?
    ''', (project_id,))
    members = cursor.fetchall()
    conn.close()
    return members

# مدیریت وظایف
def create_task(project_id, title, description, assigned_to, priority, due_date):
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (project_id, title, description, assigned_to, priority, due_date, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, title, description, assigned_to, priority, due_date, 
          datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_project_tasks(project_id):
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, u.first_name as assigned_to_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.user_id
        WHERE t.project_id = ?
        ORDER BY t.priority DESC, t.due_date ASC
    ''', (project_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_task_status(task_id, status):
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()
    if status == 'completed':
        cursor.execute('''
            UPDATE tasks SET status = ?, completed_date = ? WHERE id = ?
        ''', (status, datetime.datetime.now().isoformat(), task_id))
    else:
        cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (status, task_id))
    conn.commit()
    conn.close()

# مدیریت پیشرفت
def update_progress(project_id, task_id, user_id, progress_percentage, notes):
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO progress (project_id, task_id, user_id, progress_percentage, notes, update_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (project_id, task_id, user_id, progress_percentage, notes, 
          datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_project_progress(project_id):
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.title, p.progress_percentage, p.notes, u.first_name, p.update_date
        FROM progress p
        JOIN tasks t ON p.task_id = t.id
        JOIN users u ON p.user_id = u.user_id
        WHERE p.project_id = ?
        ORDER BY p.update_date DESC
    ''', (project_id,))
    progress = cursor.fetchall()
    conn.close()
    return progress

# کلیدهای میانبر
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('📋 پروژه‌های من', '➕ پروژه جدید')
    keyboard.row('📝 وظایف', '📊 پیشرفت')
    keyboard.row('📁 فایل‌ها', '👥 اعضا')
    keyboard.row('📈 گزارش‌ها', '📖 راهنما')
    return keyboard

def create_project_keyboard(project_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📝 وظایف", callback_data=f"project_tasks_{project_id}"),
        InlineKeyboardButton("📊 پیشرفت", callback_data=f"project_progress_{project_id}")
    )
    keyboard.row(
        InlineKeyboardButton("👥 اعضا", callback_data=f"project_members_{project_id}"),
        InlineKeyboardButton("📁 فایل‌ها", callback_data=f"project_files_{project_id}")
    )
    keyboard.row(
        InlineKeyboardButton("✏️ ویرایش", callback_data=f"edit_project_{project_id}"),
        InlineKeyboardButton("❌ حذف", callback_data=f"delete_project_{project_id}")
    )
    return keyboard

def create_task_keyboard(task_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("✅ تکمیل", callback_data=f"complete_task_{task_id}"),
        InlineKeyboardButton("⏸️ در حال انجام", callback_data=f"in_progress_task_{task_id}")
    )
    keyboard.row(
        InlineKeyboardButton("📝 ویرایش", callback_data=f"edit_task_{task_id}"),
        InlineKeyboardButton("❌ حذف", callback_data=f"delete_task_{task_id}")
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
📋 سلام {first_name} عزیز!

به ربات مدیریت پروژه‌های دانش‌آموزی خوش آمدید! 🎯

این ربات به شما کمک می‌کند تا:
• پروژه‌های علمی را مدیریت کنید
• وظایف را تقسیم و پیگیری کنید
• پیشرفت پروژه را ثبت کنید
• فایل‌ها را به اشتراک بگذارید

🎯 ویژگی‌ها:
• مدیریت پروژه‌های گروهی
• تقسیم وظایف
• پیگیری پیشرفت
• اشتراک‌گذاری فایل
• گزارش‌گیری دقیق

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    bot.reply_to(message, welcome_text, reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '📋 پروژه‌های من')
def my_projects(message):
    user_id = message.from_user.id
    projects = get_user_projects(user_id)
    
    if not projects:
        bot.reply_to(message, "شما هنوز در هیچ پروژه‌ای عضو نیستید.")
        return
    
    projects_text = "📋 پروژه‌های شما:\n\n"
    
    for i, project in enumerate(projects, 1):
        status_emoji = "🟢" if project[5] == 'active' else "🔴"
        projects_text += f"{i}. {status_emoji} {project[1]}\n"
        projects_text += f"   📝 {project[2][:50]}...\n"
        projects_text += f"   📂 دسته‌بندی: {project[3]}\n"
        projects_text += f"   👤 نقش: {project[9]}\n"
        projects_text += f"   📅 تاریخ شروع: {project[7][:10]}\n\n"
    
    keyboard = InlineKeyboardMarkup()
    for i, project in enumerate(projects[:5], 1):
        keyboard.row(InlineKeyboardButton(f"{i}. {project[1]}", callback_data=f"project_{project[0]}"))
    
    bot.reply_to(message, projects_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '➕ پروژه جدید')
def create_new_project(message):
    if not is_supervisor(message.from_user.id):
        bot.reply_to(message, "فقط سرپرستان می‌توانند پروژه جدید ایجاد کنند.")
        return
    
    msg = bot.reply_to(message, "📋 لطفاً عنوان پروژه را وارد کنید:")
    bot.register_next_step_handler(msg, process_project_title)

def process_project_title(message):
    title = message.text
    msg = bot.reply_to(message, "📝 لطفاً توضیحات پروژه را وارد کنید:")
    bot.register_next_step_handler(msg, process_project_description, title)

def process_project_description(message, title):
    description = message.text
    msg = bot.reply_to(message, "📂 لطفاً دسته‌بندی پروژه را وارد کنید:")
    bot.register_next_step_handler(msg, process_project_category, title, description)

def process_project_category(message, title, description):
    category = message.text
    supervisor_id = message.from_user.id
    
    project_id = create_project(title, description, category, supervisor_id)
    
    success_text = f"""
✅ پروژه جدید با موفقیت ایجاد شد!

📋 عنوان: {title}
📝 توضیحات: {description}
📂 دسته‌بندی: {category}
👤 سرپرست: {message.from_user.first_name}

حالا می‌توانید اعضا را به پروژه اضافه کنید.
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("👥 افزودن عضو", callback_data=f"add_member_{project_id}"),
        InlineKeyboardButton("📝 ایجاد وظیفه", callback_data=f"create_task_{project_id}")
    )
    
    bot.reply_to(message, success_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📝 وظایف')
def tasks_menu(message):
    user_id = message.from_user.id
    projects = get_user_projects(user_id)
    
    if not projects:
        bot.reply_to(message, "شما در هیچ پروژه‌ای عضو نیستید.")
        return
    
    tasks_text = "📝 وظایف شما:\n\n"
    total_tasks = 0
    completed_tasks = 0
    
    for project in projects:
        tasks = get_project_tasks(project[0])
        project_tasks = [t for t in tasks if t[4] == user_id]
        
        if project_tasks:
            tasks_text += f"📋 {project[1]}:\n"
            for task in project_tasks:
                status_emoji = "✅" if task[5] == 'completed' else "⏳"
                priority_emoji = "🔴" if task[6] == 'high' else "🟡" if task[6] == 'medium' else "🟢"
                tasks_text += f"  {status_emoji} {priority_emoji} {task[1]}\n"
                total_tasks += 1
                if task[5] == 'completed':
                    completed_tasks += 1
            tasks_text += "\n"
    
    if total_tasks == 0:
        tasks_text = "شما هنوز وظیفه‌ای ندارید."
    else:
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        tasks_text += f"📊 آمار:\n"
        tasks_text += f"📝 کل وظایف: {total_tasks}\n"
        tasks_text += f"✅ تکمیل شده: {completed_tasks}\n"
        tasks_text += f"📈 درصد تکمیل: {completion_rate:.1f}%\n"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("➕ وظیفه جدید", callback_data="new_task"),
        InlineKeyboardButton("📊 گزارش وظایف", callback_data="tasks_report")
    )
    
    bot.reply_to(message, tasks_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📊 پیشرفت')
def progress_menu(message):
    user_id = message.from_user.id
    projects = get_user_projects(user_id)
    
    if not projects:
        bot.reply_to(message, "شما در هیچ پروژه‌ای عضو نیستید.")
        return
    
    progress_text = "📊 پیشرفت پروژه‌های شما:\n\n"
    
    for project in projects:
        progress_data = get_project_progress(project[0])
        if progress_data:
            progress_text += f"📋 {project[1]}:\n"
            for prog in progress_data[:3]:  # فقط 3 مورد آخر
                progress_text += f"  📝 {prog[0]}: {prog[1]}%\n"
                progress_text += f"  👤 {prog[3]}: {prog[2]}\n"
            progress_text += "\n"
    
    if not any(get_project_progress(p[0]) for p in projects):
        progress_text = "هنوز پیشرفتی ثبت نشده است."
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📈 نمودار پیشرفت", callback_data="progress_chart"),
        InlineKeyboardButton("📊 گزارش تفصیلی", callback_data="detailed_progress")
    )
    
    bot.reply_to(message, progress_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📁 فایل‌ها')
def files_menu(message):
    user_id = message.from_user.id
    projects = get_user_projects(user_id)
    
    if not projects:
        bot.reply_to(message, "شما در هیچ پروژه‌ای عضو نیستید.")
        return
    
    files_text = "📁 فایل‌های پروژه‌های شما:\n\n"
    
    # در نسخه کامل، فایل‌ها از دیتابیس خوانده می‌شوند
    files_text += "📄 گزارش‌های تحقیقاتی\n"
    files_text += "📊 نمودارها و جداول\n"
    files_text += "📝 مستندات پروژه\n"
    files_text += "🎬 ویدیوهای آموزشی\n"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📤 آپلود فایل", callback_data="upload_file"),
        InlineKeyboardButton("📥 دانلود فایل", callback_data="download_file")
    )
    keyboard.row(
        InlineKeyboardButton("📋 لیست فایل‌ها", callback_data="list_files")
    )
    
    bot.reply_to(message, files_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '👥 اعضا')
def members_menu(message):
    user_id = message.from_user.id
    projects = get_user_projects(user_id)
    
    if not projects:
        bot.reply_to(message, "شما در هیچ پروژه‌ای عضو نیستید.")
        return
    
    members_text = "👥 اعضای پروژه‌های شما:\n\n"
    
    for project in projects:
        members = get_project_members(project[0])
        if members:
            members_text += f"📋 {project[1]}:\n"
            for member in members:
                role_emoji = "👑" if member[1] == 'supervisor' else "👤"
                members_text += f"  {role_emoji} {member[0]} ({member[1]})\n"
            members_text += "\n"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("➕ افزودن عضو", callback_data="add_member"),
        InlineKeyboardButton("👥 مدیریت اعضا", callback_data="manage_members")
    )
    
    bot.reply_to(message, members_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📈 گزارش‌ها')
def reports_menu(message):
    reports_text = """
📈 گزارش‌های موجود:

📊 گزارش پیشرفت کلی
📝 گزارش وظایف
👥 گزارش اعضا
📁 گزارش فایل‌ها
⏰ گزارش زمانی
💰 گزارش هزینه‌ها

لطفاً نوع گزارش مورد نظر را انتخاب کنید:
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📊 پیشرفت کلی", callback_data="report_overall"),
        InlineKeyboardButton("📝 وظایف", callback_data="report_tasks")
    )
    keyboard.row(
        InlineKeyboardButton("👥 اعضا", callback_data="report_members"),
        InlineKeyboardButton("📁 فایل‌ها", callback_data="report_files")
    )
    keyboard.row(
        InlineKeyboardButton("⏰ زمانی", callback_data="report_time"),
        InlineKeyboardButton("💰 هزینه‌ها", callback_data="report_cost")
    )
    
    bot.reply_to(message, reports_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📖 راهنما')
def help_command(message):
    help_text = """
📖 راهنمای ربات مدیریت پروژه

📋 پروژه‌های من:
• مشاهده پروژه‌های عضو شده
• دسترسی به جزئیات پروژه
• مدیریت وظایف و پیشرفت

➕ پروژه جدید:
• ایجاد پروژه جدید (فقط سرپرستان)
• تعیین عنوان و توضیحات
• انتخاب دسته‌بندی

📝 وظایف:
• مشاهده وظایف محول شده
• به‌روزرسانی وضعیت وظایف
• ایجاد وظایف جدید

📊 پیشرفت:
• ثبت پیشرفت کارها
• مشاهده نمودار پیشرفت
• گزارش‌گیری از عملکرد

📁 فایل‌ها:
• آپلود فایل‌های پروژه
• دانلود فایل‌های مشترک
• مدیریت مستندات

👥 اعضا:
• مشاهده اعضای پروژه
• افزودن عضو جدید
• مدیریت نقش‌ها

📈 گزارش‌ها:
• گزارش پیشرفت کلی
• گزارش وظایف
• گزارش اعضا و فایل‌ها

💡 نکات مهم:
• وظایف را منظم پیگیری کنید
• پیشرفت را به‌موقع ثبت کنید
• فایل‌ها را به اشتراک بگذارید
• با اعضا همکاری کنید

📞 پشتیبانی:
برای سوالات بیشتر با پشتیبانی تماس بگیرید.
    """
    
    bot.reply_to(message, help_text)

# مدیریت callback ها
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("project_"):
        project_id = int(call.data.split("_")[1])
        project = get_project_by_id(project_id)
        
        if not project:
            bot.answer_callback_query(call.id, "پروژه یافت نشد")
            return
        
        project_text = f"""
📋 {project[1]}

📝 توضیحات:
{project[2]}

📂 دسته‌بندی: {project[3]}
📊 وضعیت: {project[5]}
📅 تاریخ شروع: {project[7][:10]}
📅 تاریخ پایان: {project[8][:10] if project[8] else 'تعیین نشده'}
        """
        
        bot.edit_message_text(project_text, call.message.chat.id, call.message.message_id,
                             reply_markup=create_project_keyboard(project_id))
    
    elif call.data.startswith("complete_task_"):
        task_id = int(call.data.split("_")[2])
        update_task_status(task_id, 'completed')
        bot.answer_callback_query(call.id, "وظیفه تکمیل شد!")
        bot.edit_message_text("✅ وظیفه با موفقیت تکمیل شد!", 
                             call.message.chat.id, call.message.message_id)

# راه‌اندازی ربات
if __name__ == "__main__":
    init_database()
    print("📋 ربات مدیریت پروژه‌های دانش‌آموزی راه‌اندازی شد!")
    print("🎯 آماده برای مدیریت پروژه‌های علمی...")
    bot.polling(none_stop=True)