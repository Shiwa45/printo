#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drishthi_printing.settings')
django.setup()

from django.db import connection
from apps.design_tool.models import DesignTemplate, UserDesign
from apps.products.models import ProductCategory, Product

def inspect_database():
    print("Inspecting database for UUID issues...")
    
    with connection.cursor() as cursor:
        # Check design_tool tables
        try:
            cursor.execute("SELECT id FROM design_tool_designtemplate LIMIT 5")
            rows = cursor.fetchall()
            print(f"DesignTemplate table has {len(rows)} sample rows")
            for row in rows:
                print(f"  ID: {row[0]} (length: {len(str(row[0]))})")
        except Exception as e:
            print(f"DesignTemplate error: {e}")
        
        try:
            cursor.execute("SELECT id FROM design_tool_userdesign LIMIT 5")
            rows = cursor.fetchall()
            print(f"UserDesign table has {len(rows)} sample rows")
            for row in rows:
                print(f"  ID: {row[0]} (length: {len(str(row[0]))})")
        except Exception as e:
            print(f"UserDesign error: {e}")
        
        # Check products tables that might have UUID issues
        try:
            cursor.execute("SELECT id FROM products_productcategory LIMIT 5")
            rows = cursor.fetchall()
            print(f"ProductCategory table has {len(rows)} sample rows")
            for row in rows:
                print(f"  ID: {row[0]} (length: {len(str(row[0]))})")
        except Exception as e:
            print(f"ProductCategory error: {e}")
        
        # List all tables
        print("\nAll tables in database:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  {table[0]}")

if __name__ == '__main__':
    inspect_database()