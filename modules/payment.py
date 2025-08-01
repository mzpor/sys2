import json
import uuid
import logging
import requests

class PaymentModule:
    """ماژول مدیریت پرداخت"""
    
    def __init__(self, bot_token, base_url, payment_token, group_link):
        """مقداردهی اولیه ماژول پرداخت"""
        self.bot_token = bot_token
        self.base_url = base_url
        self.payment_token = payment_token
        self.group_link = group_link
        
        # قیمت کلاس‌ها (به ریال)
        self.class_prices = {
            "کلاس هزار تومانی": 10000,  # 1000 تومان
            "کلاس دو هزار تومانی": 20000  # 2000 تومان
        }
        
        self.user_states = {}
    
    def send_message(self, chat_id, text, reply_markup=None, secondary_reply_markup=None):
        """ارسال پیام به کاربر با پشتیبانی از کیبورد معمولی و شیشه‌ای"""
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup and secondary_reply_markup:
            # ترکیب کیبورد شیشه‌ای و معمولی
            payload["reply_markup"] = reply_markup
            payload["reply_markup"].update(secondary_reply_markup)
        elif reply_markup:
            payload["reply_markup"] = reply_markup
        elif secondary_reply_markup:
            payload["reply_markup"] = secondary_reply_markup
        response = requests.post(f"{self.base_url}/sendMessage", json=payload)
        logging.info(f"ارسال پیام: {response.status_code}, پاسخ: {response.text}")
        return response.json()
    
    def build_reply_keyboard(self, buttons):
        """ساخت کیبورد معمولی"""
        return {
            "keyboard": [[{"text": btn}] for btn in buttons],
            "resize_keyboard": True
        }
    
    def build_inline_keyboard(self, buttons):
        """ساخت کیبورد شیشه‌ای"""
        return {
            "inline_keyboard": [[{"text": btn["text"], "callback_data": btn["callback_data"]}] for btn in buttons]
        }
    
    def send_invoice(self, chat_id, amount, class_name):
        """ارسال پیام صورتحساب به کاربر"""
        payload = {
            "chat_id": chat_id,
            "title": f"پرداخت برای {class_name}",
            "description": f"پرداخت برای ثبت‌نام در {class_name} با مبلغ {amount // 10} تومان",
            "payload": str(uuid.uuid4()),
            "provider_token": self.payment_token,
            "currency": "IRR",
            "prices": [{"label": class_name, "amount": amount}],
            "need_phone_number": True
        }
        try:
            response = requests.post(
                f"{self.base_url}/sendInvoice",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            logging.info(f"وضعیت HTTP (sendInvoice): {response.status_code}")
            logging.info(f"پاسخ خام (sendInvoice): {response.text}")
            response_data = response.json()
            if response_data.get("ok"):
                logging.info(f"صورتحساب با موفقیت برای چت {chat_id} ارسال شد")
                return True
            else:
                logging.error(f"خطای API: {response_data}")
                return False
        except Exception as e:
            logging.error(f"خطا در ارسال صورتحساب: {e}")
            return False
    
    def answer_pre_checkout_query(self, pre_checkout_query_id, ok=True, error_message=None):
        """پاسخ به PreCheckoutQuery"""
        payload = {
            "pre_checkout_query_id": pre_checkout_query_id,
            "ok": ok
        }
        if error_message:
            payload["error_message"] = error_message
        response = requests.post(f"{self.base_url}/answerPreCheckoutQuery", json=payload)
        logging.info(f"پاسخ به PreCheckoutQuery: {response.status_code}, پاسخ: {response.text}")
        return response.json()
    
    def handle_message(self, message):
        """مدیریت پیام‌های دریافتی"""
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        successful_payment = message.get("successful_payment")
        
        if successful_payment:
            selected_class = self.user_states.get(f"payment_class_{user_id}")
            if selected_class:
                self.send_message(chat_id, f"💸 پرداخت برای '{selected_class}' با موفقیت انجام شد!", 
                                reply_markup=self.build_reply_keyboard(["شروع", "خروج", "کلاس"]))
                self.send_message(chat_id, f"📎 لینک ورود به گروه: {self.group_link}", 
                                reply_markup=self.build_reply_keyboard(["شروع", "خروج", "کلاس"]))
                self.send_message(chat_id, "🎉 از اینکه همراه شدید، بی‌نهایت سپاسگزاریم!", 
                                reply_markup=self.build_reply_keyboard(["شروع", "خروج", "کلاس"]))
                self.user_states[user_id] = "DONE"
                return True
        
        elif text == "/start" or text == "شروع":
            self.user_states[user_id] = "START"
            self.send_message(chat_id, "🎓 به ربات خوش اومدی! لطفاً یکی از گزینه‌ها رو انتخاب کن:", 
                            reply_markup=self.build_reply_keyboard(["شروع", "خروج", "کلاس"]))
            return True
        
        elif text == "خروج":
            self.user_states[user_id] = "START"
            self.send_message(chat_id, "👋 خداحافظ! هر وقت خواستی برگرد.", 
                            reply_markup={"remove_keyboard": True})
            return True
        
        elif text == "کلاس" or text == "برگشت به قبل":
            self.user_states[user_id] = "CHOOSE_CLASS"
            self.send_message(chat_id, "🎓 لطفاً یکی از کلاس‌ها رو انتخاب کن:", 
                            reply_markup=self.build_inline_keyboard([
                                {"text": "کلاس هزار تومانی", "callback_data": "کلاس هزار تومانی"},
                                {"text": "کلاس دو هزار تومانی", "callback_data": "کلاس دو هزار تومانی"}
                            ]), 
                            secondary_reply_markup=self.build_reply_keyboard(["برگشت به قبل"]))
            return True
        
        return False  # پیام پردازش نشد
    
    def handle_callback(self, callback):
        """مدیریت کال‌بک‌های دریافتی"""
        chat_id = callback["message"]["chat"]["id"]
        user_id = callback["from"]["id"]
        callback_data = callback["data"]
        state = self.user_states.get(user_id, "START")
        
        if state == "CHOOSE_CLASS" and callback_data in self.class_prices:
            self.user_states[user_id] = "PAY"
            self.user_states[f"payment_class_{user_id}"] = callback_data
            if self.send_invoice(chat_id, self.class_prices[callback_data], callback_data):
                self.user_states[user_id] = "AWAITING_PAYMENT"
                return True
            else:
                self.send_message(chat_id, "❌ خطا در ارسال صورتحساب. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.", 
                                reply_markup=self.build_reply_keyboard(["برگشت به قبل"]))
                return True
        
        return False  # کال‌بک پردازش نشد
    
    def handle_pre_checkout_query(self, pre_checkout_query):
        """مدیریت پیش‌پرداخت"""
        pre_checkout_query_id = pre_checkout_query["id"]
        user_id = pre_checkout_query["from"]["id"]
        logging.info(f"دریافت PreCheckoutQuery: {json.dumps(pre_checkout_query, indent=2, ensure_ascii=False)}")
        self.answer_pre_checkout_query(pre_checkout_query_id, ok=True)
        self.user_states[user_id] = "PAYMENT_CONFIRMED"
        return True