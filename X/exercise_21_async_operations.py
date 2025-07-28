 """
تمرین 21: عملیات ناهمزمان
سطح: پیشرفته
هدف: آشنایی با برنامه‌نویسی ناهمزمان
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any

class AsyncBotManager:
    """مدیریت ناهمزمان ربات"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://tapi.bale.ai/bot{bot_token}"
        self.session = None
    
    async def init_session(self):
        """راه‌اندازی جلسه HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """بستن جلسه HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def send_message_async(self, chat_id: int, text: str, reply_markup: Dict = None):
        """
        ارسال پیام به صورت ناهمزمان
        
        پارامترها:
            chat_id (int): شناسه چت
            text (str): متن پیام
            reply_markup (dict): کیبورد پاسخ
        """
        await self.init_session()
        
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        try:
            async with self.session.post(f"{self.base_url}/sendMessage", json=payload) as response:
                result = await response.json()
                if response.status == 200:
                    print(f"✅ پیام به {chat_id} ارسال شد")
                    return result
                else:
                    print(f"❌ خطا در ارسال پیام: {result}")
                    return None
        except Exception as e:
            print(f"❌ خطا در ارسال پیام: {e}")
            return None
    
    async def get_updates_async(self, offset: int = None):
        """
        دریافت آپدیت‌ها به صورت ناهمزمان
        
        پارامترها:
            offset (int): شناسه آخرین آپدیت
        
        خروجی:
            dict: آپدیت‌های دریافتی
        """
        await self.init_session()
        
        params = {}
        if offset:
            params["offset"] = offset
        
        try:
            async with self.session.get(f"{self.base_url}/getUpdates", params=params) as response:
                result = await response.json()
                return result
        except Exception as e:
            print(f"❌ خطا در دریافت آپدیت‌ها: {e}")
            return {"result": []}
    
    async def broadcast_message(self, chat_ids: List[int], text: str, reply_markup: Dict = None):
        """
        ارسال پیام به چندین چت به صورت ناهمزمان
        
        پارامترها:
            chat_ids (list): لیست شناسه‌های چت
            text (str): متن پیام
            reply_markup (dict): کیبورد پاسخ
        """
        tasks = []
        for chat_id in chat_ids:
            task = self.send_message_async(chat_id, text, reply_markup)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for result in results if result is not None)
        print(f"📤 {success_count} از {len(chat_ids)} پیام با موفقیت ارسال شد")
        
        return results
    
    async def process_updates_batch(self, updates: List[Dict]):
        """
        پردازش دسته‌ای آپدیت‌ها
        
        پارامترها:
            updates (list): لیست آپدیت‌ها
        """
        tasks = []
        
        for update in updates:
            if 'message' in update:
                task = self.process_message_async(update['message'])
                tasks.append(task)
            elif 'callback_query' in update:
                task = self.process_callback_async(update['callback_query'])
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def process_message_async(self, message: Dict):
        """
        پردازش پیام به صورت ناهمزمان
        
        پارامترها:
            message (dict): پیام دریافتی
        """
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        text = message.get('text', '')
        
        # پردازش دستورات
        if text == '/start':
            await self.show_main_menu_async(chat_id, user_id)
        elif text == '/help':
            await self.show_help_async(chat_id, user_id)
        else:
            await self.handle_text_message_async(chat_id, user_id, text)
    
    async def process_callback_async(self, callback_query: Dict):
        """
        پردازش callback به صورت ناهمزمان
        
        پارامترها:
            callback_query (dict): callback دریافتی
        """
        chat_id = callback_query['message']['chat']['id']
        user_id = callback_query['from']['id']
        data = callback_query.get('data', '')
        
        await self.handle_callback_async(chat_id, user_id, data)
    
    async def show_main_menu_async(self, chat_id: int, user_id: int):
        """نمایش منوی اصلی به صورت ناهمزمان"""
        welcome_text = "به ربات تلاوت خوش آمدید!"
        keyboard = create_keyboard([
            [{'text': '📚 ثبت نام', 'callback_data': 'register'}],
            [{'text': 'ℹ️ راهنما', 'callback_data': 'help'}]
        ])
        
        await self.send_message_async(chat_id, welcome_text, keyboard)
    
    async def show_help_async(self, chat_id: int, user_id: int):
        """نمایش راهنما به صورت ناهمزمان"""
        help_text = """
📖 راهنمای ربات:

/start - شروع ربات
/help - نمایش این راهنما
/classes - مشاهده کلاس‌ها
/account - حساب کاربری
        """
        
        await self.send_message_async(chat_id, help_text)
    
    async def handle_text_message_async(self, chat_id: int, user_id: int, text: str):
        """پردازش پیام متنی به صورت ناهمزمان"""
        response = f"پیام شما: {text}"
        await self.send_message_async(chat_id, response)
    
    async def handle_callback_async(self, chat_id: int, user_id: int, data: str):
        """پردازش callback به صورت ناهمزمان"""
        if data == 'register':
            await self.start_registration_async(chat_id, user_id)
        elif data == 'help':
            await self.show_help_async(chat_id, user_id)
        else:
            await self.send_message_async(chat_id, "دکمه انتخابی نامعتبر است.")
    
    async def start_registration_async(self, chat_id: int, user_id: int):
        """شروع ثبت‌نام به صورت ناهمزمان"""
        message = "لطفاً نام و نام خانوادگی خود را وارد کنید:"
        await self.send_message_async(chat_id, message)
    
    async def run_bot_async(self):
        """اجرای اصلی ربات به صورت ناهمزمان"""
        print("🤖 ربات ناهمزمان شروع شد...")
        
        offset = None
        
        try:
            while True:
                # دریافت آپدیت‌ها
                updates_response = await self.get_updates_async(offset)
                
                if 'result' in updates_response:
                    updates = updates_response['result']
                    
                    if updates:
                        # به‌روزرسانی offset
                        offset = updates[-1]['update_id'] + 1
                        
                        # پردازش آپدیت‌ها
                        await self.process_updates_batch(updates)
                
                # تاخیر بین درخواست‌ها
                await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            print("🛑 ربات متوقف شد")
        finally:
            await self.close_session()

def run_async_bot():
    """اجرای ربات ناهمزمان"""
    bot_manager = AsyncBotManager("YOUR_BOT_TOKEN")
    
    try:
        asyncio.run(bot_manager.run_bot_async())
    except Exception as e:
        print(f"❌ خطا در اجرای ربات: {e}")

print("✅ تمرین 21: عملیات ناهمزمان تکمیل شد!")

# تمرین: تابعی برای پردازش همزمان چندین درخواست بنویسید
# تمرین: تابعی برای مدیریت صف پیام‌ها بنویسید
# تمرین: تابعی برای محدود کردن نرخ درخواست‌ها بنویسید