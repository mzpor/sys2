#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test for PaymentModule
"""

from payment_module import PaymentModule
from kargah_module import KargahModule

def test_payment_module():
    """تست ماژول پرداخت"""
    print("🧪 Testing PaymentModule")
    print("=" * 40)
    
    # Initialize modules
    kargah = KargahModule()
    payment = PaymentModule(kargah)
    
    print(f"📋 Available workshops: {len(kargah.workshops)}")
    
    # Test cost extraction
    print("\n💰 Testing cost extraction:")
    test_costs = [
        "500,000 تومان",
        "۱۰۰۰۰",
        "10000",
        "۷۵۰۰۰۰ تومان",
        "750000 تومان"
    ]
    
    for cost in test_costs:
        amount = payment._extract_amount_from_cost(cost)
        print(f"  {cost} -> {amount} ریال ({amount // 10} تومان)")
    
    # Test workshop payment simulation
    print("\n💳 Testing workshop payment simulation:")
    if kargah.workshops:
        workshop_id = list(kargah.workshops.keys())[0]
        workshop_data = kargah.workshops[workshop_id]
        
        print(f"  Workshop: {workshop_data.get('instructor_name', 'نامشخص')}")
        print(f"  Cost: {workshop_data.get('cost', 'نامشخص')}")
        
        # Simulate payment
        amount = payment._extract_amount_from_cost(workshop_data.get('cost', '0 تومان'))
        print(f"  Extracted amount: {amount} ریال ({amount // 10} تومان)")
    
    print("\n✅ Payment module test completed!")

if __name__ == "__main__":
    test_payment_module() 