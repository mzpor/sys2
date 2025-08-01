#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test for cost normalization functionality
"""

from kargah_module import KargahModule

def test_cost_normalization():
    """تست نرمال‌سازی هزینه"""
    print("🧪 Testing Cost Normalization")
    print("=" * 40)
    
    kargah = KargahModule()
    
    # Test cases
    test_cases = [
        ("۱۰۰۰۰", "10000 تومان"),
        ("10000", "10000 تومان"),
        ("۵۰۰,۰۰۰ تومان", "500,000 تومان"),
        ("500,000 تومان", "500,000 تومان"),
        ("۷۵۰۰۰۰", "750000 تومان"),
        ("750000", "750000 تومان"),
        ("۱,۰۰۰,۰۰۰ تومان", "1,000,000 تومان"),
        ("1,000,000 تومان", "1,000,000 تومان"),
    ]
    
    for input_text, expected in test_cases:
        result = kargah._normalize_cost_text(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: '{input_text}' -> Output: '{result}' (Expected: '{expected}')")
    
    print("\n✅ Cost normalization test completed!")

if __name__ == "__main__":
    test_cost_normalization() 