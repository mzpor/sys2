#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive test for KargahModule - simulating real bot interactions
"""

import json
from kargah_module import KargahModule

def simulate_message(kargah, user_id, text):
    """شبیه‌سازی پیام کاربر"""
    message = {
        "chat": {"id": 123456789},
        "from": {"id": user_id},
        "text": text
    }
    kargah.handle_message(message)

def simulate_callback(kargah, user_id, data):
    """شبیه‌سازی callback"""
    callback = {
        "message": {"chat": {"id": 123456789}, "message_id": 1},
        "from": {"id": user_id},
        "data": data,
        "id": "test_callback_id"
    }
    kargah.handle_callback(callback)

def test_interactive():
    """تست تعاملی ماژول کارگاه"""
    print("🧪 Interactive Test for KargahModule")
    print("=" * 50)
    
    # Initialize module
    kargah = KargahModule()
    test_user_id = 1114227010  # محمد ۱
    
    print(f"📋 Current workshops: {len(kargah.workshops)}")
    
    # Test 1: Command /kargah
    print("\n1️⃣ Testing /kargah command...")
    simulate_message(kargah, test_user_id, "/kargah")
    
    # Test 2: Add workshop flow
    print("\n2️⃣ Testing add workshop flow...")
    simulate_callback(kargah, test_user_id, "kargah_add")
    
    # Simulate user entering instructor name
    simulate_message(kargah, test_user_id, "آقای تست")
    
    # Simulate user entering cost
    simulate_message(kargah, test_user_id, "750,000 تومان")
    
    # Simulate user entering link
    simulate_message(kargah, test_user_id, "https://t.me/test_workshop")
    
    print(f"📋 Workshops after adding: {len(kargah.workshops)}")
    
    # Test 3: View workshop
    print("\n3️⃣ Testing view workshop...")
    simulate_callback(kargah, test_user_id, "kargah_view_05")
    
    # Test 4: Edit workshop
    print("\n4️⃣ Testing edit workshop...")
    simulate_callback(kargah, test_user_id, "kargah_edit_instructor_05")
    simulate_message(kargah, test_user_id, "آقای تست ویرایش شده")
    
    # Test 5: Delete workshop
    print("\n5️⃣ Testing delete workshop...")
    simulate_callback(kargah, test_user_id, "kargah_delete_05")
    
    print(f"📋 Final workshops: {len(kargah.workshops)}")
    
    print("\n✅ Interactive test completed!")

if __name__ == "__main__":
    test_interactive() 