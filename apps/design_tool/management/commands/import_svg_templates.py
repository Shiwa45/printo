# apps/design_tool/management/commands/import_svg_templates.py
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.design_tool.models import DesignTemplate
from apps.products.models import ProductCategory
import os
import xml.etree.ElementTree as ET

class Command(BaseCommand):
    help = 'Import SVG templates from a directory'

    def add_arguments(self, parser):
        parser.add_argument('--directory', type=str, help='Directory containing SVG files')
        parser.add_argument('--category', type=str, help='Category slug to assign templates to')

    def handle(self, *args, **options):
        directory = options['directory']
        category_slug = options['category']
        
        if not directory or not os.path.exists(directory):
            self.stdout.write(self.style.ERROR('Invalid directory path'))
            return
        
        try:
            category = ProductCategory.objects.get(slug=category_slug)
        except ProductCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Category {category_slug} not found'))
            return
        
        svg_files = [f for f in os.listdir(directory) if f.endswith('.svg')]
        created_count = 0
        
        for filename in svg_files:
            filepath = os.path.join(directory, filename)
            name = filename.replace('.svg', '').replace('_', ' ').replace('-', ' ').title()
            
            # Check if template already exists
            if DesignTemplate.objects.filter(name=name, category=category).exists():
                self.stdout.write(f'Skipping {name} - already exists')
                continue
            
            try:
                # Parse SVG to get dimensions
                tree = ET.parse(filepath)
                root = tree.getroot()
                
                # Extract dimensions (default to business card size if not found)
                width = self.extract_dimension(root.get('width', '89mm'))
                height = self.extract_dimension(root.get('height', '54mm'))
                
                # Create template
                with open(filepath, 'rb') as svg_file:
                    template = DesignTemplate.objects.create(
                        name=name,
                        category=category,
                        width=width,
                        height=height,
                        product_types=[category.slug]
                    )
                    
                    template.template_file.save(
                        filename,
                        ContentFile(svg_file.read()),
                        save=True
                    )
                    
                created_count += 1
                self.stdout.write(f'Created template: {name}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {filename}: {str(e)}'))
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} templates')
        )
    
    def extract_dimension(self, dimension_str):
        """Extract numeric value from dimension string (e.g., '89mm' -> 89)"""
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', str(dimension_str))
        return float(match.group(1)) if match else 89.0
