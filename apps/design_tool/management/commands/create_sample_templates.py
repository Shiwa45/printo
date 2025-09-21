"""
Management command to create sample templates for testing
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.design_tool.models import DesignTemplate
from apps.products.models import ProductCategory
import json


class Command(BaseCommand):
    help = 'Create sample templates for testing front/back design functionality'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample templates...')
        
        try:
            # Get or create a category
            category, created = ProductCategory.objects.get_or_create(
                slug='business-cards',
                defaults={
                    'name': 'Business Cards',
                    'description': 'Professional business card templates'
                }
            )
            
            # Sample template data
            sample_templates = [
                {
                    'name': 'Professional Front Template',
                    'side': 'front',
                    'template_data': {
                        "version": "5.3.0",
                        "objects": [
                            {
                                "type": "rect",
                                "left": 50,
                                "top": 50,
                                "width": 200,
                                "height": 100,
                                "fill": "#3b82f6",
                                "stroke": "#1d4ed8",
                                "strokeWidth": 2
                            },
                            {
                                "type": "text",
                                "left": 150,
                                "top": 80,
                                "text": "Your Name",
                                "fontSize": 18,
                                "fontFamily": "Arial",
                                "fill": "#ffffff"
                            }
                        ],
                        "background": "#ffffff",
                        "width": 1050,
                        "height": 638
                    }
                },
                {
                    'name': 'Professional Back Template',
                    'side': 'back',
                    'template_data': {
                        "version": "5.3.0",
                        "objects": [
                            {
                                "type": "rect",
                                "left": 25,
                                "top": 25,
                                "width": 250,
                                "height": 150,
                                "fill": "#10b981",
                                "stroke": "#059669",
                                "strokeWidth": 2
                            },
                            {
                                "type": "text",
                                "left": 150,
                                "top": 80,
                                "text": "Contact Info",
                                "fontSize": 16,
                                "fontFamily": "Arial",
                                "fill": "#ffffff"
                            }
                        ],
                        "background": "#ffffff",
                        "width": 1050,
                        "height": 638
                    }
                },
                {
                    'name': 'Simple Single Template',
                    'side': 'single',
                    'template_data': {
                        "version": "5.3.0",
                        "objects": [
                            {
                                "type": "rect",
                                "left": 100,
                                "top": 100,
                                "width": 150,
                                "height": 80,
                                "fill": "#ef4444",
                                "stroke": "#dc2626",
                                "strokeWidth": 2
                            },
                            {
                                "type": "text",
                                "left": 175,
                                "top": 130,
                                "text": "Business Card",
                                "fontSize": 14,
                                "fontFamily": "Arial",
                                "fill": "#ffffff"
                            }
                        ],
                        "background": "#ffffff",
                        "width": 1050,
                        "height": 638
                    }
                }
            ]
            
            created_count = 0
            
            with transaction.atomic():
                for template_data in sample_templates:
                    template, created = DesignTemplate.objects.get_or_create(
                        name=template_data['name'],
                        category=category,
                        side=template_data['side'],
                        defaults={
                            'template_data': template_data['template_data'],
                            'width': 89.0,  # Business card width in mm
                            'height': 54.0,  # Business card height in mm
                            'dpi': 300,
                            'bleed_mm': 3.0,
                            'safe_area_mm': 5.0,
                            'status': 'active',
                            'product_types': ['business-cards'],
                            'tags': ['business', 'professional', 'sample'],
                            'description': f'Sample {template_data["side"]} template for testing'
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f'Created template: {template.name}')
                    else:
                        self.stdout.write(f'Template already exists: {template.name}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {created_count} sample templates'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample templates: {e}')
            )