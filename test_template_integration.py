#!/usr/bin/env python
"""
Test script for Pixabay Template Integration
"""
import requests
import json

def test_template_search_api():
    """Test the template search API endpoint"""
    print("=== Testing Pixabay Template Search API ===\n")
    
    test_queries = [
        {"q": "business card", "template_type": "vector"},
        {"q": "flyer", "category": "business"},
        {"q": "poster", "template_type": "illustration"},
        {"q": "", "category": "backgrounds"}  # Default search
    ]
    
    base_url = "http://localhost:8000/design-tool/api/search/pixabay-templates/"
    
    for i, params in enumerate(test_queries, 1):
        print(f"Test {i}: {params}")
        try:
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    hits = data['data']['hits']
                    print(f"  [SUCCESS] Found {len(hits)} templates")
                    if hits:
                        first_template = hits[0]
                        print(f"  First template: {first_template.get('tags', 'No tags')}")
                        print(f"  Aspect ratio: {first_template.get('aspectRatio', 'Unknown')}")
                        print(f"  Is Vector: {first_template.get('isVector', False)}")
                else:
                    print(f"  [ERROR] API returned: {data.get('message', 'Unknown error')}")
            else:
                print(f"  [ERROR] HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"  [ERROR] Request failed: {e}")
        
        print()

def test_template_categories():
    """Test different template categories"""
    print("=== Testing Template Categories ===\n")
    
    categories = ['backgrounds', 'business', 'computer', 'education', 'graphics']
    base_url = "http://localhost:8000/design-tool/api/search/pixabay-templates/"
    
    for category in categories:
        print(f"Testing category: {category}")
        try:
            params = {"category": category, "per_page": 3}
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    hits = data['data']['hits']
                    print(f"  [SUCCESS] Found {len(hits)} templates in {category}")
                else:
                    print(f"  [ERROR] {data.get('message', 'Unknown error')}")
            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  [ERROR] {e}")
        
        print()

def test_template_types():
    """Test different template types"""
    print("=== Testing Template Types ===\n")
    
    types = ['vector', 'illustration', 'all']
    base_url = "http://localhost:8000/design-tool/api/search/pixabay-templates/"
    
    for template_type in types:
        print(f"Testing type: {template_type}")
        try:
            params = {"q": "design", "template_type": template_type, "per_page": 3}
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    hits = data['data']['hits']
                    print(f"  [SUCCESS] Found {len(hits)} templates of type {template_type}")
                    vector_count = sum(1 for hit in hits if hit.get('isVector'))
                    print(f"  Vector templates: {vector_count}/{len(hits)}")
                else:
                    print(f"  [ERROR] {data.get('message', 'Unknown error')}")
            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  [ERROR] {e}")
        
        print()

if __name__ == "__main__":
    print("Pixabay Template Integration Test\n")
    
    test_template_search_api()
    test_template_categories() 
    test_template_types()
    
    print("[SUCCESS] Template integration tests completed!")
    print("\nNext steps:")
    print("1. Open your design editor in a browser")
    print("2. Look for the 'Design Templates' section in the sidebar")
    print("3. Try searching for templates like 'business card', 'flyer', etc.")
    print("4. Click on any template to use it as a background")