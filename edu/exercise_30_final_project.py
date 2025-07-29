 """
تمرین 30: پروژه نهایی - سیستم کامل ربات
سطح: پیشرفته
هدف: ترکیب تمام آموخته‌ها در یک سیستم کامل
"""

import asyncio
import threading
import time
from datetime import datetime
import json
import logging

class CompleteBotSystem:
    """سیستم کامل ربات تلاوت"""
    
    def __init__(self, bot_token: str, environment: str = "production"):
        # تنظیمات اصلی
        self.bot_token = bot_token
        self.environment = environment
        self.base_url = f"https://tapi.bale.ai/bot{bot_token}"
        
        # راه‌اندازی سیستم‌های مختلف
        self.setup_logging()
        self.setup_security()
        self.setup_monitoring()
        self.setup_ml_system()
        self.setup_database()
        self.setup_webhook()
        
        # وضعیت سیستم
        self.is_running = False
        self.start_time = None
        
        print("🚀 سیستم کامل ربات تلاوت راه‌اندازی شد")
    
    def setup_logging(self):
        """راه‌اندازی سیستم لاگینگ"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot_system.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('CompleteBotSystem')
        self.logger.info("سیستم لاگینگ راه‌اندازی شد")
    
    def setup_security(self):
        """راه‌اندازی سیستم امنیت"""
        from exercise_23_security_system import SecurityManager
        self.security_manager = SecurityManager()
        self.logger.info("سیستم امنیت راه‌اندازی شد")
    
    def setup_monitoring(self):
        """راه‌اندازی سیستم مانیتورینگ"""
        from exercise_27_monitoring_system import SystemMonitor, BotMonitor, HealthChecker
        self.system_monitor = SystemMonitor()
        self.bot_monitor = BotMonitor()
        self.health_checker = HealthChecker()
        self.logger.info("سیستم مانیتورینگ راه‌اندازی شد")
    
    def setup_ml_system(self):
        """راه‌اندازی سیستم یادگیری ماشین"""
        from exercise_29_machine_learning import SmartBot
        self.smart_bot = SmartBot()
        self.logger.info("سیستم یادگیری ماشین راه‌اندازی شد")
    
    def setup_database(self):
        """راه‌اندازی پایگاه داده"""
        from exercise_20_database_simulation import DatabaseManager
        self.db_manager = DatabaseManager()
        self.logger.info("پایگاه داده راه‌اندازی شد")
    
    def setup_webhook(self):
        """راه‌اندازی سیستم webhook"""
        from exercise_22_webhook_system import WebhookBot
        self.webhook_bot = WebhookBot(self.bot_token)
        self.logger.info("سیستم webhook راه‌اندازی شد")
    
    def start_system(self):
        """شروع سیستم کامل"""
        self.is_running = True
        self.start_time = datetime.now()
        
        # شروع مانیتورینگ
        self.system_monitor.start_monitoring()
        
        # شروع thread های مختلف
        self.start_background_tasks()
        
        # شروع webhook server
        self.start_webhook_server()
        
        self.logger.info("سیستم کامل شروع شد")
        print("🎉 سیستم کامل ربات تلاوت فعال شد!")
    
    def start_background_tasks(self):
        """شروع وظایف پس‌زمینه"""
        # Thread برای مانیتورینگ
        monitoring_thread = threading.Thread(target=self.monitoring_task)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        # Thread برای پاکسازی
        cleanup_thread = threading.Thread(target=self.cleanup_task)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        # Thread برای آموزش مدل‌ها
        training_thread = threading.Thread(target=self.training_task)
        training_thread.daemon = True
        training_thread.start()
    
    def monitoring_task(self):
        """وظیفه مانیتورینگ"""
        while self.is_running:
            try:
                # بررسی سلامت سیستم
                if not self.health_checker.is_system_healthy():
                    self.logger.warning("سیستم سالم نیست!")
                
                # چاپ گزارش مانیتورینگ
                if self.start_time and (datetime.now() - self.start_time).seconds % 300 == 0:  # هر 5 دقیقه
                    self.print_monitoring_report()
                
                time.sleep(60)  # بررسی هر دقیقه
                
            except Exception as e:
                self.logger.error(f"خطا در مانیتورینگ: {e}")
                time.sleep(60)
    
    def cleanup_task(self):
        """وظیفه پاکسازی"""
        while self.is_running:
            try:
                # پاکسازی کش‌ها
                self.cleanup_caches()
                
                # پاکسازی فایل‌های قدیمی
                self.cleanup_old_files()
                
                time.sleep(3600)  # هر ساعت
                
            except Exception as e:
                self.logger.error(f"خطا در پاکسازی: {e}")
                time.sleep(3600)
    
    def training_task(self):
        """وظیفه آموزش مدل‌ها"""
        while self.is_running:
            try:
                # آموزش مدل‌های ML
                self.smart_bot.ml_bot.train_intent_classifier()
                self.smart_bot.ml_bot.train_sentiment_analyzer()
                self.smart_bot.ml_bot.build_user_behavior_model()
                
                # ذخیره مدل‌ها
                self.smart_bot.ml_bot.save_models()
                
                time.sleep(86400)  # هر روز
                
            except Exception as e:
                self.logger.error(f"خطا در آموزش مدل‌ها: {e}")
                time.sleep(3600)
    
    def cleanup_caches(self):
        """پاکسازی کش‌ها"""
        current_time = time.time()
        
        # پاکسازی کش کاربران
        if hasattr(self.smart_bot.ml_bot, 'user_cache'):
            expired_keys = [
                key for key, entry in self.smart_bot.ml_bot.user_cache.items()
                if current_time - entry['timestamp'] > 3600  # 1 ساعت
            ]
            for key in expired_keys:
                del self.smart_bot.ml_bot.user_cache[key]
        
        self.logger.info("کش‌ها پاکسازی شدند")
    
    def cleanup_old_files(self):
        """پاکسازی فایل‌های قدیمی"""
        import os
        from datetime import datetime, timedelta
        
        # حذف فایل‌های لاگ قدیمی
        log_dir = "logs"
        if os.path.exists(log_dir):
            cutoff_date = datetime.now() - timedelta(days=30)
            for filename in os.listdir(log_dir):
                filepath = os.path.join(log_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_date:
                        os.remove(filepath)
        
        self.logger.info("فایل‌های قدیمی پاکسازی شدند")
    
    def start_webhook_server(self):
        """شروع سرور webhook"""
        try:
            self.webhook_bot.run_webhook_server(host='0.0.0.0', port=5000)
        except Exception as e:
            self.logger.error(f"خطا در شروع webhook server: {e}")
    
    def process_message_complete(self, message: dict):
        """پردازش کامل پیام"""
        try:
            # بررسی امنیت
            if not secure_message_processing(message):
                return False
            
            # پردازش هوشمند
            response = self.smart_bot.process_smart_message(message)
            
            # پیگیری متریک‌ها
            if 'message' in message:
                user_id = message['message']['from']['id']
                self.bot_monitor.track_message(user_id, 'text')
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطا در پردازش پیام: {e}")
            return False
    
    def process_callback_complete(self, callback_query: dict):
        """پردازش کامل callback"""
        try:
            # بررسی امنیت
            if not secure_callback_processing(callback_query):
                return False
            
            # پردازش callback
            chat_id = callback_query['message']['chat']['id']
            user_id = callback_query['from']['id']
            data = callback_query.get('data', '')
            
            handle_callback_query({'callback_query': callback_query})
            
            # پیگیری متریک‌ها
            self.bot_monitor.track_message(user_id, 'callback')
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطا در پردازش callback: {e}")
            return False
    
    def get_system_status(self) -> dict:
        """دریافت وضعیت سیستم"""
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        status = {
            'system': {
                'running': self.is_running,
                'uptime_seconds': uptime,
                'uptime_hours': uptime / 3600,
                'environment': self.environment
            },
            'bot': self.bot_monitor.get_bot_stats(),
            'security': self.security_manager.get_security_report(),
            'health': self.health_checker.run_health_checks(),
            'database': {
                'total_users': len(registered_users),
                'active_sessions': len(user_states)
            }
        }
        
        return status
    
    def print_monitoring_report(self):
        """چاپ گزارش مانیتورینگ"""
        status = self.get_system_status()
        
        print("\n" + "="*50)
        print("📊 گزارش مانیتورینگ سیستم")
        print("="*50)
        
        # وضعیت سیستم
        system = status['system']
        print(f"🖥️  وضعیت: {'فعال' if system['running'] else 'غیرفعال'}")
        print(f"⏱️  زمان کارکرد: {system['uptime_hours']:.1f} ساعت")
        print(f"🌍 محیط: {system['environment']}")
        
        # آمار ربات
        bot_stats = status['bot']
        print(f"🤖 پیام‌ها: {bot_stats['total_messages']}")
        print(f"👥 کاربران فعال: {bot_stats['active_users']}")
        print(f"❌ نرخ خطا: {bot_stats['error_rate']:.2f}%")
        
        # سلامت سیستم
        health_status = "✅ سالم" if self.health_checker.is_system_healthy() else "❌ مشکل"
        print(f"🏥 سلامت سیستم: {health_status}")
        
        print("="*50)
    
    def stop_system(self):
        """توقف سیستم"""
        self.is_running = False
        
        # توقف مانیتورینگ
        self.system_monitor.stop_monitoring()
        
        # ذخیره مدل‌ها
        self.smart_bot.ml_bot.save_models()
        
        # ذخیره داده‌ها
        save_users_to_file()
        
        self.logger.info("سیستم متوقف شد")
        print("🛑 سیستم کامل ربات تلاوت متوقف شد")
    
    def emergency_shutdown(self):
        """خاموشی اضطراری"""
        self.logger.critical("خاموشی اضطراری سیستم")
        self.stop_system()
        print("🚨 خاموشی اضطراری سیستم")

def create_complete_bot_system(bot_token: str, environment: str = "production"):
    """ایجاد سیستم کامل ربات"""
    return CompleteBotSystem(bot_token, environment)

def run_complete_system():
    """اجرای سیستم کامل"""
    # تنظیمات
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    ENVIRONMENT = "production"
    
    # ایجاد سیستم
    bot_system = create_complete_bot_system(BOT_TOKEN, ENVIRONMENT)
    
    try:
        # شروع سیستم
        bot_system.start_system()
        
        # نگه داشتن برنامه
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 دریافت سیگنال توقف...")
        bot_system.stop_system()
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        bot_system.emergency_shutdown()

def generate_final_report():
    """تولید گزارش نهایی"""
    report = {
        'project_info': {
            'name': 'ربات تلاوت قرآن',
            'version': '1.0.0',
            'description': 'سیستم کامل ربات تلگرام برای مدیریت کلاس‌های تلاوت',
            'completion_date': datetime.now().isoformat()
        },
        'features': [
            'سیستم ثبت‌نام کامل',
            'مدیریت کلاس‌ها',
            'سیستم پرداخت',
            'یادگیری ماشین',
            'امنیت پیشرفته',
            'مانیتورینگ کامل',
            'API مستند',
            'سیستم webhook',
            'پایگاه داده',
            'تست‌های جامع'
        ],
        'exercises_completed': [
            'تمرین 1: راه‌اندازی اولیه',
            'تمرین 2: ساختارهای داده',
            'تمرین 3: توابع پایه',
            'تمرین 4: تاریخ و زمان',
            'تمرین 5: ارتباط API',
            'تمرین 6: مدیریت کاربران',
            'تمرین 7: توابع ادمین',
            'تمرین 8: سیستم منو',
            'تمرین 9: سیستم ثبت‌نام',
            'تمرین 10: انتخاب کلاس',
            'تمرین 11: سیستم پرداخت',
            'تمرین 12: سیستم تمرین',
            'تمرین 13: مدیریت callback',
            'تمرین 14: پردازش پیام‌ها',
            'تمرین 15: مدیریت خطاها',
            'تمرین 16: اعتبارسنجی داده‌ها',
            'تمرین 17: عملیات فایل',
            'تمرین 18: سیستم لاگینگ',
            'تمرین 19: مدیریت تنظیمات',
            'تمرین 20: شبیه‌سازی پایگاه داده',
            'تمرین 21: عملیات ناهمزمان',
            'تمرین 22: سیستم webhook',
            'تمرین 23: سیستم امنیت',
            'تمرین 24: چارچوب تست',
            'تمرین 25: بهینه‌سازی عملکرد',
            'تمرین 26: سیستم استقرار',
            'تمرین 27: سیستم مانیتورینگ',
            'تمرین 28: مستندسازی API',
            'تمرین 29: یادگیری ماشین',
            'تمرین 30: پروژه نهایی'
        ],
        'technologies_used': [
            'Python 3.9+',
            'Flask',
            'SQLite/PostgreSQL',
            'Scikit-learn',
            'Docker',
            'Nginx',
            'Systemd',
            'Prometheus',
            'Swagger'
        ],
        'learning_outcomes': [
            'برنامه‌نویسی پایتون پیشرفته',
            'معماری نرم‌افزار',
            'پایگاه داده',
            'API طراحی',
            'یادگیری ماشین',
            'امنیت نرم‌افزار',
            'تست‌نویسی',
            'مانیتورینگ',
            'استقرار نرم‌افزار',
            'مستندسازی'
        ]
    }
    
    with open('final_project_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("📋 گزارش نهایی پروژه در final_project_report.json ذخیره شد")
    return report

if __name__ == "__main__":
    print("🎓 تمرین 30: پروژه نهایی - سیستم کامل ربات")
    print("=" * 60)
    
    # تولید گزارش نهایی
    report = generate_final_report()
    
    print("\n🎉 تبریک! شما تمام 30 تمرین را با موفقیت تکمیل کردید!")
    print("🚀 حالا می‌توانید سیستم کامل ربات را اجرا کنید:")
    print("   python exercise_30_final_project.py")
    
    print("\n📚 مهارت‌های کسب شده:")
    for outcome in report['learning_outcomes']:
        print(f"   ✅ {outcome}")
    
    print("\n🌟 موفق باشید در مسیر یادگیری!")

print("✅ تمرین 30: پروژه نهایی تکمیل شد!")

# 🎓 خلاصه کامل پروژه:
# این پروژه شامل 30 تمرین از مبتدی تا پیشرفته است که یک ربات تلگرام کامل را می‌سازد.
# هر تمرین یک جنبه خاص از برنامه‌نویسی را آموزش می‌دهد.
# در نهایت، تمام آموخته‌ها در یک سیستم کامل ترکیب می‌شوند.