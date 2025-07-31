 """
تمرین 29: یکپارچه‌سازی یادگیری ماشین
سطح: پیشرفته
هدف: آشنایی با یادگیری ماشین در ربات
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import re

class MLBot:
    """ربات با قابلیت یادگیری ماشین"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        self.classifier = MultinomialNB()
        self.intent_classifier = None
        self.sentiment_analyzer = None
        self.user_behavior_model = None
        self.training_data = []
        self.is_trained = False
    
    def prepare_training_data(self):
        """آماده‌سازی داده‌های آموزشی"""
        # داده‌های نمونه برای تشخیص قصد کاربر
        intent_data = [
            ("سلام", "greeting"),
            ("درود", "greeting"),
            ("خداحافظ", "farewell"),
            ("بای", "farewell"),
            ("ثبت نام", "registration"),
            ("می‌خوام ثبت نام کنم", "registration"),
            ("کلاس‌ها", "class_info"),
            ("لیست کلاس‌ها", "class_info"),
            ("قیمت", "price_info"),
            ("هزینه کلاس", "price_info"),
            ("پرداخت", "payment"),
            ("لینک پرداخت", "payment"),
            ("راهنما", "help"),
            ("کمک", "help"),
            ("مشکل", "support"),
            ("خطا", "support"),
            ("نظر", "feedback"),
            ("بازخورد", "feedback"),
            ("تمرین", "exercise"),
            ("تمرین تلاوت", "exercise"),
            ("امتیاز", "score"),
            ("نمره", "score"),
            ("حساب کاربری", "account"),
            ("پروفایل", "account")
        ]
        
        # داده‌های نمونه برای تحلیل احساسات
        sentiment_data = [
            ("عالی بود", "positive"),
            ("خیلی خوب", "positive"),
            ("ممنون", "positive"),
            ("متشکرم", "positive"),
            ("بد بود", "negative"),
            ("خوب نبود", "negative"),
            ("مشکل دارم", "negative"),
            ("راضی نیستم", "negative"),
            ("متوسط", "neutral"),
            ("خوب", "neutral"),
            ("قابل قبول", "neutral")
        ]
        
        self.training_data = {
            'intent': intent_data,
            'sentiment': sentiment_data
        }
    
    def train_intent_classifier(self):
        """آموزش مدل تشخیص قصد"""
        if not self.training_data:
            self.prepare_training_data()
        
        texts, labels = zip(*self.training_data['intent'])
        
        # تبدیل متن به بردار
        X = self.vectorizer.fit_transform(texts)
        
        # تقسیم داده‌ها
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42
        )
        
        # آموزش مدل
        self.intent_classifier = MultinomialNB()
        self.intent_classifier.fit(X_train, y_train)
        
        # ارزیابی مدل
        y_pred = self.intent_classifier.predict(X_test)
        accuracy = self.intent_classifier.score(X_test, y_test)
        
        print(f"✅ مدل تشخیص قصد آموزش داده شد - دقت: {accuracy:.2f}")
        
        return accuracy
    
    def predict_intent(self, text: str) -> str:
        """پیش‌بینی قصد کاربر"""
        if not self.intent_classifier:
            return "unknown"
        
        # پیش‌پردازش متن
        processed_text = self.preprocess_text(text)
        
        # تبدیل به بردار
        X = self.vectorizer.transform([processed_text])
        
        # پیش‌بینی
        intent = self.intent_classifier.predict(X)[0]
        confidence = np.max(self.intent_classifier.predict_proba(X))
        
        return intent if confidence > 0.3 else "unknown"
    
    def train_sentiment_analyzer(self):
        """آموزش تحلیل‌گر احساسات"""
        if not self.training_data:
            self.prepare_training_data()
        
        texts, labels = zip(*self.training_data['sentiment'])
        
        # تبدیل متن به بردار
        X = self.vectorizer.fit_transform(texts)
        
        # تقسیم داده‌ها
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42
        )
        
        # آموزش مدل
        self.sentiment_analyzer = MultinomialNB()
        self.sentiment_analyzer.fit(X_train, y_train)
        
        # ارزیابی مدل
        accuracy = self.sentiment_analyzer.score(X_test, y_test)
        
        print(f"✅ تحلیل‌گر احساسات آموزش داده شد - دقت: {accuracy:.2f}")
        
        return accuracy
    
    def analyze_sentiment(self, text: str) -> str:
        """تحلیل احساسات متن"""
        if not self.sentiment_analyzer:
            return "neutral"
        
        # پیش‌پردازش متن
        processed_text = self.preprocess_text(text)
        
        # تبدیل به بردار
        X = self.vectorizer.transform([processed_text])
        
        # پیش‌بینی
        sentiment = self.sentiment_analyzer.predict(X)[0]
        confidence = np.max(self.sentiment_analyzer.predict_proba(X))
        
        return sentiment if confidence > 0.4 else "neutral"
    
    def preprocess_text(self, text: str) -> str:
        """پیش‌پردازش متن"""
        # حذف کاراکترهای خاص
        text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z\s]', '', text)
        
        # حذف فاصله‌های اضافی
        text = ' '.join(text.split())
        
        return text.lower()
    
    def build_user_behavior_model(self):
        """ساخت مدل رفتار کاربر"""
        if not registered_users:
            print("⚠️ داده‌های کاربری برای ساخت مدل کافی نیست")
            return
        
        # استخراج ویژگی‌های کاربر
        user_features = []
        user_labels = []
        
        for user_id, user_data in registered_users.items():
            features = [
                len(user_data.get('first_name', '')),
                len(user_data.get('last_name', '')),
                len(user_data.get('mobile', '')),
                user_data.get('registration_date', 0),
                1 if user_data.get('registered_class') else 0
            ]
            
            # برچسب بر اساس فعالیت
            activity_score = user_data.get('activity_score', 0)
            if activity_score > 10:
                label = 'high_activity'
            elif activity_score > 5:
                label = 'medium_activity'
            else:
                label = 'low_activity'
            
            user_features.append(features)
            user_labels.append(label)
        
        if len(user_features) < 10:
            print("⚠️ داده‌های کافی برای آموزش مدل رفتار کاربر وجود ندارد")
            return
        
        # تبدیل به آرایه numpy
        X = np.array(user_features)
        y = np.array(user_labels)
        
        # تقسیم داده‌ها
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # آموزش مدل
        self.user_behavior_model = MultinomialNB()
        self.user_behavior_model.fit(X_train, y_train)
        
        # ارزیابی
        accuracy = self.user_behavior_model.score(X_test, y_test)
        print(f"✅ مدل رفتار کاربر آموزش داده شد - دقت: {accuracy:.2f}")
    
    def predict_user_behavior(self, user_id: int) -> str:
        """پیش‌بینی رفتار کاربر"""
        if not self.user_behavior_model or user_id not in registered_users:
            return "unknown"
        
        user_data = registered_users[user_id]
        
        features = [
            len(user_data.get('first_name', '')),
            len(user_data.get('last_name', '')),
            len(user_data.get('mobile', '')),
            user_data.get('registration_date', 0),
            1 if user_data.get('registered_class') else 0
        ]
        
        X = np.array([features])
        prediction = self.user_behavior_model.predict(X)[0]
        
        return prediction
    
    def save_models(self, filename: str = "ml_models.pkl"):
        """ذخیره مدل‌ها"""
        models = {
            'intent_classifier': self.intent_classifier,
            'sentiment_analyzer': self.sentiment_analyzer,
            'user_behavior_model': self.user_behavior_model,
            'vectorizer': self.vectorizer
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(models, f)
        
        print(f"💾 مدل‌ها در {filename} ذخیره شدند")
    
    def load_models(self, filename: str = "ml_models.pkl"):
        """بارگذاری مدل‌ها"""
        try:
            with open(filename, 'rb') as f:
                models = pickle.load(f)
            
            self.intent_classifier = models.get('intent_classifier')
            self.sentiment_analyzer = models.get('sentiment_analyzer')
            self.user_behavior_model = models.get('user_behavior_model')
            self.vectorizer = models.get('vectorizer')
            
            print(f"📂 مدل‌ها از {filename} بارگذاری شدند")
            return True
        
        except FileNotFoundError:
            print(f"❌ فایل {filename} یافت نشد")
            return False
        except Exception as e:
            print(f"❌ خطا در بارگذاری مدل‌ها: {e}")
            return False

class SmartBot:
    """ربات هوشمند با قابلیت‌های ML"""
    
    def __init__(self):
        self.ml_bot = MLBot()
        self.conversation_history = {}
        self.user_preferences = {}
    
    def process_smart_message(self, message: dict):
        """پردازش هوشمند پیام"""
        if 'message' not in message:
            return
        
        chat_id = message['message']['chat']['id']
        user_id = message['message']['from']['id']
        text = message['message'].get('text', '')
        
        # تحلیل قصد
        intent = self.ml_bot.predict_intent(text)
        
        # تحلیل احساسات
        sentiment = self.ml_bot.analyze_sentiment(text)
        
        # ذخیره تاریخچه
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'text': text,
            'intent': intent,
            'sentiment': sentiment,
            'timestamp': time.time()
        })
        
        # پردازش بر اساس قصد
        response = self.handle_intent(chat_id, user_id, intent, sentiment, text)
        
        return response
    
    def handle_intent(self, chat_id: int, user_id: int, intent: str, sentiment: str, text: str):
        """مدیریت قصد کاربر"""
        if intent == "greeting":
            return self.handle_greeting(chat_id, user_id, sentiment)
        elif intent == "registration":
            return self.handle_registration(chat_id, user_id)
        elif intent == "class_info":
            return self.handle_class_info(chat_id, user_id)
        elif intent == "payment":
            return self.handle_payment(chat_id, user_id)
        elif intent == "help":
            return self.handle_help(chat_id, user_id)
        elif intent == "feedback":
            return self.handle_feedback(chat_id, user_id, sentiment, text)
        else:
            return self.handle_unknown_intent(chat_id, user_id, text)
    
    def handle_greeting(self, chat_id: int, user_id: int, sentiment: str):
        """مدیریت سلام"""
        if sentiment == "positive":
            response = "سلام! خوشحالم که شما را می‌بینم! 😊"
        else:
            response = "سلام! چطور می‌تونم کمکتون کنم؟"
        
        send_message(chat_id, response)
    
    def handle_registration(self, chat_id: int, user_id: int):
        """مدیریت ثبت‌نام"""
        if user_id in registered_users:
            response = "شما قبلاً ثبت‌نام کرده‌اید. آیا می‌خواهید کلاس جدیدی اضافه کنید؟"
        else:
            response = "بله! برای ثبت‌نام لطفاً نام و نام خانوادگی خود را وارد کنید:"
            start_registration(chat_id, user_id)
        
        send_message(chat_id, response)
    
    def handle_class_info(self, chat_id: int, user_id: int):
        """مدیریت اطلاعات کلاس"""
        show_classes(chat_id, user_id)
    
    def handle_payment(self, chat_id: int, user_id: int):
        """مدیریت پرداخت"""
        if user_id in registered_users and registered_users[user_id].get('selected_class'):
            class_id = registered_users[user_id]['selected_class']
            show_payment_link(chat_id, user_id, class_id)
        else:
            response = "ابتدا باید کلاس را انتخاب کنید."
            send_message(chat_id, response)
    
    def handle_help(self, chat_id: int, user_id: int):
        """مدیریت راهنما"""
        help_text = """
🤖 راهنمای ربات:

📚 ثبت نام - برای ثبت‌نام در کلاس‌ها
📖 کلاس‌ها - مشاهده لیست کلاس‌ها
💳 پرداخت - انجام پرداخت
❓ راهنما - نمایش این راهنما
        """
        send_message(chat_id, help_text)
    
    def handle_feedback(self, chat_id: int, user_id: int, sentiment: str, text: str):
        """مدیریت بازخورد"""
        if sentiment == "positive":
            response = "ممنون از بازخورد مثبت شما! 😊"
        elif sentiment == "negative":
            response = "متأسفم که تجربه خوبی نداشته‌اید. لطفاً مشکل را توضیح دهید تا بررسی کنم."
        else:
            response = "ممنون از بازخورد شما! نظرات شما برای بهبود ربات مهم است."
        
        send_message(chat_id, response)
    
    def handle_unknown_intent(self, chat_id: int, user_id: int, text: str):
        """مدیریت قصد نامشخص"""
        response = f"متأسفم، منظور شما را متوجه نشدم. لطفاً از دستورات موجود استفاده کنید یا /help را ارسال کنید."
        send_message(chat_id, response)
    
    def get_user_insights(self, user_id: int) -> dict:
        """دریافت بینش کاربر"""
        if user_id not in self.conversation_history:
            return {}
        
        history = self.conversation_history[user_id]
        
        insights = {
            'total_messages': len(history),
            'common_intents': {},
            'sentiment_distribution': {},
            'last_activity': max([msg['timestamp'] for msg in history]) if history else 0
        }
        
        # تحلیل قصدهای رایج
        for msg in history:
            intent = msg['intent']
            insights['common_intents'][intent] = insights['common_intents'].get(intent, 0) + 1
        
        # تحلیل توزیع احساسات
        for msg in history:
            sentiment = msg['sentiment']
            insights['sentiment_distribution'][sentiment] = insights['sentiment_distribution'].get(sentiment, 0) + 1
        
        return insights

