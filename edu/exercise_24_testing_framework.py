 """
تمرین 24: چارچوب تست
سطح: پیشرفته
هدف: آشنایی با تست‌نویسی پیشرفته
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import time

class BotTestCase(unittest.TestCase):
    """کلاس پایه برای تست‌های ربات"""
    
    def setUp(self):
        """راه‌اندازی قبل از هر تست"""
        self.mock_message = {
            'message': {
                'chat': {'id': 12345},
                'from': {'id': 67890, 'first_name': 'علی'},
                'text': '/start'
            }
        }
        
        self.mock_callback = {
            'callback_query': {
                'message': {'chat': {'id': 12345}},
                'from': {'id': 67890},
                'data': 'test_callback'
            }
        }
    
    def tearDown(self):
        """پاکسازی بعد از هر تست"""
        # پاک کردن داده‌های تست
        if 67890 in user_states:
            del user_states[67890]
        if 67890 in registered_users:
            del registered_users[67890]

class TestMessageProcessing(BotTestCase):
    """تست پردازش پیام‌ها"""
    
    @patch('requests.post')
    def test_send_message_success(self, mock_post):
        """تست ارسال پیام موفق"""
        # تنظیم mock
        mock_response = Mock()
        mock_response.json.return_value = {'ok': True}
        mock_post.return_value = mock_response
        
        # تست ارسال پیام
        result = send_message(12345, "تست پیام")
        
        # بررسی فراخوانی
        mock_post.assert_called_once()
        self.assertTrue(result)
    
    @patch('requests.post')
    def test_send_message_failure(self, mock_post):
        """تست ارسال پیام ناموفق"""
        # تنظیم mock
        mock_response = Mock()
        mock_response.json.return_value = {'ok': False, 'error_code': 400}
        mock_post.return_value = mock_response
        
        # تست ارسال پیام
        result = send_message(12345, "تست پیام")
        
        # بررسی نتیجه
        self.assertFalse(result)
    
    def test_process_message_start_command(self):
        """تست پردازش دستور /start"""
        # تنظیم داده‌های تست
        message = {
            'message': {
                'chat': {'id': 12345},
                'from': {'id': 67890},
                'text': '/start'
            }
        }
        
        # اجرای تست
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {'ok': True}
            mock_post.return_value = mock_response
            
            process_message(message)
            
            # بررسی فراخوانی
            mock_post.assert_called()

class TestRegistrationSystem(BotTestCase):
    """تست سیستم ثبت‌نام"""
    
    def test_start_registration(self):
        """تست شروع ثبت‌نام"""
        chat_id = 12345
        user_id = 67890
        
        # اجرای تست
        start_registration(chat_id, user_id)
        
        # بررسی وضعیت
        self.assertIn(user_id, user_states)
        self.assertEqual(user_states[user_id]['step'], 'waiting_name_lastname')
    
    def test_name_validation(self):
        """تست اعتبارسنجی نام"""
        # تست نام معتبر
        valid_names = ["علی محمدی", "Ali Mohammadi", "احمد رضایی"]
        for name in valid_names:
            is_valid, cleaned, error = validate_name(name)
            self.assertTrue(is_valid, f"نام '{name}' باید معتبر باشد")
        
        # تست نام نامعتبر
        invalid_names = ["ع", "123", "", "علی123"]
        for name in invalid_names:
            is_valid, cleaned, error = validate_name(name)
            self.assertFalse(is_valid, f"نام '{name}' نباید معتبر باشد")
    
    def test_phone_validation(self):
        """تست اعتبارسنجی تلفن"""
        # تست تلفن معتبر
        valid_phones = ["09123456789", "09123456789"]
        for phone in valid_phones:
            is_valid, cleaned, error = validate_phone(phone)
            self.assertTrue(is_valid, f"تلفن '{phone}' باید معتبر باشد")
        
        # تست تلفن نامعتبر
        invalid_phones = ["123", "08123456789", "912345678"]
        for phone in invalid_phones:
            is_valid, cleaned, error = validate_phone(phone)
            self.assertFalse(is_valid, f"تلفن '{phone}' نباید معتبر باشد")

class TestClassSystem(BotTestCase):
    """تست سیستم کلاس‌ها"""
    
    def test_show_classes(self):
        """تست نمایش کلاس‌ها"""
        chat_id = 12345
        user_id = 67890
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {'ok': True}
            mock_post.return_value = mock_response
            
            show_classes(chat_id, user_id)
            
            # بررسی فراخوانی
            mock_post.assert_called()
    
    def test_class_selection(self):
        """تست انتخاب کلاس"""
        chat_id = 12345
        user_id = 67890
        class_id = "quran_recitation"
        
        # تنظیم وضعیت
        user_states[user_id] = {'step': 'selecting_class'}
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {'ok': True}
            mock_post.return_value = mock_response
            
            handle_class_selection(chat_id, user_id, class_id)
            
            # بررسی فراخوانی
            mock_post.assert_called()

class TestPaymentSystem(BotTestCase):
    """تست سیستم پرداخت"""
    
    def test_payment_link_generation(self):
        """تست تولید لینک پرداخت"""
        chat_id = 12345
        user_id = 67890
        class_id = "quran_recitation"
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {'ok': True}
            mock_post.return_value = mock_response
            
            show_payment_link(chat_id, user_id, class_id)
            
            # بررسی فراخوانی
            mock_post.assert_called()
    
    def test_payment_completion(self):
        """تست تکمیل پرداخت"""
        chat_id = 12345
        user_id = 67890
        
        # تنظیم داده‌های تست
        user_states[user_id] = {
            'first_name': 'علی',
            'last_name': 'محمدی',
            'mobile': '09123456789',
            'national_id': '1234567890',
            'selected_class': 'quran_recitation'
        }
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {'ok': True}
            mock_post.return_value = mock_response
            
            handle_payment_completion(chat_id, user_id)
            
            # بررسی ثبت‌نام
            self.assertIn(user_id, registered_users)
            self.assertEqual(registered_users[user_id]['registered_class'], 'quran_recitation')

class TestSecuritySystem(BotTestCase):
    """تست سیستم امنیت"""
    
    def test_rate_limiting(self):
        """تست محدودیت نرخ"""
        user_id = 67890
        action = "message"
        
        # تست محدودیت
        for i in range(10):
            result = security_manager.check_rate_limit(user_id, action, limit=10)
            self.assertTrue(result, f"تلاش {i+1} باید مجاز باشد")
        
        # تست تجاوز از محدودیت
        result = security_manager.check_rate_limit(user_id, action, limit=10)
        self.assertFalse(result, "تلاش 11 باید محدود شود")
    
    def test_input_validation(self):
        """تست اعتبارسنجی ورودی"""
        # تست ورودی معتبر
        valid_inputs = ["سلام", "Hello", "123456"]
        for text in valid_inputs:
            result = security_manager.validate_input(text)
            self.assertTrue(result, f"ورودی '{text}' باید معتبر باشد")
        
        # تست ورودی نامعتبر
        invalid_inputs = ["<script>alert('xss')</script>", "javascript:alert('xss')"]
        for text in invalid_inputs:
            result = security_manager.validate_input(text)
            self.assertFalse(result, f"ورودی '{text}' نباید معتبر باشد")

class TestDatabaseOperations(BotTestCase):
    """تست عملیات پایگاه داده"""
    
    def test_user_operations(self):
        """تست عملیات کاربر"""
        user_data = {
            'user_id': 67890,
            'first_name': 'علی',
            'last_name': 'محمدی',
            'mobile': '09123456789',
            'national_id': '1234567890'
        }
        
        # تست اضافه کردن کاربر
        result = db_manager.add_user(user_data)
        self.assertTrue(result)
        
        # تست دریافت کاربر
        user = db_manager.get_user(67890)
        self.assertIsNotNone(user)
        self.assertEqual(user['first_name'], 'علی')

def run_all_tests():
    """اجرای تمام تست‌ها"""
    # ایجاد test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # اضافه کردن تست‌ها
    test_classes = [
        TestMessageProcessing,
        TestRegistrationSystem,
        TestClassSystem,
        TestPaymentSystem,
        TestSecuritySystem,
        TestDatabaseOperations
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # اجرای تست‌ها
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # نمایش نتایج
    print(f"\n📊 نتایج تست‌ها:")
    print(f"تست‌های اجرا شده: {result.testsRun}")
    print(f"تست‌های موفق: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"تست‌های ناموفق: {len(result.failures)}")
    print(f"خطاها: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("🧪 شروع تست‌های ربات...")
    success = run_all_tests()
    
    if success:
        print("✅ تمام تست‌ها با موفقیت اجرا شدند!")
    else:
        print("❌ برخی تست‌ها ناموفق بودند.")

print("✅ تمرین 24: چارچوب تست تکمیل شد!")

# تمرین: تست‌های جدید برای ویژگی‌های خاص بنویسید
# تمرین: تست‌های عملکرد (Performance) بنویسید
# تمرین: تست‌های یکپارچگی (Integration) بنویسید