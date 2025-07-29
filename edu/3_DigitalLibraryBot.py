# ربات کتابخانه دیجیتال
# DigitalLibraryBot - اشتراک کتاب، مقاله، منابع آموزشی
# توسعه‌دهنده: محمد زارع‌پور

import telebot
import json
import datetime
import sqlite3
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

# تنظیمات اولیه
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(BOT_TOKEN)

# دیتابیس
def init_database():
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            join_date TEXT,
            upload_count INTEGER DEFAULT 0,
            download_count INTEGER DEFAULT 0
        )
    ''')
    
    # جدول کتاب‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            category TEXT,
            description TEXT,
            file_id TEXT,
            file_size INTEGER,
            uploader_id INTEGER,
            upload_date TEXT,
            download_count INTEGER DEFAULT 0,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0
        )
    ''')
    
    # جدول دسته‌بندی‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            description TEXT,
            book_count INTEGER DEFAULT 0
        )
    ''')
    
    # جدول نظرات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            book_id INTEGER,
            user_id INTEGER,
            rating INTEGER,
            comment TEXT,
            review_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # جدول دانلودها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY,
            book_id INTEGER,
            user_id INTEGER,
            download_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# دسته‌بندی‌های پیش‌فرض
def insert_default_categories():
    categories = [
        ("ادبیات", "کتاب‌های ادبی و داستانی"),
        ("علمی", "کتاب‌های علمی و آموزشی"),
        ("تاریخ", "کتاب‌های تاریخی"),
        ("فلسفه", "کتاب‌های فلسفی"),
        ("دین", "کتاب‌های مذهبی"),
        ("روانشناسی", "کتاب‌های روانشناسی"),
        ("اقتصاد", "کتاب‌های اقتصادی"),
        ("هنر", "کتاب‌های هنری"),
        ("زبان", "کتاب‌های آموزش زبان"),
        ("کامپیوتر", "کتاب‌های کامپیوتر و برنامه‌نویسی")
    ]
    
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    
    for name, description in categories:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (name, description)
            VALUES (?, ?)
        ''', (name, description))
    
    conn.commit()
    conn.close()

# مدیریت کاربران
def add_user(user_id, username, first_name):
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, join_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# مدیریت کتاب‌ها
def add_book(title, author, category, description, file_id, file_size, uploader_id):
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO books (title, author, category, description, file_id, file_size, uploader_id, upload_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, author, category, description, file_id, file_size, uploader_id, datetime.datetime.now().isoformat()))
    
    # افزایش تعداد کتاب‌های دسته‌بندی
    cursor.execute('UPDATE categories SET book_count = book_count + 1 WHERE name = ?', (category,))
    
    # افزایش تعداد آپلودهای کاربر
    cursor.execute('UPDATE users SET upload_count = upload_count + 1 WHERE user_id = ?', (uploader_id,))
    
    conn.commit()
    conn.close()

def get_books_by_category(category, limit=10):
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM books WHERE category = ? ORDER BY upload_date DESC LIMIT ?
    ''', (category, limit))
    books = cursor.fetchall()
    conn.close()
    return books

def search_books(query):
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM books 
        WHERE title LIKE ? OR author LIKE ? OR description LIKE ?
        ORDER BY rating DESC
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    books = cursor.fetchall()
    conn.close()
    return books

def get_book_by_id(book_id):
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    conn.close()
    return book

# مدیریت نظرات
def add_review(book_id, user_id, rating, comment):
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    
    # بررسی اینکه کاربر قبلاً نظر داده یا نه
    cursor.execute('SELECT id FROM reviews WHERE book_id = ? AND user_id = ?', (book_id, user_id))
    existing_review = cursor.fetchone()
    
    if existing_review:
        # به‌روزرسانی نظر موجود
        cursor.execute('''
            UPDATE reviews SET rating = ?, comment = ?, review_date = ?
            WHERE book_id = ? AND user_id = ?
        ''', (rating, comment, datetime.datetime.now().isoformat(), book_id, user_id))
    else:
        # افزودن نظر جدید
        cursor.execute('''
            INSERT INTO reviews (book_id, user_id, rating, comment, review_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (book_id, user_id, rating, comment, datetime.datetime.now().isoformat()))
    
    # محاسبه میانگین امتیاز کتاب
    cursor.execute('SELECT AVG(rating) FROM reviews WHERE book_id = ?', (book_id,))
    avg_rating = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM reviews WHERE book_id = ?', (book_id,))
    review_count = cursor.fetchone()[0]
    
    # به‌روزرسانی امتیاز کتاب
    cursor.execute('UPDATE books SET rating = ?, review_count = ? WHERE id = ?', (avg_rating, review_count, book_id))
    
    conn.commit()
    conn.close()

