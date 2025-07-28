 """
تمرین 20: شبیه‌سازی پایگاه داده
سطح: متوسط
هدف: آشنایی با مفاهیم پایگاه داده
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """مدیریت شبیه‌سازی پایگاه داده"""
    
    def __init__(self, db_file="bot_database.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """راه‌اندازی پایگاه داده"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # جدول کاربران
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        first_name TEXT,
                        last_name TEXT,
                        mobile TEXT,
                        national_id TEXT,
                        registration_date TIMESTAMP,
                        status TEXT DEFAULT 'active'
                    )
                ''')
                
                # جدول کلاس‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS classes (
                        class_id TEXT PRIMARY KEY,
                        name TEXT,
                        price TEXT,
                        schedule TEXT,
                        description TEXT,
                        max_students INTEGER DEFAULT 20,
                        current_students INTEGER DEFAULT 0
                    )
                ''')
                
                # جدول ثبت‌نام‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS registrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        class_id TEXT,
                        registration_date TIMESTAMP,
                        payment_status TEXT DEFAULT 'pending',
                        payment_amount TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (user_id),
                        FOREIGN KEY (class_id) REFERENCES classes (class_id)
                    )
                ''')
                
                # جدول تمرین‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS exercises (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER,
                        exercise_date DATE,
                        status TEXT DEFAULT 'active',
                        participants_count INTEGER DEFAULT 0
                    )
                ''')
                
                # جدول امتیازات
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        exercise_id INTEGER,
                        score INTEGER,
                        scored_by INTEGER,
                        score_date TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id),
                        FOREIGN KEY (exercise_id) REFERENCES exercises (id)
                    )
                ''')
                
                conn.commit()
                print("✅ پایگاه داده راه‌اندازی شد")
        
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی پایگاه داده: {e}")
    
    def add_user(self, user_data: Dict[str, Any]) -> bool:
        """
        اضافه کردن کاربر
        
        پارامترها:
            user_data (dict): اطلاعات کاربر
        
        خروجی:
            bool: موفقیت عملیات
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, first_name, last_name, mobile, national_id, registration_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_data['user_id'],
                    user_data.get('first_name', ''),
                    user_data.get('last_name', ''),
                    user_data.get('mobile', ''),
                    user_data.get('national_id', ''),
                    user_data.get('registration_date', time.time())
                ))
                
                conn.commit()
                return True
        
        except Exception as e:
            print(f"❌ خطا در اضافه کردن کاربر: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات کاربر
        
        پارامترها:
            user_id (int): شناسه کاربر
        
        خروجی:
            dict: اطلاعات کاربر یا None
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM users WHERE user_id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
        
        except Exception as e:
            print(f"❌ خطا در دریافت کاربر: {e}")
            return None
    
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """
        به‌روزرسانی اطلاعات کاربر
        
        پارامترها:
            user_id (int): شناسه کاربر
            updates (dict): اطلاعات جدید
        
        خروجی:
            bool: موفقیت عملیات
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
                values = list(updates.values()) + [user_id]
                
                cursor.execute(f'''
                    UPDATE users SET {set_clause} WHERE user_id = ?
                ''', values)
                
                conn.commit()
                return True
        
        except Exception as e:
            print(f"❌ خطا در به‌روزرسانی کاربر: {e}")
            return False
    
    def add_registration(self, user_id: int, class_id: str, payment_amount: str) -> bool:
        """
        اضافه کردن ثبت‌نام
        
        پارامترها:
            user_id (int): شناسه کاربر
            class_id (str): شناسه کلاس
            payment_amount (str): مبلغ پرداخت
        
        خروجی:
            bool: موفقیت عملیات
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO registrations 
                    (user_id, class_id, registration_date, payment_amount)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, class_id, time.time(), payment_amount))
                
                # به‌روزرسانی تعداد دانشجویان کلاس
                cursor.execute('''
                    UPDATE classes SET current_students = current_students + 1
                    WHERE class_id = ?
                ''', (class_id,))
                
                conn.commit()
                return True
        
        except Exception as e:
            print(f"❌ خطا در اضافه کردن ثبت‌نام: {e}")
            return False
    
    def get_user_registrations(self, user_id: int) -> List[Dict[str, Any]]:
        """
        دریافت ثبت‌نام‌های کاربر
        
        پارامترها:
            user_id (int): شناسه کاربر
        
        خروجی:
            list: لیست ثبت‌نام‌ها
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT r.*, c.name as class_name, c.price as class_price
                    FROM registrations r
                    JOIN classes c ON r.class_id = c.class_id
                    WHERE r.user_id = ?
                    ORDER BY r.registration_date DESC
                ''', (user_id,))
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        
        except Exception as e:
            print(f"❌ خطا در دریافت ثبت‌نام‌ها: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        دریافت آمار پایگاه داده
        
        خروجی:
            dict: آمار پایگاه داده
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # تعداد کاربران
                cursor.execute('SELECT COUNT(*) FROM users')
                stats['total_users'] = cursor.fetchone()[0]
                
                # تعداد ثبت‌نام‌ها
                cursor.execute('SELECT COUNT(*) FROM registrations')
                stats['total_registrations'] = cursor.fetchone()[0]
                
                # تعداد کلاس‌ها
                cursor.execute('SELECT COUNT(*) FROM classes')
                stats['total_classes'] = cursor.fetchone()[0]
                
                # کلاس‌های محبوب
                cursor.execute('''
                    SELECT c.name, COUNT(r.id) as registration_count
                    FROM classes c
                    LEFT JOIN registrations r ON c.class_id = r.class_id
                    GROUP BY c.class_id
                    ORDER BY registration_count DESC
                    LIMIT 5
                ''')
                
                stats['popular_classes'] = [
                    {'name': row[0], 'count': row[1]} 
                    for row in cursor.fetchall()
                ]
                
                return stats
        
        except Exception as e:
            print(f"❌ خطا در دریافت آمار: {e}")
            return {}

# ایجاد نمونه مدیر پایگاه داده
db_manager = DatabaseManager()

def save_user_to_db(user_data):
    """ذخیره کاربر در پایگاه داده"""
    return db_manager.add_user(user_data)

def get_user_from_db(user_id):
    """دریافت کاربر از پایگاه داده"""
    return db_manager.get_user(user_id)

print("✅ تمرین 20: شبیه‌سازی پایگاه داده تکمیل شد!")

# تمرین: تابعی برای جستجوی کاربران بنویسید
# تمرین: تابعی برای گزارش‌گیری پیشرفته بنویسید
# تمرین: تابعی برای پشتیبان‌گیری از پایگاه داده بنویسید