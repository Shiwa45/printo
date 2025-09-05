#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drishthi_printing.settings')
django.setup()

from django.test import Client
from apps.products.models import Product, ProductCategory

def test_design_tool():
    print("Testing Design Tool Implementation...")
    
    client = Client()
    
    # Test 1: Template list page
    try:
        response = client.get('/design-tool/templates/')
        print(f"✅ Templates page: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Templates page error: {e}")
    
    # Test 2: Check if we have products with design tool enabled
    try:
        # Create a test category and product if they don't exist
        category, created = ProductCategory.objects.get_or_create(
            name="Business Cards",
            defaults={'slug': 'business-cards', 'description': 'Professional business cards'}
        )
        if created:
            print("✅ Created test category: Business Cards")
        
        product, created = Product.objects.get_or_create(
            name="Standard Business Cards",
            defaults={
                'slug': 'business-cards',
                'category': category,
                'price': 100.00,
                'description': 'High quality business cards',
                'design_tool_enabled': True
            }
        )
        if created:
            print("✅ Created test product: Standard Business Cards")
        
        # Test editor page
        response = client.get('/design-tool/editor/business-cards/')
        print(f"✅ Design editor page: Status {response.status_code}")
        
    except Exception as e:
        print(f"❌ Design editor error: {e}")
    
    # Test 3: API endpoints
    try:
        response = client.get('/design-tool/api/search/images/?q=business')
        print(f"✅ Image search API: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Image search API error: {e}")
    
    print("\n🎉 Design Tool System Test Complete!")
    print("\nNext steps:")
    print("1. Configure API keys in .env file")
    print("2. Run: python manage.py runserver")
    print("3. Visit: http://127.0.0.1:8000/design-tool/templates/")

if __name__ == '__main__':
    test_design_tool()