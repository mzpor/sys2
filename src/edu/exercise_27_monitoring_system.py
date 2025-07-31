 """
تمرین 27: سیستم مانیتورینگ
سطح: پیشرفته
هدف: آشنایی با مانیتورینگ و نظارت
"""

import psutil
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque

class SystemMonitor:
    """مانیتورینگ سیستم"""
    
    def __init__(self):
        self.metrics = defaultdict(deque)
        self.alerts = []
        self.thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90,
            'response_time': 5.0
        }
        self.monitoring_active = False
    
    def start_monitoring(self):
        """شروع مانیتورینگ"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("📊 مانیتورینگ سیستم شروع شد")
    
    def stop_monitoring(self):
        """توقف مانیتورینگ"""
        self.monitoring_active = False
        print("🛑 مانیتورینگ سیستم متوقف شد")
    
    def _monitor_loop(self):
        """حلقه مانیتورینگ"""
        while self.monitoring_active:
            try:
                # جمع‌آوری متریک‌ها
                metrics = self._collect_metrics()
                
                # ذخیره متریک‌ها
                timestamp = time.time()
                for key, value in metrics.items():
                    self.metrics[key].append((timestamp, value))
                    
                    # نگهداری فقط 1000 رکورد آخر
                    if len(self.metrics[key]) > 1000:
                        self.metrics[key].popleft()
                
                # بررسی هشدارها
                self._check_alerts(metrics)
                
                time.sleep(30)  # بررسی هر 30 ثانیه
                
            except Exception as e:
                print(f"❌ خطا در مانیتورینگ: {e}")
                time.sleep(60)
    
    def _collect_metrics(self) -> dict:
        """جمع‌آوری متریک‌های سیستم"""
        metrics = {}
        
        # CPU
        metrics['cpu_percent'] = psutil.cpu_percent(interval=1)
        
        # Memory
        memory = psutil.virtual_memory()
        metrics['memory_percent'] = memory.percent
        metrics['memory_available'] = memory.available / (1024**3)  # GB
        
        # Disk
        disk = psutil.disk_usage('/')
        metrics['disk_percent'] = disk.percent
        metrics['disk_free'] = disk.free / (1024**3)  # GB
        
        # Network
        network = psutil.net_io_counters()
        metrics['network_bytes_sent'] = network.bytes_sent
        metrics['network_bytes_recv'] = network.bytes_recv
        
        # Process info
        process = psutil.Process()
        metrics['process_cpu_percent'] = process.cpu_percent()
        metrics['process_memory_percent'] = process.memory_percent()
        
        return metrics
    
    def _check_alerts(self, metrics: dict):
        """بررسی هشدارها"""
        for metric, value in metrics.items():
            if metric in self.thresholds:
                threshold = self.thresholds[metric]
                if value > threshold:
                    alert = {
                        'metric': metric,
                        'value': value,
                        'threshold': threshold,
                        'timestamp': datetime.now(),
                        'severity': 'high' if value > threshold * 1.5 else 'medium'
                    }
                    self.alerts.append(alert)
                    self._send_alert(alert)
    
    def _send_alert(self, alert: dict):
        """ارسال هشدار"""
        message = f"""
