#!/usr/bin/env python
"""
Test script for Pixabay API integration
"""
import os
import django
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drishthi_printing.settings')
django.setup()

from apps.design_tool.services.free_apis import ImageSearchService
import requests
from django.conf import settings

def test_direct_pixabay_api():
    """Test direct Pixabay API call"""
    print("Testing direct Pixabay API call...")
    
    try:
        url = "https://pixabay.com/api/"
        params = {
            'key': settings.PIXABAY_API_KEY,
            'q': 'flowers',
            'safesearch': 'true',
            'page': 1,
            'per_page': 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"[SUCCESS] Direct API call successful!")
        print(f"  Total images found: {data.get('totalHits', 0)}")
        print(f"  Images returned: {len(data.get('hits', []))}")
        
        if data.get('hits'):
            first_image = data['hits'][0]
            print(f"  First image: {first_image.get('tags', 'No tags')}")
            print(f"  Image URL: {first_image.get('webformatURL', 'No URL')}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Direct API call failed: {e}")
        return False

def test_image_search_service():
    """Test the ImageSearchService class"""
    print("\nTesting ImageSearchService...")
    
    try:
        service = ImageSearchService()
        results = service.search_single_source('pixabay', 'nature', 1, 5)
        
        print(f"[SUCCESS] ImageSearchService successful!")
        print(f"  Images returned: {len(results)}")
        
        if results:
            first_result = results[0]
            print(f"  First image title: {first_result.get('title', 'No title')}")
            print(f"  Source: {first_result.get('source', 'No source')}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] ImageSearchService failed: {e}")
        return False

def test_api_key_configuration():
    """Test if API key is properly configured"""
    print("\nTesting API key configuration...")
    
    try:
        api_key = getattr(settings, 'PIXABAY_API_KEY', '')
        
        if api_key and api_key != '':
            print(f"[SUCCESS] API key is configured")
            print(f"  Key length: {len(api_key)} characters")
            print(f"  Key preview: {api_key[:8]}...{api_key[-4:]}")
            return True
        else:
            print("[ERROR] API key is not configured or empty")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error checking API key: {e}")
        return False

if __name__ == "__main__":
    print("=== Pixabay API Integration Test ===\n")
    
    # Run tests
    test1 = test_api_key_configuration()
    test2 = test_direct_pixabay_api()
    test3 = test_image_search_service()
    
    print(f"\n=== Test Results ===")
    print(f"API Key Configuration: {'PASS' if test1 else 'FAIL'}")
    print(f"Direct API Call: {'PASS' if test2 else 'FAIL'}")
    print(f"ImageSearchService: {'PASS' if test3 else 'FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n[SUCCESS] All tests passed! Pixabay integration is working correctly.")
    else:
        print("\n[ERROR] Some tests failed. Check the errors above.")