# ایجاد نمونه ربات هوشمند
smart_bot = SmartBot()

def train_ml_models():
    """آموزش مدل‌های ML"""
    print("🤖 شروع آموزش مدل‌های یادگیری ماشین...")
    
    # آموزش مدل تشخیص قصد
    intent_accuracy = smart_bot.ml_bot.train_intent_classifier()
    
    # آموزش تحلیل‌گر احساسات
    sentiment_accuracy = smart_bot.ml_bot.train_sentiment_analyzer()
    
    # ساخت مدل رفتار کاربر
    smart_bot.ml_bot.build_user_behavior_model()
    
    # ذخیره مدل‌ها
    smart_bot.ml_bot.save_models()
    
    print(f"✅ آموزش مدل‌ها تکمیل شد:")
    print(f"   - تشخیص قصد: {intent_accuracy:.2f}")
    print(f"   - تحلیل احساسات: {sentiment_accuracy:.2f}")

print("✅ تمرین 29: یکپارچه‌سازی یادگیری ماشین تکمیل شد!")

# آموزش مدل‌ها
train_ml_models()

# تمرین: تابعی برای تشخیص زبان کاربر بنویسید
# تمرین: تابعی برای پیشنهاد کلاس بر اساس علاقه بنویسید
# تمرین: تابعی برای تشخیص کلاهبرداری بنویسید