def get_book_reviews(book_id, limit=5):
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, u.first_name 
        FROM reviews r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.book_id = ?
        ORDER BY r.review_date DESC
        LIMIT ?
    ''', (book_id, limit))
    reviews = cursor.fetchall()
    conn.close()
    return reviews

# مدیریت دانلودها
def record_download(book_id, user_id):
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    
    # ثبت دانلود
    cursor.execute('''
        INSERT INTO downloads (book_id, user_id, download_date)
        VALUES (?, ?, ?)
    ''', (book_id, user_id, datetime.datetime.now().isoformat()))
    
    # افزایش تعداد دانلود کتاب
    cursor.execute('UPDATE books SET download_count = download_count + 1 WHERE id = ?', (book_id,))
    
    # افزایش تعداد دانلودهای کاربر
    cursor.execute('UPDATE users SET download_count = download_count + 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()

# کلیدهای میانبر
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('📚 جستجو', '📂 دسته‌بندی‌ها')
    keyboard.row('📤 آپلود کتاب', '⭐ بهترین‌ها')
    keyboard.row('📊 آمار من', '📖 راهنما')
    return keyboard

def create_category_keyboard():
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM categories ORDER BY book_count DESC')
    categories = cursor.fetchall()
    conn.close()
    
    keyboard = InlineKeyboardMarkup()
    for i in range(0, len(categories), 2):
        row = []
        row.append(InlineKeyboardButton(categories[i][0], callback_data=f"category_{categories[i][0]}"))
        if i + 1 < len(categories):
            row.append(InlineKeyboardButton(categories[i+1][0], callback_data=f"category_{categories[i+1][0]}"))
        keyboard.row(*row)
    
    return keyboard

def create_book_keyboard(book_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📥 دانلود", callback_data=f"download_{book_id}"),
        InlineKeyboardButton("⭐ امتیاز", callback_data=f"rate_{book_id}")
    )
    keyboard.row(
        InlineKeyboardButton("💬 نظرات", callback_data=f"reviews_{book_id}"),
        InlineKeyboardButton("📚 بیشتر", callback_data="more_books")
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

به کتابخانه دیجیتال خوش آمدید! 📖

این ربات به شما کمک می‌کند تا:
• کتاب‌های مختلف را جستجو کنید
• کتاب‌های مورد علاقه را دانلود کنید
• کتاب‌های خود را به اشتراک بگذارید
• نظرات خود را ثبت کنید

📚 ویژگی‌ها:
• جستجوی پیشرفته
• دسته‌بندی‌های مختلف
• سیستم امتیازدهی
• نظرات کاربران
• آمار دانلود

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    bot.reply_to(message, welcome_text, reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '📚 جستجو')
def search_menu(message):
    msg = bot.reply_to(message, "🔍 لطفاً کلمه کلیدی مورد نظر را وارد کنید:")
    bot.register_next_step_handler(msg, process_search)

def process_search(message):
    query = message.text
    books = search_books(query)
    
    if not books:
        bot.reply_to(message, f"❌ هیچ کتابی با کلمه کلیدی '{query}' یافت نشد.")
        return
    
    result_text = f"🔍 نتایج جستجو برای '{query}':\n\n"
    
    for i, book in enumerate(books[:5], 1):
        result_text += f"{i}. 📖 {book[1]}\n"
        result_text += f"   👤 نویسنده: {book[2]}\n"
        result_text += f"   📂 دسته‌بندی: {book[3]}\n"
        result_text += f"   ⭐ امتیاز: {book[10]:.1f}/5\n"
        result_text += f"   📥 دانلود: {book[9]} بار\n\n"
    
    if len(books) > 5:
        result_text += f"... و {len(books) - 5} کتاب دیگر"
    
    keyboard = InlineKeyboardMarkup()
    for i, book in enumerate(books[:5], 1):
        keyboard.row(InlineKeyboardButton(f"{i}. {book[1]}", callback_data=f"book_{book[0]}"))
    
    bot.reply_to(message, result_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📂 دسته‌بندی‌ها')
def categories_menu(message):
    bot.reply_to(message, "📂 دسته‌بندی‌های کتاب‌ها\n\nلطفاً دسته‌بندی مورد نظر را انتخاب کنید:", 
                 reply_markup=create_category_keyboard())

@bot.message_handler(func=lambda message: message.text == '📤 آپلود کتاب')
def upload_book(message):
    msg = bot.reply_to(message, "📤 برای آپلود کتاب، لطفاً اطلاعات زیر را وارد کنید:\n\nعنوان کتاب:")
    bot.register_next_step_handler(msg, process_book_title)

def process_book_title(message):
    title = message.text
    msg = bot.reply_to(message, "👤 نام نویسنده:")
    bot.register_next_step_handler(msg, process_book_author, title)

def process_book_author(message, title):
    author = message.text
    msg = bot.reply_to(message, "📂 دسته‌بندی (مثال: ادبیات، علمی، تاریخ):")
    bot.register_next_step_handler(msg, process_book_category, title, author)

def process_book_category(message, title, author):
    category = message.text
    msg = bot.reply_to(message, "📝 توضیحات کتاب:")
    bot.register_next_step_handler(msg, process_book_description, title, author, category)

def process_book_description(message, title, author, category):
    description = message.text
    msg = bot.reply_to(message, "📎 حالا فایل کتاب را ارسال کنید:")
    bot.register_next_step_handler(msg, process_book_file, title, author, category, description)

def process_book_file(message, title, author, category, description):
    if not message.document:
        bot.reply_to(message, "❌ لطفاً فایل کتاب را ارسال کنید.")
        return
    
    file_id = message.document.file_id
    file_size = message.document.file_size
    uploader_id = message.from_user.id
    
    add_book(title, author, category, description, file_id, file_size, uploader_id)
    
    success_text = f"""
✅ کتاب با موفقیت آپلود شد!

📖 عنوان: {title}
👤 نویسنده: {author}
📂 دسته‌بندی: {category}
📝 توضیحات: {description}
📊 حجم فایل: {file_size / 1024 / 1024:.1f} MB

کتاب شما در دسترس سایر کاربران قرار گرفت.
    """
    
    bot.reply_to(message, success_text)

@bot.message_handler(func=lambda message: message.text == '⭐ بهترین‌ها')
def show_best_books(message):
    conn = sqlite3.connect('digital_library.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM books 
        ORDER BY rating DESC, download_count DESC 
        LIMIT 10
    ''')
    books = cursor.fetchall()
    conn.close()
    
    if not books:
        bot.reply_to(message, "هنوز هیچ کتابی آپلود نشده است.")
        return
    
    result_text = "⭐ بهترین کتاب‌ها:\n\n"
    
    for i, book in enumerate(books, 1):
        result_text += f"{i}. 📖 {book[1]}\n"
        result_text += f"   👤 {book[2]}\n"
        result_text += f"   ⭐ {book[10]:.1f}/5 ({book[11]} نظر)\n"
        result_text += f"   📥 {book[9]} دانلود\n\n"
    
    keyboard = InlineKeyboardMarkup()
    for i, book in enumerate(books[:5], 1):
        keyboard.row(InlineKeyboardButton(f"{i}. {book[1]}", callback_data=f"book_{book[0]}"))
    
    bot.reply_to(message, result_text, reply_markup=keyboard)

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
📤 کتاب‌های آپلود شده: {user_stats[5]}
📥 کتاب‌های دانلود شده: {user_stats[6]}
📅 تاریخ عضویت: {user_stats[4][:10]}
    """
    
    bot.reply_to(message, stats_text)

@bot.message_handler(func=lambda message: message.text == '📖 راهنما')
def help_command(message):
    help_text = """
