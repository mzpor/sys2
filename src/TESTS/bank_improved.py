 import requests
import time
import json
import os
from datetime import datetime

BOT_TOKEN = "811316021:qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1"
WALLET_TOKEN = "WALLET-LIiCzxGZnCd58Obr"  # توکن کیف پول
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
WALLET_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
GROUP_LINK = "https://bale.ai/join/MadreseTalavatGroup"

# فایل ذخیره‌سازی داده‌ها
DATA_FILE = "payment_data.json"

CLASS_PRICES = {
    "کلاس پایه": 1000,  # قیمت به تومان
    "کلاس پیشرفته": 1000  # قیمت به تومان
}

user_states = {}
payment_records = {}  # ثبت پرداخت‌ها

def load_data():
    """بارگذاری داده‌ها از فایل"""
    global user_states, payment_records
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                user_states = data.get('user_states', {})
                payment_records = data.get('payment_records', {})
                print(f"✅ داده‌ها بارگذاری شد: {len(user_states)} کاربر")
    except Exception as e:
        print(f"❌ خطا در بارگذاری داده‌ها: {e}")

def save_data():
    """ذخیره داده‌ها در فایل"""
    try:
        data = {
            'user_states': user_states,
            'payment_records': payment_records,
            'last_save': datetime.now().isoformat()
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("💾 داده‌ها ذخیره شد")
    except Exception as e:
        print(f"❌ خطا در ذخیره داده‌ها: {e}")

def get_updates(offset=None):
    res = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset})
    return res.json()

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        response = requests.post(f"{BASE_URL}/sendMessage", json=payload)
        if response.status_code != 200:
            print(f"❌ خطا در ارسال پیام: {response.status_code}")
    except Exception as e:
        print(f"❌ خطا در ارسال پیام: {e}")

def build_keyboard(buttons):
    return {
        "keyboard": [[{"text": btn}] for btn in buttons],
        "resize_keyboard": True
    }

