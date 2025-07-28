 """
تمرین 22: سیستم Webhook
سطح: پیشرفته
هدف: آشنایی با سیستم Webhook
"""

from flask import Flask, request, jsonify
import threading
import time

class WebhookBot:
    """ربات با سیستم Webhook"""
    
    def __init__(self, bot_token: str, webhook_url: str = None):
        self.bot_token = bot_token
        self.base_url = f"https://tapi.bale.ai/bot{bot_token}"
        self.webhook_url = webhook_url
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """راه‌اندازی مسیرهای Flask"""
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook_handler():
            """پردازش Webhook"""
            try:
                data = request.get_json()
                self.process_webhook_update(data)
                return jsonify({'status': 'ok'})
            except Exception as e:
                print(f"❌ خطا در پردازش Webhook: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """بررسی سلامت سیستم"""
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'bot_token': self.bot_token[:10] + '...'
            })
        
        @self.app.route('/stats', methods=['GET'])
        def get_stats():
            """دریافت آمار"""
            return jsonify({
                'total_users': len(registered_users),
                'active_sessions': len(user_states),
                'total_classes': len(CLASSES)
            })
    
    def set_webhook(self, webhook_url: str):
        """
        تنظیم Webhook
        
        پارامترها:
            webhook_url (str): آدرس Webhook
        """
        try:
            import requests
            
            payload = {
                'url': webhook_url,
                'allowed_updates': ['message', 'callback_query']
            }
            
            response = requests.post(f"{self.base_url}/setWebhook", json=payload)
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ Webhook تنظیم شد: {webhook_url}")
                return True
            else:
                print(f"❌ خطا در تنظیم Webhook: {result}")
                return False
        
        except Exception as e:
            print(f"❌ خطا در تنظیم Webhook: {e}")
            return False
    
    def delete_webhook(self):
        """حذف Webhook"""
        try:
            import requests
            
            response = requests.post(f"{self.base_url}/deleteWebhook")
            result = response.json()
            
            if result.get('ok'):
                print("✅ Webhook حذف شد")
                return True
            else:
                print(f"❌ خطا در حذف Webhook: {result}")
                return False
        
        except Exception as e:
            print(f"❌ خطا در حذف Webhook: {e}")
            return False
    
    def process_webhook_update(self, update: dict):
        """
        پردازش آپدیت Webhook
        
        پارامترها:
            update (dict): آپدیت دریافتی
        """
        print(f"📥 دریافت Webhook: {update.keys()}")
        
        if 'message' in update:
            self.process_webhook_message(update['message'])
        elif 'callback_query' in update:
            self.process_webhook_callback(update['callback_query'])
    
    def process_webhook_message(self, message: dict):
        """
        پردازش پیام Webhook
        
        پارامترها:
            message (dict): پیام دریافتی
        """
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        text = message.get('text', '')
        
        print(f"💬 پیام از {user_id}: {text}")
        
        # پردازش در thread جداگانه
        thread = threading.Thread(
            target=self.handle_message_thread,
            args=(chat_id, user_id, text)
        )
        thread.start()
    
    def process_webhook_callback(self, callback_query: dict):
        """
        پردازش Callback Webhook
        
        پارامترها:
            callback_query (dict): Callback دریافتی
        """
        chat_id = callback_query['message']['chat']['id']
        user_id = callback_query['from']['id']
        data = callback_query.get('data', '')
        
        print(f"🔘 Callback از {user_id}: {data}")
        
        # پردازش در thread جداگانه
        thread = threading.Thread(
            target=self.handle_callback_thread,
            args=(chat_id, user_id, data)
        )
        thread.start()
    
    def handle_message_thread(self, chat_id: int, user_id: int, text: str):
        """پردازش پیام در thread جداگانه"""
        try:
            if text == '/start':
                self.show_main_menu(chat_id, user_id)
            elif text == '/help':
                self.show_help(chat_id, user_id)
            else:
                self.handle_text_message(chat_id, user_id, text)
        except Exception as e:
            print(f"❌ خطا در پردازش پیام: {e}")
    
    def handle_callback_thread(self, chat_id: int, user_id: int, data: str):
        """پردازش callback در thread جداگانه"""
        try:
            if data == 'register':
                self.start_registration(chat_id, user_id)
            elif data == 'help':
                self.show_help(chat_id, user_id)
            else:
                self.send_message(chat_id, "دکمه انتخابی نامعتبر است.")
        except Exception as e:
            print(f"❌ خطا در پردازش callback: {e}")
    
    def show_main_menu(self, chat_id: int, user_id: int):
        """نمایش منوی اصلی"""
        welcome_text = "به ربات تلاوت خوش آمدید!"
        keyboard = create_keyboard([
            [{'text': '📚 ثبت نام', 'callback_data': 'register'}],
            [{'text': 'ℹ️ راهنما', 'callback_data': 'help'}]
        ])
        
        self.send_message(chat_id, welcome_text, keyboard)
    
    def show_help(self, chat_id: int, user_id: int):
        """نمایش راهنما"""
        help_text = """
📖 راهنمای ربات:

/start - شروع ربات
/help - نمایش این راهنما
/classes - مشاهده کلاس‌ها
/account - حساب کاربری
        """
        
        self.send_message(chat_id, help_text)
    
    def handle_text_message(self, chat_id: int, user_id: int, text: str):
        """پردازش پیام متنی"""
        response = f"پیام شما: {text}"
        self.send_message(chat_id, response)
    
    def start_registration(self, chat_id: int, user_id: int):
        """شروع ثبت‌نام"""
        message = "لطفاً نام و نام خانوادگی خود را وارد کنید:"
        self.send_message(chat_id, message)
    
    def send_message(self, chat_id: int, text: str, reply_markup: dict = None):
        """ارسال پیام"""
        try:
            import requests
            
            payload = {
                'chat_id': chat_id,
                'text': text
            }
            
            if reply_markup:
                payload['reply_markup'] = reply_markup
            
            response = requests.post(f"{self.base_url}/sendMessage", json=payload)
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ پیام به {chat_id} ارسال شد")
            else:
                print(f"❌ خطا در ارسال پیام: {result}")
        
        except Exception as e:
            print(f"❌ خطا در ارسال پیام: {e}")
    
    def run_webhook_server(self, host: str = '0.0.0.0', port: int = 5000):
        """
        اجرای سرور Webhook
        
        پارامترها:
            host (str): آدرس سرور
            port (int): پورت سرور
        """
        print(f"🌐 سرور Webhook در حال اجرا روی {host}:{port}")
        self.app.run(host=host, port=port, debug=False)

def create_webhook_bot(bot_token: str, webhook_url: str):
    """ایجاد ربات Webhook"""
    bot = WebhookBot(bot_token, webhook_url)
    
    # تنظیم Webhook
    if webhook_url:
        bot.set_webhook(webhook_url)
    
    return bot

print("✅ تمرین 22: سیستم Webhook تکمیل شد!")

# مثال استفاده:
# bot = create_webhook_bot("YOUR_BOT_TOKEN", "https://your-domain.com/webhook")
# bot.run_webhook_server()

# تمرین: تابعی برای مدیریت چندین Webhook بنویسید
# تمرین: تابعی برای امنیت Webhook بنویسید
# تمرین: تابعی برای مانیتورینگ Webhook بنویسید