📖 راهنمای کتابخانه دیجیتال

🔍 جستجو:
• روی "جستجو" کلیک کنید
• کلمه کلیدی را وارد کنید
• نتایج را مشاهده کنید

📂 دسته‌بندی‌ها:
• دسته‌بندی مورد نظر را انتخاب کنید
• کتاب‌های آن دسته را مشاهده کنید

📤 آپلود کتاب:
• اطلاعات کتاب را وارد کنید
• فایل کتاب را ارسال کنید
• کتاب در دسترس قرار می‌گیرد

⭐ امتیازدهی:
• به کتاب‌ها امتیاز دهید
• نظرات خود را ثبت کنید
• به دیگران کمک کنید

📥 دانلود:
• روی "دانلود" کلیک کنید
• فایل کتاب دریافت می‌شود
• آمار دانلود ثبت می‌شود

💡 نکات مهم:
• فقط کتاب‌های قانونی آپلود کنید
• نظرات مفید و سازنده بگذارید
• به حقوق نویسندگان احترام بگذارید
• از کتاب‌ها به درستی استفاده کنید

📞 پشتیبانی:
برای سوالات بیشتر با پشتیبانی تماس بگیرید.
    """
    
    bot.reply_to(message, help_text)

# مدیریت callback ها
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("category_"):
        category = call.data.split("_")[1]
        books = get_books_by_category(category)
        
        if not books:
            bot.answer_callback_query(call.id, "هیچ کتابی در این دسته‌بندی موجود نیست")
            return
        
        result_text = f"📂 کتاب‌های دسته‌بندی '{category}':\n\n"
        
        for i, book in enumerate(books[:5], 1):
            result_text += f"{i}. 📖 {book[1]}\n"
            result_text += f"   👤 {book[2]}\n"
            result_text += f"   ⭐ {book[10]:.1f}/5\n\n"
        
        keyboard = InlineKeyboardMarkup()
        for i, book in enumerate(books[:5], 1):
            keyboard.row(InlineKeyboardButton(f"{i}. {book[1]}", callback_data=f"book_{book[0]}"))
        
        bot.edit_message_text(result_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        
    elif call.data.startswith("book_"):
        book_id = int(call.data.split("_")[1])
        book = get_book_by_id(book_id)
        
        if not book:
            bot.answer_callback_query(call.id, "کتاب یافت نشد")
            return
        
        book_text = f"""
