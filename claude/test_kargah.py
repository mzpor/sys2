#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for KargahModule
"""

import json
from kargah_module import KargahModule

def test_kargah_module():
    """Test the kargah module functionality"""
    print("🧪 Testing KargahModule...")
    
    # Initialize the module
    kargah = KargahModule()
    
    # Test loading workshops
    print(f"📋 Loaded {len(kargah.workshops)} workshops")
    for workshop_id, workshop in kargah.workshops.items():
        print(f"  - {workshop_id}: {workshop['instructor_name']} - {workshop['cost']}")
    
    # Test keyboard generation
    print("\n⌨️ Testing keyboard generation...")
    management_keyboard = kargah.get_workshop_management_keyboard()
    print(f"Management keyboard: {management_keyboard}")
    
    list_keyboard = kargah.get_workshop_list_keyboard()
    print(f"List keyboard: {list_keyboard}")
    
    # Test admin check
    print("\n👤 Testing admin check...")
    test_user_id = 1114227010  # محمد ۱ from config
    is_admin = kargah.is_user_admin(test_user_id)
    print(f"User {test_user_id} is admin: {is_admin}")
    
    # Test adding a new workshop
    print("\n➕ Testing workshop addition...")
    kargah.workshops["04"] = {
        "instructor_name": "آقای کاظمی",
        "cost": "600,000 تومان",
        "link": "https://t.me/workshop4"
    }
    kargah.save_workshops()
    print("✅ Workshop added and saved")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    test_kargah_module() 