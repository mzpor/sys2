 """
تمرین 25: بهینه‌سازی عملکرد
سطح: پیشرفته
هدف: آشنایی با بهینه‌سازی کد
"""

import time
import threading
from collections import defaultdict, deque
from functools import lru_cache
import gc

class PerformanceMonitor:
    """مانیتورینگ عملکرد"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_times = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def start_timer(self, operation: str):
        """شروع تایمر"""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str):
        """پایان تایمر"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.metrics[operation].append(duration)
            del self.start_times[operation]
    
    def get_average_time(self, operation: str) -> float:
        """دریافت میانگین زمان"""
        times = self.metrics.get(operation, [])
        return sum(times) / len(times) if times else 0
    
    def get_performance_report(self) -> dict:
        """دریافت گزارش عملکرد"""
        report = {}
        for operation, times in self.metrics.items():
            if times:
                report[operation] = {
                    'count': len(times),
                    'average': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times)
                }
        
        report['cache'] = {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        }
        
        return report

# ایجاد مانیتور عملکرد
perf_monitor = PerformanceMonitor()

class OptimizedBot:
    """ربات بهینه‌سازی شده"""
    
    def __init__(self):
        self.message_cache = {}
        self.user_cache = {}
        self.class_cache = {}
        self.cache_ttl = 300  # 5 دقیقه
        self.max_cache_size = 1000
    
    @lru_cache(maxsize=128)
    def get_class_info(self, class_id: str) -> dict:
        """دریافت اطلاعات کلاس با کش"""
        perf_monitor.start_timer('get_class_info')
        
        if class_id in CLASSES:
            result = CLASSES[class_id]
        else:
            result = {}
        
        perf_monitor.end_timer('get_class_info')
        return result
    
    def get_user_info_cached(self, user_id: int) -> dict:
        """دریافت اطلاعات کاربر با کش"""
        current_time = time.time()
        
        # بررسی کش
        if user_id in self.user_cache:
            cache_entry = self.user_cache[user_id]
            if current_time - cache_entry['timestamp'] < self.cache_ttl:
                perf_monitor.cache_hits += 1
                return cache_entry['data']
        
        perf_monitor.cache_misses += 1
        
        # دریافت از منبع اصلی
        user_data = registered_users.get(user_id, {})
        
        # ذخیره در کش
        self.user_cache[user_id] = {
            'data': user_data,
            'timestamp': current_time
        }
        
        # مدیریت اندازه کش
        if len(self.user_cache) > self.max_cache_size:
            self._cleanup_cache()
        
        return user_data
    
    def _cleanup_cache(self):
        """پاکسازی کش"""
        current_time = time.time()
        
        # حذف ورودی‌های منقضی شده
        expired_keys = [
            key for key, entry in self.user_cache.items()
            if current_time - entry['timestamp'] > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.user_cache[key]
    
    def batch_send_messages(self, messages: list):
        """ارسال دسته‌ای پیام‌ها"""
        perf_monitor.start_timer('batch_send_messages')
        
        results = []
        for message_data in messages:
            chat_id = message_data['chat_id']
            text = message_data['text']
            reply_markup = message_data.get('reply_markup')
            
            try:
                result = send_message(chat_id, text, reply_markup)
                results.append({'success': True, 'chat_id': chat_id})
            except Exception as e:
                results.append({'success': False, 'chat_id': chat_id, 'error': str(e)})
        
        perf_monitor.end_timer('batch_send_messages')
        return results
    
    def process_messages_batch(self, messages: list):
        """پردازش دسته‌ای پیام‌ها"""
        perf_monitor.start_timer('process_messages_batch')
        
        # گروه‌بندی پیام‌ها بر اساس نوع
        text_messages = []
        callback_messages = []
        
        for message in messages:
            if 'message' in message:
                text_messages.append(message)
            elif 'callback_query' in message:
                callback_messages.append(message)
        
        # پردازش موازی
        with threading.ThreadPoolExecutor(max_workers=2) as executor:
            text_future = executor.submit(self._process_text_messages, text_messages)
            callback_future = executor.submit(self._process_callback_messages, callback_messages)
            
            text_results = text_future.result()
            callback_results = callback_future.result()
        
        perf_monitor.end_timer('process_messages_batch')
        return text_results + callback_results
    
    def _process_text_messages(self, messages: list):
        """پردازش پیام‌های متنی"""
        results = []
        for message in messages:
            try:
                process_message(message)
                results.append({'success': True, 'type': 'text'})
            except Exception as e:
                results.append({'success': False, 'type': 'text', 'error': str(e)})
        return results
    
    def _process_callback_messages(self, messages: list):
        """پردازش پیام‌های callback"""
        results = []
        for message in messages:
            try:
                handle_callback_query(message)
                results.append({'success': True, 'type': 'callback'})
            except Exception as e:
                results.append({'success': False, 'type': 'callback', 'error': str(e)})
        return results

class MemoryOptimizer:
    """بهینه‌سازی حافظه"""
    
    def __init__(self):
        self.object_counts = defaultdict(int)
        self.memory_threshold = 1000
    
    def track_object(self, obj_type: str):
        """پیگیری اشیاء"""
        self.object_counts[obj_type] += 1
    
    def check_memory_usage(self):
        """بررسی استفاده از حافظه"""
        total_objects = sum(self.object_counts.values())
        
        if total_objects > self.memory_threshold:
            self._cleanup_memory()
    
    def _cleanup_memory(self):
        """پاکسازی حافظه"""
        # پاک کردن کش‌ها
        if hasattr(globals(), 'user_cache'):
            user_cache.clear()
        
        # پاک کردن وضعیت‌های قدیمی
        current_time = time.time()
        expired_states = [
            user_id for user_id, state in user_states.items()
            if current_time - state.get('timestamp', 0) > 3600  # 1 ساعت
        ]
        
        for user_id in expired_states:
            del user_states[user_id]
        
        # اجرای garbage collector
        gc.collect()
        
        print("🧹 پاکسازی حافظه انجام شد")

class DatabaseOptimizer:
    """بهینه‌سازی پایگاه داده"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.query_cache = {}
        self.batch_operations = []
    
    def batch_insert_users(self, users_data: list):
        """درج دسته‌ای کاربران"""
        if not users_data:
            return
        
        # گروه‌بندی عملیات
        for user_data in users_data:
            self.batch_operations.append(('insert_user', user_data))
        
        # اجرای دسته‌ای
        if len(self.batch_operations) >= 10:
            self._execute_batch_operations()
    
    def _execute_batch_operations(self):
        """اجرای عملیات دسته‌ای"""
        if not self.batch_operations:
            return
        
        # اینجا باید با پایگاه داده واقعی کار شود
        print(f"📦 اجرای {len(self.batch_operations)} عملیات دسته‌ای")
        self.batch_operations.clear()
    
    def optimize_queries(self):
        """بهینه‌سازی کوئری‌ها"""
        # حذف کوئری‌های تکراری
        unique_queries = set()
        optimized_operations = []
        
        for operation in self.batch_operations:
            query_key = f"{operation[0]}_{hash(str(operation[1]))}"
            if query_key not in unique_queries:
                unique_queries.add(query_key)
                optimized_operations.append(operation)
        
        self.batch_operations = optimized_operations

# ایجاد نمونه‌های بهینه‌سازی
optimized_bot = OptimizedBot()
memory_optimizer = MemoryOptimizer()
db_optimizer = DatabaseOptimizer(db_manager)

def optimized_message_processing(message: dict):
    """پردازش بهینه پیام"""
    perf_monitor.start_timer('message_processing')
    
    try:
        # بررسی حافظه
        memory_optimizer.check_memory_usage()
        
        # پردازش پیام
        if 'message' in message:
            chat_id = message['message']['chat']['id']
            user_id = message['message']['from']['id']
            
            # استفاده از کش
            user_info = optimized_bot.get_user_info_cached(user_id)
            
            # پردازش
            process_message(message)
            
            # پیگیری شیء
            memory_optimizer.track_object('message')
        
        perf_monitor.end_timer('message_processing')
        return True
    
    except Exception as e:
        print(f"❌ خطا در پردازش پیام: {e}")
        return False

def get_performance_stats():
    """دریافت آمار عملکرد"""
    return perf_monitor.get_performance_report()

print("✅ تمرین 25: بهینه‌سازی عملکرد تکمیل شد!")

# تمرین: تابعی برای بهینه‌سازی کوئری‌ها بنویسید
# تمرین: تابعی برای مدیریت حافظه پیشرفته بنویسید
# تمرین: تابعی برای بهینه‌سازی شبکه بنویسید