🚨 هشدار سیستم:
متریک: {alert['metric']}
مقدار: {alert['value']:.2f}
آستانه: {alert['threshold']}
شدت: {alert['severity']}
زمان: {alert['timestamp']}
        """
        print(message.strip())

class BotMonitor:
    """مانیتورینگ ربات"""
    
    def __init__(self):
        self.bot_metrics = defaultdict(int)
        self.response_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.user_activity = defaultdict(int)
        self.start_time = time.time()
    
    def track_message(self, user_id: int, message_type: str):
        """پیگیری پیام"""
        self.bot_metrics['total_messages'] += 1
        self.bot_metrics[f'{message_type}_messages'] += 1
        self.user_activity[user_id] += 1
    
    def track_response_time(self, response_time: float):
        """پیگیری زمان پاسخ"""
        self.response_times.append(response_time)
    
    def track_error(self, error_type: str):
        """پیگیری خطا"""
        self.error_counts[error_type] += 1
        self.bot_metrics['total_errors'] += 1
    
    def track_registration(self, user_id: int):
        """پیگیری ثبت‌نام"""
        self.bot_metrics['total_registrations'] += 1
        self.user_activity[user_id] += 5  # امتیاز بیشتر برای ثبت‌نام
    
    def track_payment(self, user_id: int, amount: float):
        """پیگیری پرداخت"""
        self.bot_metrics['total_payments'] += 1
        self.bot_metrics['total_payment_amount'] += amount
        self.user_activity[user_id] += 10  # امتیاز بیشتر برای پرداخت
    
    def get_bot_stats(self) -> dict:
        """دریافت آمار ربات"""
        uptime = time.time() - self.start_time
        
        stats = {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'total_messages': self.bot_metrics['total_messages'],
            'total_registrations': self.bot_metrics['total_registrations'],
            'total_payments': self.bot_metrics['total_payments'],
            'total_errors': self.bot_metrics['total_errors'],
            'active_users': len(self.user_activity),
            'avg_response_time': sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            'error_rate': self.bot_metrics['total_errors'] / max(self.bot_metrics['total_messages'], 1) * 100
        }
        
        return stats
    
    def get_top_users(self, limit: int = 10) -> list:
        """دریافت کاربران فعال"""
        sorted_users = sorted(
            self.user_activity.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_users[:limit]
    
    def get_error_report(self) -> dict:
        """گزارش خطاها"""
        return dict(self.error_counts)

class HealthChecker:
    """بررسی سلامت سیستم"""
    
    def __init__(self):
        self.health_checks = []
        self.last_check = {}
    
    def add_health_check(self, name: str, check_func):
        """اضافه کردن بررسی سلامت"""
        self.health_checks.append((name, check_func))
    
    def run_health_checks(self) -> dict:
        """اجرای بررسی‌های سلامت"""
        results = {}
        
        for name, check_func in self.health_checks:
            try:
                start_time = time.time()
                result = check_func()
                response_time = time.time() - start_time
                
                results[name] = {
                    'status': 'healthy' if result else 'unhealthy',
                    'response_time': response_time,
                    'timestamp': datetime.now()
                }
                
                self.last_check[name] = results[name]
                
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now()
                }
        
        return results
    
    def is_system_healthy(self) -> bool:
        """بررسی سلامت کلی سیستم"""
        checks = self.run_health_checks()
        return all(check['status'] == 'healthy' for check in checks.values())

# ایجاد نمونه‌های مانیتورینگ
system_monitor = SystemMonitor()
bot_monitor = BotMonitor()
health_checker = HealthChecker()

def setup_monitoring():
    """راه‌اندازی مانیتورینگ"""
    
    # اضافه کردن بررسی‌های سلامت
    def check_database():
        try:
            # بررسی اتصال به پایگاه داده
            return True
        except:
            return False
    
    def check_api_connection():
        try:
            # بررسی اتصال به API
            return True
        except:
            return False
    
    def check_memory_usage():
        memory = psutil.virtual_memory()
        return memory.percent < 90
    
    health_checker.add_health_check('database', check_database)
    health_checker.add_health_check('api_connection', check_api_connection)
    health_checker.add_health_check('memory_usage', check_memory_usage)
    
    # شروع مانیتورینگ سیستم
    system_monitor.start_monitoring()

def enhanced_message_processing(message: dict):
    """پردازش پیام با مانیتورینگ"""
    start_time = time.time()
    
    try:
        # پردازش پیام
        if 'message' in message:
            user_id = message['message']['from']['id']
            text = message['message'].get('text', '')
            
            # پیگیری متریک‌ها
            bot_monitor.track_message(user_id, 'text')
            
            # پردازش
            result = process_message(message)
            
            # محاسبه زمان پاسخ
            response_time = time.time() - start_time
            bot_monitor.track_response_time(response_time)
            
            return result
        
    except Exception as e:
        bot_monitor.track_error('message_processing')
        print(f"❌ خطا در پردازش پیام: {e}")
        return False

def get_monitoring_dashboard():
    """دریافت داشبورد مانیتورینگ"""
    dashboard = {
        'system': {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        },
        'bot': bot_monitor.get_bot_stats(),
        'health': health_checker.run_health_checks(),
        'alerts': system_monitor.alerts[-10:] if system_monitor.alerts else [],
        'top_users': bot_monitor.get_top_users(5),
        'error_report': bot_monitor.get_error_report()
    }
    
    return dashboard

def print_monitoring_report():
    """چاپ گزارش مانیتورینگ"""
    dashboard = get_monitoring_dashboard()
    
    print("\n📊 گزارش مانیتورینگ:")
    print("=" * 50)
    
    # آمار سیستم
    print(f"💻 CPU: {dashboard['system']['cpu_percent']:.1f}%")
    print(f"🧠 Memory: {dashboard['system']['memory_percent']:.1f}%")
    print(f"💾 Disk: {dashboard['system']['disk_percent']:.1f}%")
    
    # آمار ربات
    bot_stats = dashboard['bot']
    print(f"🤖 Uptime: {bot_stats['uptime_hours']:.1f} ساعت")
    print(f"📨 Total Messages: {bot_stats['total_messages']}")
    print(f"👥 Active Users: {bot_stats['active_users']}")
    print(f"⏱️ Avg Response Time: {bot_stats['avg_response_time']:.3f}s")
    print(f"❌ Error Rate: {bot_stats['error_rate']:.2f}%")
    
    # سلامت سیستم
    health_status = "✅ Healthy" if health_checker.is_system_healthy() else "❌ Unhealthy"
    print(f"🏥 System Health: {health_status}")

print("✅ تمرین 27: سیستم مانیتورینگ تکمیل شد!")

# راه‌اندازی مانیتورینگ
setup_monitoring()

# تمرین: تابعی برای ارسال هشدار به تلگرام بنویسید
# تمرین: تابعی برای ذخیره متریک‌ها در فایل بنویسید
# تمرین: تابعی برای نمایش نمودار عملکرد بنویسید