📖 {book[1]}

👤 نویسنده: {book[2]}
📂 دسته‌بندی: {book[3]}
📝 توضیحات: {book[4]}
⭐ امتیاز: {book[10]:.1f}/5 ({book[11]} نظر)
📥 دانلود: {book[9]} بار
📅 تاریخ آپلود: {book[8][:10]}
📊 حجم فایل: {book[6] / 1024 / 1024:.1f} MB
        """
        
        bot.edit_message_text(book_text, call.message.chat.id, call.message.message_id, 
                             reply_markup=create_book_keyboard(book_id))
        
    elif call.data.startswith("download_"):
        book_id = int(call.data.split("_")[1])
        book = get_book_by_id(book_id)
        
        if not book:
            bot.answer_callback_query(call.id, "کتاب یافت نشد")
            return
        
        # ثبت دانلود
        record_download(book_id, call.from_user.id)
        
        # ارسال فایل
        bot.send_document(call.message.chat.id, book[5], caption=f"📖 {book[1]}\n👤 {book[2]}")
        bot.answer_callback_query(call.id, "کتاب با موفقیت دانلود شد!")

# راه‌اندازی ربات
if __name__ == "__main__":
    init_database()
    insert_default_categories()
    print("📚 ربات کتابخانه دیجیتال راه‌اندازی شد!")
    print("📖 آماده برای اشتراک‌گذاری کتاب‌ها...")
    bot.polling(none_stop=True)