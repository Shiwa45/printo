#!/usr/bin/env python
"""Test script for the pricing calculator"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drishthi_printing.settings')
django.setup()

from apps.products.models import PricingCalculator
from decimal import Decimal

def test_book_pricing():
    print("=== Testing Book Pricing Calculator ===")
    
    # Test 1: Basic A4 book pricing
    print("\n1. Testing A4 Book (100 pages, 50 quantity, B&W Standard, 75gsm, Paperback)")
    result = PricingCalculator.calculate_book_price(
        size='A4',
        paper_type='75gsm',
        print_type='bw_standard',
        pages=100,
        quantity=50,
        binding_type='paperback_perfect'
    )
    
    if result['errors']:
        print("ERRORS:", result['errors'])
    else:
        print("SUCCESS: Calculation successful!")
        print(f"   Subtotal: Rs.{result['subtotal']}")
        print(f"   Discount: Rs.{result['discount']}")
        print(f"   Total: Rs.{result['total']}")
        print(f"   Per Book: Rs.{result['per_book']}")
        print("   Breakdown:")
        for item in result['breakdown']:
            print(f"     - {item['item']}: Rs.{item['cost']}")
    
    # Test 2: Color printing with design services
    print("\n2. Testing A4 Book (200 pages, 100 quantity, Color Premium, 130gsm Art, Hardcover + Design)")
    result = PricingCalculator.calculate_book_price(
        size='A4',
        paper_type='130gsm_art',
        print_type='color_premium',
        pages=200,
        quantity=100,
        binding_type='hardcover',
        include_cover_design=True,
        include_isbn=True,
        include_design_support=True
    )
    
    if result['errors']:
        print("ERRORS:", result['errors'])
    else:
        print("SUCCESS: Calculation successful!")
        print(f"   Subtotal: Rs.{result['subtotal']}")
        print(f"   Discount: Rs.{result['discount']}")
        print(f"   Total: Rs.{result['total']}")
        print(f"   Per Book: Rs.{result['per_book']}")
        print("   Breakdown:")
        for item in result['breakdown']:
            print(f"     - {item['item']}: Rs.{item['cost']}")
    
    # Test 3: A5 size book
    print("\n3. Testing A5 Book (80 pages, 25 quantity, B&W Premium, 100gsm, Spiral)")
    result = PricingCalculator.calculate_book_price(
        size='A5',
        paper_type='100gsm',
        print_type='bw_premium',
        pages=80,
        quantity=25,
        binding_type='spiral_binding'
    )
    
    if result['errors']:
        print("❌ Errors:", result['errors'])
    else:
        print("✅ Calculation successful!")
        print(f"   Subtotal: ₹{result['subtotal']}")
        print(f"   Discount: ₹{result['discount']}")
        print(f"   Total: ₹{result['total']}")
        print(f"   Per Book: ₹{result['per_book']}")

def test_quantity_discounts():
    print("\n=== Testing Quantity Discounts ===")
    
    quantities = [20, 25, 50, 100, 150, 250, 300]
    for qty in quantities:
        discount_info = PricingCalculator.get_quantity_discount(qty)
        print(f"Quantity {qty}: {discount_info['label']} ({discount_info['percentage']*100:.0f}%)")

def test_error_handling():
    print("\n=== Testing Error Handling ===")
    
    # Test invalid size
    print("\n1. Testing invalid size")
    result = PricingCalculator.calculate_book_price(size='INVALID')
    print("EXPECTED ERROR:", result['errors'])
    
    # Test invalid paper type
    print("\n2. Testing invalid paper type") 
    result = PricingCalculator.calculate_book_price(paper_type='invalid_gsm')
    print("EXPECTED ERROR:", result['errors'])
    
    # Test page limits
    print("\n3. Testing page limits (5 pages with paperback)")
    result = PricingCalculator.calculate_book_price(pages=5, binding_type='paperback_perfect')
    print("EXPECTED ERROR:", result['errors'])

if __name__ == "__main__":
    test_book_pricing()
    test_quantity_discounts()
    test_error_handling()
    
    print("\n=== Pricing Calculator Tests Complete ===")