def create_payment_link(amount, description, user_id):
    """ایجاد لینک پرداخت واقعی"""
    try:
        payment_data = {
            "amount": amount,
            "description": description,
            "callback_url": f"https://tapi.bale.ai/bot{BOT_TOKEN}/payment_callback",
            "user_id": user_id,
            "currency": "IRR"  # ریال ایران
        }
        
        response = requests.post(
            f"{WALLET_URL}/createInvoice",
            json=payment_data,
            headers={"Authorization": f"Bearer {WALLET_TOKEN}"}
        )
        
        print(f"🔗 درخواست ایجاد لینک پرداخت: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            payment_url = result.get("payment_url")
            invoice_id = result.get("invoice_id")
            
            # ثبت اطلاعات پرداخت
            payment_records[invoice_id] = {
                'user_id': user_id,
                'amount': amount,
                'description': description,
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            save_data()
            
            return payment_url, invoice_id
        else:
            print(f"❌ خطا در ایجاد لینک پرداخت: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ خطا در ایجاد لینک پرداخت: {e}")
        return None, None

def check_payment_status(invoice_id):
    """بررسی وضعیت پرداخت"""
    try:
        response = requests.get(
            f"{WALLET_URL}/getInvoice",
            params={"invoice_id": invoice_id},
            headers={"Authorization": f"Bearer {WALLET_TOKEN}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status")
            
            # به‌روزرسانی وضعیت در ثبت‌ها
            if invoice_id in payment_records:
                payment_records[invoice_id]['status'] = status
                payment_records[invoice_id]['updated_at'] = datetime.now().isoformat()
                save_data()
            
            return status == "paid"
        else:
            print(f"❌ خطا در بررسی وضعیت پرداخت: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ خطا در بررسی وضعیت پرداخت: {e}")
        return False

def handle_payment_success(user_id, selected_class):
    """مدیریت موفقیت پرداخت"""
    send_message(user_id, "✅ پرداخت با موفقیت انجام شد!")
    send_message(user_id, "🌟 محمد می‌گه: «قدم گذاشتن در مسیر رشد از همین‌جا شروع می‌شه!»")
    send_message(user_id, f"📎 لینک ورود به گروه: {GROUP_LINK}")
    send_message(user_id, "🎉 از اینکه همراه شدید، بی‌نهایت سپاسگزاریم!")
    
    # ثبت موفقیت پرداخت
    payment_records[f"success_{user_id}_{datetime.now().timestamp()}"] = {
        'user_id': user_id,
        'class': selected_class,
        'status': 'completed',
        'completed_at': datetime.now().isoformat()
    }
    save_data()

def get_payment_stats():
    """دریافت آمار پرداخت‌ها"""
    total_payments = len(payment_records)
    completed_payments = len([p for p in payment_records.values() if p.get('status') == 'completed'])
    total_amount = sum([p.get('amount', 0) for p in payment_records.values() if p.get('status') == 'completed'])
    
    return {
        'total': total_payments,
        'completed': completed_payments,
        'total_amount': total_amount
    }

def main():
    offset = None
    print("🤖 ربات پرداخت فعال شد...")
    
    # بارگذاری داده‌های قبلی
    load_data()
    
    # نمایش آمار
    stats = get_payment_stats()
    print(f"📊 آمار پرداخت‌ها: {stats['completed']}/{stats['total']} - {stats['total_amount']:,} تومان")

    while True:
        try:
            updates = get_updates(offset)
            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    message = update.get("message")
                    if not message: continue

                    chat_id = message["chat"]["id"]
                    user_id = message["from"]["id"]
                    text = message.get("text", "")

                    state = user_states.get(user_id, "START")

                    if text == "/start":
                        user_states[user_id] = "CHOOSE_CLASS"
                        send_message(chat_id, "🎓 لطفاً یکی از کلاس‌ها را انتخاب کنید:", 
                                     reply_markup=build_keyboard(list(CLASS_PRICES.keys())))

                    elif state == "CHOOSE_CLASS" and text in CLASS_PRICES:
                        user_states[user_id] = "PAY"
                        user_states[f"class_{user_id}"] = text
                        price = CLASS_PRICES[text]
                        send_message(chat_id, f"✅ شما کلاس '{text}' با قیمت {price:,} تومان را انتخاب کردید.", 
                                     reply_markup=build_keyboard(["💳 پرداخت واقعی"]))

                    elif state == "PAY" and text == "💳 پرداخت واقعی":
                        selected_class = user_states.get(f"class_{user_id}", "نامشخص")
                        price = CLASS_PRICES[selected_class]
                        description = f"پرداخت برای {selected_class}"
                        
                        print(f"💰 درخواست پرداخت: {user_id} - {selected_class} - {price:,} تومان")
                        
                        # ایجاد لینک پرداخت واقعی
                        payment_url, invoice_id = create_payment_link(price, description, user_id)
                        
                        if payment_url and invoice_id:
                            user_states[f"invoice_{user_id}"] = invoice_id
                            user_states[user_id] = "WAITING_PAYMENT"
                            
                            keyboard = {
                                "inline_keyboard": [[
                                    {"text": "💳 پرداخت", "url": payment_url}
                                ]]
                            }
                            
                            send_message(chat_id, 
                                       f"💳 لینک پرداخت برای {selected_class}:\n\n"
                                       f"💰 مبلغ: {price:,} تومان\n"
                                       f"📝 توضیحات: {description}\n\n"
                                       f"لطفاً روی دکمه پرداخت کلیک کنید:",
                                       keyboard)
                        else:
                            send_message(chat_id, "❌ خطا در ایجاد لینک پرداخت. لطفاً دوباره تلاش کنید.")

                    elif state == "WAITING_PAYMENT":
                        # بررسی وضعیت پرداخت
                        invoice_id = user_states.get(f"invoice_{user_id}")
                        if invoice_id and check_payment_status(invoice_id):
                            selected_class = user_states.get(f"class_{user_id}", "نامشخص")
                            
                            print(f"✅ پرداخت موفق: {user_id} - {selected_class}")
                            handle_payment_success(user_id, selected_class)

                            user_states[user_id] = "DONE"
                            # پاک کردن اطلاعات پرداخت
                            if f"invoice_{user_id}" in user_states:
                                del user_states[f"invoice_{user_id}"]
                        else:
                            send_message(chat_id, "⏳ در انتظار پرداخت... لطفاً پرداخت را تکمیل کنید.")

                    elif text == "/stats" and user_id == 123456789:  # فقط برای ادمین
                        stats = get_payment_stats()
                        stats_msg = f"📊 آمار پرداخت‌ها:\n\n"
                        stats_msg += f"📈 کل درخواست‌ها: {stats['total']}\n"
                        stats_msg += f"✅ پرداخت‌های موفق: {stats['completed']}\n"
                        stats_msg += f"💰 کل مبلغ: {stats['total_amount']:,} تومان\n"
                        send_message(chat_id, stats_msg)

            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n🛑 ربات متوقف شد!")
            save_data()
            break
        except Exception as e:
            print(f"❌ خطای غیرمنتظره: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()