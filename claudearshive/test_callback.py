# test_callback.py
from registration_module import RegistrationModule
import json

def test_callbacks():
    """تست callback های registration_module"""
    print("🧪 Testing Registration Callbacks...")
    
    # ایجاد نمونه ماژول
    registration_module = RegistrationModule()
    
    # تنظیم کاربر تست
    test_user_id = 2045777722
    test_user_str = str(test_user_id)
    
    # تنظیم داده‌های کاربر
    registration_module.user_data[test_user_str] = {
        "first_name": "محمد",
        "full_name": "محمد رایتل",
        "national_id": "0065847172",
        "phone": "989222507759"
    }
    
    # تست callback های مختلف
    test_callbacks = [
        "edit_name",
        "edit_national_id", 
        "edit_phone",
        "edit_info",
        "final_confirm",
        "quran_student_panel"
    ]
    
    for callback_data in test_callbacks:
        print(f"\n🔄 Testing callback: {callback_data}")
        
        test_callback = {
            "id": "test_id",
            "from": {"id": test_user_id},
            "message": {
                "chat": {"id": test_user_id},
                "message_id": 1
            },
            "data": callback_data
        }
        
        try:
            registration_module.handle_callback(test_callback)
            print(f"✅ Callback {callback_data} processed successfully")
        except Exception as e:
            print(f"❌ Error in callback {callback_data}: {e}")
    
    print("\n✅ Callback test completed!")

if __name__ == "__main__":
    test_callbacks() 