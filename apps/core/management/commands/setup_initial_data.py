# apps/core/management/commands/setup_initial_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import ProductCategory, Product

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup initial data for Drishthi Printing'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create superuser if doesn't exist
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@drishthiprinting.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))
        
        # Create main categories
        categories_data = [
            {
                'name': 'Book Printing',
                'slug': 'book-printing',
                'description': 'Professional book printing services',
                'sort_order': 1,
                'subcategories': [
                    ('Children\'s Book Printing', 'childrens-book-printing'),
                    ('Comic Book Printing', 'comic-book-printing'),
                    ('Coffee Table Book Printing', 'coffee-table-book-printing'),
                    ('Coloring Book Printing', 'coloring-book-printing'),
                    ('Art Book Printing', 'art-book-printing'),
                    ('Annual Reports Printing', 'annual-reports-printing'),
                    ('Year Book Printing', 'year-book-printing'),
                    ('On Demand Books Printing', 'on-demand-books-printing'),
                ]
            },
            {
                'name': 'Paper Box Printing',
                'slug': 'paper-box-printing',
                'description': 'Custom paper boxes for various industries',
                'sort_order': 2,
                'subcategories': [
                    ('Medical Paper Boxes', 'medical-paper-boxes'),
                    ('Cosmetic Paper Boxes', 'cosmetic-paper-boxes'),
                    ('Retail Paper Boxes', 'retail-paper-boxes'),
                    ('Folding Carton Boxes', 'folding-carton-boxes'),
                    ('Corrugated Boxes', 'corrugated-boxes'),
                    ('Kraft Boxes', 'kraft-boxes'),
                ]
            },
            {
                'name': 'Marketing Products',
                'slug': 'marketing-products',
                'description': 'Brochures, flyers, and promotional materials',
                'sort_order': 3,
                'subcategories': [
                    ('Brochures', 'brochures'),
                    ('Catalogue', 'catalogue'),
                    ('Poster', 'poster'),
                    ('Flyers', 'flyers'),
                    ('Dangler', 'dangler'),
                    ('Standees', 'standees'),
                    ('Pen Drives', 'pen-drives'),
                ]
            },
            {
                'name': 'Stationery Products',
                'slug': 'stationery-products',
                'description': 'Business cards, letterheads, and office stationery',
                'sort_order': 4,
                'subcategories': [
                    ('Business Cards', 'business-cards'),
                    ('Letter Head', 'letter-head'),
                    ('Envelopes', 'envelopes'),
                    ('Bill Book', 'bill-book'),
                    ('ID Cards', 'id-cards'),
                    ('Sticker', 'sticker'),
                    ('Document Printing', 'document-printing'),
                ]
            }
        ]
        
        for cat_data in categories_data:
            # Create main category
            main_cat, created = ProductCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'sort_order': cat_data['sort_order'],
                }
            )
            if created:
                self.stdout.write(f'Created category: {main_cat.name}')
            
            # Create subcategories
            for i, (sub_name, sub_slug) in enumerate(cat_data['subcategories'], 1):
                sub_cat, created = ProductCategory.objects.get_or_create(
                    slug=sub_slug,
                    defaults={
                        'name': sub_name,
                        'parent': main_cat,
                        'sort_order': i,
                    }
                )
                if created:
                    self.stdout.write(f'  Created subcategory: {sub_cat.name}')
        
        # Create bestselling products (matching your homepage)
        bestselling_products = [
            {
                'name': 'Book Printing',
                'slug': 'book-printing',
                'category_slug': 'book-printing',
                'product_type': 'book',
                'base_price': 299.00,
                'description': 'On Demand Digital Book Printing in India with premium paper quality and fast delivery options.',
                'short_description': 'Premium quality book printing with various binding options',
                'pricing_structure': {
                    'type': 'complex',
                    'calculator': 'book_printing',
                    'features': ['Premium Paper', 'Fast Delivery']
                },
                'bestseller': True,
                'featured': True
            },
            {
                'name': 'Paper Boxes',
                'slug': 'paper-boxes',
                'category_slug': 'paper-box-printing',
                'product_type': 'box',
                'base_price': 199.00,
                'description': 'Custom paper boxes for retail, medical, and cosmetic packaging with eco-friendly materials.',
                'short_description': 'Custom paper boxes for various industries',
                'pricing_structure': {
                    'type': 'quote_based',
                    'starting_price': 199,
                    'features': ['Custom Sizes', 'Eco-Friendly']
                },
                'bestseller': True,
                'featured': True
            },
            {
                'name': 'Marketing Materials',
                'slug': 'marketing-materials',
                'category_slug': 'marketing-products',
                'product_type': 'marketing',
                'base_price': 249.00,
                'description': 'Eye-catching brochures, flyers, and marketing materials for business promotion.',
                'short_description': 'Professional marketing and promotional materials',
                'pricing_structure': {
                    'type': 'standard',
                    'base_price': 249,
                    'features': ['High Impact', 'Quick Turnaround']
                },
                'bestseller': True,
                'featured': True,
                'design_tool_enabled': True
            },
            {
                'name': 'Stationery Products',
                'slug': 'stationery-products',
                'category_slug': 'stationery-products',
                'product_type': 'stationery',
                'base_price': 299.00,
                'description': 'Professional business cards, letterheads, and office stationery with premium finish options.',
                'short_description': 'Complete business stationery solutions',
                'pricing_structure': {
                    'type': 'standard',
                    'base_price': 299,
                    'features': ['Premium Finish', 'Multiple Options']
                },
                'bestseller': True,
                'featured': True,
                'design_tool_enabled': True
            }
        ]
        
        for product_data in bestselling_products:
            category = ProductCategory.objects.get(slug=product_data['category_slug'])
            product, created = Product.objects.get_or_create(
                slug=product_data['slug'],
                defaults={
                    'name': product_data['name'],
                    'category': category,
                    'product_type': product_data['product_type'],
                    'base_price': product_data['base_price'],
                    'description': product_data['description'],
                    'short_description': product_data['short_description'],
                    'pricing_structure': product_data['pricing_structure'],
                    'bestseller': product_data.get('bestseller', False),
                    'featured': product_data.get('featured', False),
                    'design_tool_enabled': product_data.get('design_tool_enabled', False),
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        # Create design tool products (for "No Design? No Problem" section)
        design_tool_products = [
            {
                'name': 'Business Card Printing',
                'slug': 'business-card-printing',
                'category_slug': 'business-cards',
                'base_price': 299.00,
                'description': 'Professional business cards with online design tool. 500+ templates available with premium paper options.',
                'features': ['500+ Templates', 'Premium Paper', 'Fast Delivery']
            },
            {
                'name': 'Letter Heads',
                'slug': 'letter-heads',
                'category_slug': 'letter-head',
                'base_price': 199.00,
                'description': 'Custom letterheads for your business correspondence with professional layouts and quality paper.',
                'features': ['Professional Design', 'Quality Paper', 'Quick Setup']
            },
            {
                'name': 'Bill Book',
                'slug': 'bill-book',
                'category_slug': 'bill-book',
                'base_price': 399.00,
                'description': 'Customizable bill books and invoice pads for your business transactions with duplicate copy options.',
                'features': ['Custom Format', 'Duplicate Copy', 'Bulk Orders']
            },
            {
                'name': 'Sticker',
                'slug': 'sticker',
                'category_slug': 'sticker',
                'base_price': 149.00,
                'description': 'Custom stickers in various shapes and sizes for branding and promotions with waterproof options.',
                'features': ['Any Shape', 'Waterproof', 'Vibrant Colors']
            },
            {
                'name': 'Brochure',
                'slug': 'brochures-design',
                'category_slug': 'brochures',
                'base_price': 599.00,
                'description': 'Professional brochures with fold options and premium paper quality for marketing campaigns.',
                'features': ['Multiple Folds', 'Glossy Finish', 'High Quality']
            },
            {
                'name': 'Flyer',
                'slug': 'flyer',
                'category_slug': 'flyers',
                'base_price': 249.00,
                'description': 'Eye-catching flyers for events, promotions, and marketing campaigns with quick printing options.',
                'features': ['Eye-Catching', 'Quick Print', 'Affordable']
            }
        ]
        
        for product_data in design_tool_products:
            try:
                category = ProductCategory.objects.get(slug=product_data['category_slug'])
                product, created = Product.objects.get_or_create(
                    slug=product_data['slug'],
                    defaults={
                        'name': product_data['name'],
                        'category': category,
                        'product_type': 'stationery',
                        'base_price': product_data['base_price'],
                        'description': product_data['description'],
                        'short_description': product_data['description'][:200],
                        'design_tool_enabled': True,
                        'featured': True,
                        'pricing_structure': {
                            'type': 'design_tool',
                            'base_price': product_data['base_price'],
                            'features': product_data['features']
                        }
                    }
                )
                if created:
                    self.stdout.write(f'Created design tool product: {product.name}')
            except ProductCategory.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Category {product_data["category_slug"]} not found for {product_data["name"]}')
                )
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed!'))
