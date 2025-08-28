
# apps/core/management/commands/create_templates.py
from django.core.management.base import BaseCommand
from apps.products.models import DesignTemplate, ProductCategory

class Command(BaseCommand):
    help = 'Create initial design templates'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating design templates...')
        
        # Business card templates
        business_card_templates = [
            {
                'name': 'Professional Business Card - Blue',
                'category': 'business-cards',
                'product_types': ['business-cards'],
                'width': 89,  # mm
                'height': 51,  # mm
                'template_data': {
                    'background': '#ffffff',
                    'elements': [
                        {
                            'type': 'text',
                            'content': 'Your Name',
                            'x': 10,
                            'y': 15,
                            'fontSize': 18,
                            'fontFamily': 'Arial',
                            'color': '#2563eb'
                        },
                        {
                            'type': 'text',
                            'content': 'Job Title',
                            'x': 10,
                            'y': 25,
                            'fontSize': 12,
                            'fontFamily': 'Arial',
                            'color': '#6b7280'
                        }
                    ]
                },
                'tags': ['professional', 'blue', 'minimal'],
                'is_featured': True
            },
            {
                'name': 'Creative Business Card - Orange',
                'category': 'business-cards',
                'product_types': ['business-cards'],
                'width': 89,
                'height': 51,
                'template_data': {
                    'background': '#f97316',
                    'elements': [
                        {
                            'type': 'text',
                            'content': 'Your Name',
                            'x': 10,
                            'y': 15,
                            'fontSize': 20,
                            'fontFamily': 'Arial Bold',
                            'color': '#ffffff'
                        }
                    ]
                },
                'tags': ['creative', 'orange', 'bold']
            }
        ]
        
        for template_data in business_card_templates:
            template, created = DesignTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'category': template_data['category'],
                    'product_types': template_data['product_types'],
                    'template_data': template_data['template_data'],
                    'width': template_data['width'],
                    'height': template_data['height'],
                    'tags': template_data['tags'],
                    'is_featured': template_data.get('is_featured', False)
                }
            )
            if created:
                self.stdout.write(f'Created template: {template.name}')
        
        self.stdout.write(self.style.SUCCESS('Design templates created!'))
