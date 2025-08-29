# apps/core/management/commands/update_product_structure.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import ProductCategory, Product, DesignTemplate
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Update product structure for enhanced service pages'
    
    def handle(self, *args, **options):
        self.stdout.write('Updating product structure...')
        
        # Clear existing data if needed
        if self.confirm_reset():
            Product.objects.all().delete()
            ProductCategory.objects.all().delete()
            DesignTemplate.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing product data'))
        
        # Create enhanced categories with proper structure
        self.create_enhanced_categories()
        
        # Create detailed products with pricing structures
        self.create_detailed_products()
        
        # Create design templates
        self.create_design_templates()
        
        self.stdout.write(self.style.SUCCESS('Product structure updated successfully!'))
    
    def confirm_reset(self):
        """Ask user confirmation to reset data"""
        response = input('Do you want to reset all product data? (yes/no): ')
        return response.lower() == 'yes'
    
    def create_enhanced_categories(self):
        """Create comprehensive category structure"""
        categories_data = [
            {
                'name': 'Book Printing',
                'slug': 'book-printing',
                'description': 'Professional book printing services for all types of publications',
                'icon': 'fas fa-book',
                'sort_order': 1,
                'subcategories': [
                    ('Children\'s Book Printing', 'childrens-book-printing', 'Colorful and safe books for children'),
                    ('Comic Book Printing', 'comic-book-printing', 'High-quality comic book printing'),
                    ('Coffee Table Book Printing', 'coffee-table-book-printing', 'Premium large format books'),
                    ('Coloring Book Printing', 'coloring-book-printing', 'Interactive coloring books'),
                    ('Art Book Printing', 'art-book-printing', 'Museum quality art publications'),
                    ('Annual Reports Printing', 'annual-reports-printing', 'Corporate annual reports'),
                    ('Year Book Printing', 'year-book-printing', 'School and college year books'),
                    ('On Demand Books Printing', 'on-demand-books-printing', 'Print-on-demand book services'),
                ]
            },
            {
                'name': 'Paper Box Printing',
                'slug': 'paper-box-printing',
                'description': 'Custom paper boxes for various industries and applications',
                'icon': 'fas fa-box',
                'sort_order': 2,
                'subcategories': [
                    ('Medical Paper Boxes', 'medical-paper-boxes', 'Pharmaceutical and medical packaging'),
                    ('Cosmetic Paper Boxes', 'cosmetic-paper-boxes', 'Beauty product packaging'),
                    ('Retail Paper Boxes', 'retail-paper-boxes', 'General retail packaging solutions'),
                    ('Folding Carton Boxes', 'folding-carton-boxes', 'Collapsible carton boxes'),
                    ('Corrugated Boxes', 'corrugated-boxes', 'Heavy-duty shipping boxes'),
                    ('Kraft Boxes', 'kraft-boxes', 'Eco-friendly kraft paper boxes'),
                ]
            },
            {
                'name': 'Marketing Products',
                'slug': 'marketing-products',
                'description': 'Promotional materials and marketing collateral',
                'icon': 'fas fa-bullhorn',
                'sort_order': 3,
                'subcategories': [
                    ('Brochures', 'brochures', 'Professional business brochures'),
                    ('Catalogues', 'catalogue', 'Product and service catalogues'),
                    ('Posters', 'poster', 'Large format promotional posters'),
                    ('Flyers', 'flyers', 'Marketing flyers and leaflets'),
                    ('Danglers', 'dangler', 'Hanging promotional materials'),
                    ('Standees', 'standees', 'Display stands and standees'),
                    ('Pen Drives', 'pen-drives', 'Custom branded USB drives'),
                ]
            },
            {
                'name': 'Stationery Products',
                'slug': 'stationery-products',
                'description': 'Business cards, letterheads, and office stationery',
                'icon': 'fas fa-pen',
                'sort_order': 4,
                'subcategories': [
                    ('Business Cards', 'business-cards', 'Professional business cards'),
                    ('Letter Head', 'letter-head', 'Corporate letterhead printing'),
                    ('Envelopes', 'envelopes', 'Custom printed envelopes'),
                    ('Bill Books', 'bill-book', 'Invoice and receipt books'),
                    ('ID Cards', 'id-cards', 'Employee and membership ID cards'),
                    ('Stickers', 'sticker', 'Custom stickers and labels'),
                    ('Document Printing', 'document-printing', 'General document printing'),
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
                    'icon': cat_data['icon'],
                    'sort_order': cat_data['sort_order'],
                }
            )
            if created:
                self.stdout.write(f'Created category: {main_cat.name}')
            
            # Create subcategories
            for i, (sub_name, sub_slug, sub_desc) in enumerate(cat_data['subcategories'], 1):
                sub_cat, created = ProductCategory.objects.get_or_create(
                    slug=sub_slug,
                    defaults={
                        'name': sub_name,
                        'parent': main_cat,
                        'description': sub_desc,
                        'sort_order': i,
                    }
                )
                if created:
                    self.stdout.write(f'  Created subcategory: {sub_cat.name}')
    
    def create_detailed_products(self):
        """Create products with comprehensive specifications"""
        
        # Book Printing Products
        book_products = [
            {
                'name': 'Children\'s Book Printing',
                'slug': 'childrens-book-printing',
                'category_slug': 'childrens-book-printing',
                'product_type': 'book',
                'base_price': Decimal('299.00'),
                'description': 'Premium children\'s book printing with child-safe inks, vibrant colors, and durable binding. Perfect for authors, publishers, and educators who want to create magical reading experiences for young minds.',
                'short_description': 'High-quality children\'s book printing with safe materials and vibrant colors',
                'size_options': ['A4 (210×297mm)', 'A5 (148×210mm)', 'Letter (216×279mm)', 'Custom Size'],
                'paper_options': ['70 GSM Maplitho', '80 GSM Maplitho', '100 GSM Art Paper', '130 GSM Art Paper'],
                'print_options': ['Black & White Standard', 'Black & White Premium', 'Color Standard', 'Color Premium'],
                'binding_options': ['Perfect Binding', 'Saddle Stitching', 'Hardcover', 'Spiral Binding'],
                'finish_options': ['Matte Lamination', 'Gloss Lamination', 'Spot UV'],
                'pricing_structure': {
                    'type': 'book_calculator',
                    'base_rates': {
                        'A4': {'bw_standard': 1.1, 'bw_premium': 1.3, 'color_standard': 2.5, 'color_premium': 2.7},
                        'A5': {'bw_standard': 0.6, 'bw_premium': 0.75, 'color_standard': 1.25, 'color_premium': 1.35}
                    },
                    'binding_costs': {'perfect': 40, 'saddle': 25, 'hardcover': 150, 'spiral': 40}
                },
                'featured': True,
                'bestseller': True,
                'min_quantity': 25,
                'lead_time_days': 5
            },
            {
                'name': 'Comic Book Printing',
                'slug': 'comic-book-printing', 
                'category_slug': 'comic-book-printing',
                'product_type': 'book',
                'base_price': Decimal('449.00'),
                'description': 'Professional comic book printing with high-resolution color printing, specialized comic paper, and binding options perfect for independent creators and publishers.',
                'short_description': 'Professional comic book printing with vibrant colors and crisp graphics',
                'size_options': ['US Comic (170×260mm)', 'Manga Size (128×182mm)', 'European (210×280mm)', 'Custom'],
                'paper_options': ['70 GSM Maplitho', '80 GSM Maplitho', '100 GSM Art Paper'],
                'print_options': ['Full Color CMYK', 'Spot Colors', 'Pantone Matching'],
                'binding_options': ['Saddle Stitch', 'Perfect Bound', 'Spiral Binding'],
                'finish_options': ['Matte', 'Gloss', 'Satin'],
                'pricing_structure': {
                    'type': 'book_calculator',
                    'specialty': 'comic',
                    'color_premium': True
                },
                'featured': True,
                'min_quantity': 25,
                'lead_time_days': 6
            },
            {
                'name': 'Coffee Table Book Printing',
                'slug': 'coffee-table-book-printing',
                'category_slug': 'coffee-table-book-printing',
                'product_type': 'book',
                'base_price': Decimal('1299.00'),
                'description': 'Premium coffee table books with exceptional print quality for photography, art, and showcase publications. Museum-quality printing with luxury finishes.',
                'short_description': 'Luxury coffee table books with museum-quality printing',
                'size_options': ['A4 Landscape', '25×25cm Square', '30×30cm Square', 'Custom Large Format'],
                'paper_options': ['150 GSM Art Paper', '200 GSM Art Paper', '250 GSM Art Paper', '300 GSM Art Paper'],
                'print_options': ['High-Resolution Color', 'Pantone Spot Colors', 'Metallic Inks'],
                'binding_options': ['Hardcover Case Bound', 'Premium Hardcover', 'Leather Bound'],
                'finish_options': ['Dust Jacket', 'Premium Lamination', 'Foil Stamping'],
                'pricing_structure': {
                    'type': 'book_calculator',
                    'specialty': 'coffee_table',
                    'premium_rates': True
                },
                'featured': True,
                'min_quantity': 10,
                'lead_time_days': 10
            }
        ]
        
        # Stationery Products  
        stationery_products = [
            {
                'name': 'Professional Business Cards',
                'slug': 'business-cards-premium',
                'category_slug': 'business-cards',
                'product_type': 'stationery',
                'base_price': Decimal('299.00'),
                'description': 'Premium business cards that make a lasting impression. Available in multiple paper weights, finishes, and sizes with professional design services.',
                'short_description': 'Premium business cards with multiple finish options',
                'size_options': ['Standard (90×54mm)', 'US Standard (89×51mm)', 'Square (54×54mm)', 'Custom'],
                'paper_options': ['300 GSM Art Card', '350 GSM Art Card', '400 GSM Textured'],
                'print_options': ['Single Side', 'Double Side', 'Variable Data Printing'],
                'binding_options': ['Standard Cut', 'Rounded Corners', 'Die Cut'],
                'finish_options': ['Matte Lamination', 'Gloss Lamination', 'Spot UV', 'Gold Foiling', 'Silver Foiling'],
                'design_tool_enabled': True,
                'pricing_structure': {
                    'type': 'standard_calculator',
                    'base_per_100': 299,
                    'quantity_breaks': [100, 250, 500, 1000, 2000, 5000],
                    'finish_costs': {'matte': 0, 'gloss': 0, 'spot_uv': 150, 'foiling': 300}
                },
                'featured': True,
                'bestseller': True,
                'min_quantity': 100,
                'lead_time_days': 2
            },
            {
                'name': 'Corporate Letterheads',
                'slug': 'letterhead-printing',
                'category_slug': 'letter-head', 
                'product_type': 'stationery',
                'base_price': Decimal('199.00'),
                'description': 'Professional letterheads for corporate correspondence. Premium paper options with custom designs that reflect your brand identity.',
                'short_description': 'Professional letterheads with custom designs',
                'size_options': ['A4 (210×297mm)', 'Letter (216×279mm)', 'Legal (216×356mm)'],
                'paper_options': ['80 GSM Bond Paper', '100 GSM Maplitho', '120 GSM Art Paper'],
                'print_options': ['Single Side', 'Double Side', 'Watermark'],
                'finish_options': ['No Finish', 'Embossing', 'Foil Stamping'],
                'design_tool_enabled': True,
                'pricing_structure': {
                    'type': 'standard_calculator',
                    'base_per_100': 199,
                    'paper_costs': {'80gsm': 0, '100gsm': 25, '120gsm': 50}
                },
                'min_quantity': 100,
                'lead_time_days': 3
            },
            {
                'name': 'Custom Stickers & Labels',
                'slug': 'custom-stickers',
                'category_slug': 'sticker',
                'product_type': 'stationery',
                'base_price': Decimal('149.00'),
                'description': 'Custom stickers and labels in any shape and size for branding, promotions, and product labeling with waterproof and UV-resistant options.',
                'short_description': 'Custom stickers in any shape with waterproof options',
                'size_options': ['1 inch', '2 inch', '3 inch', '4 inch', 'Custom Size'],
                'paper_options': ['Vinyl Sticker', 'Paper Sticker', 'Transparent', 'Metallic Foil'],
                'print_options': ['Full Color', 'Single Color', 'Spot Colors'],
                'finish_options': ['Matte', 'Gloss', 'Waterproof', 'UV Resistant'],
                'design_tool_enabled': True,
                'pricing_structure': {
                    'type': 'standard_calculator',
                    'base_per_100': 149,
                    'material_costs': {'vinyl': 0, 'paper': -20, 'transparent': 50, 'metallic': 100}
                },
                'min_quantity': 50,
                'lead_time_days': 3
            }
        ]
        
        # Marketing Products
        marketing_products = [
            {
                'name': 'Professional Brochures',
                'slug': 'brochure-printing',
                'category_slug': 'brochures',
                'product_type': 'marketing',
                'base_price': Decimal('599.00'),
                'description': 'High-impact brochures that showcase your business professionally. Multiple folding options, premium papers, and professional finishing available.',
                'short_description': 'Professional brochures with multiple folding options',
                'size_options': ['A4 (210×297mm)', 'A5 (148×210mm)', 'DL (99×210mm)', 'Custom'],
                'paper_options': ['130 GSM Art Paper', '150 GSM Art Paper', '200 GSM Art Paper', '250 GSM Art Card'],
                'print_options': ['Single Side', 'Double Side', 'Full Color'],
                'binding_options': ['Bi-fold', 'Tri-fold', 'Z-fold', 'Gate Fold', 'Accordion Fold'],
                'finish_options': ['Matte Lamination', 'Gloss Lamination', 'Spot UV', 'Embossing'],
                'pricing_structure': {
                    'type': 'standard_calculator', 
                    'base_per_100': 599,
                    'folding_costs': {'bi': 0, 'tri': 25, 'z': 25, 'gate': 50, 'accordion': 75}
                },
                'featured': True,
                'min_quantity': 50,
                'lead_time_days': 4
            },
            {
                'name': 'Marketing Flyers',
                'slug': 'flyer-printing',
                'category_slug': 'flyers',
                'product_type': 'marketing', 
                'base_price': Decimal('199.00'),
                'description': 'Eye-catching flyers for promotions, events, and marketing campaigns. High-quality printing with fast turnaround times and bulk discounts.',
                'short_description': 'High-quality marketing flyers with vibrant colors',
                'size_options': ['A4 (210×297mm)', 'A5 (148×210mm)', 'DL (99×210mm)', '6×4 inches'],
                'paper_options': ['130 GSM Art Paper', '170 GSM Art Paper', '250 GSM Art Card'],
                'print_options': ['Single Side', 'Double Side'],
                'finish_options': ['No Finish', 'Matte Lamination', 'Gloss Lamination'],
                'pricing_structure': {
                    'type': 'standard_calculator',
                    'base_per_100': 199,
                    'same_day_available': True
                },
                'featured': True,
                'min_quantity': 50,
                'lead_time_days': 1
            },
            {
                'name': 'Professional Posters',
                'slug': 'poster-printing',
                'category_slug': 'poster',
                'product_type': 'marketing',
                'base_price': Decimal('299.00'),
                'description': 'Large format poster printing for events, promotions, and advertising. Weather-resistant materials and vibrant color output available.',
                'short_description': 'Large format posters with vibrant colors',
                'size_options': ['A3 (297×420mm)', 'A2 (420×594mm)', 'A1 (594×841mm)', 'A0 (841×1189mm)'],
                'paper_options': ['200 GSM Photo Paper', '300 GSM Art Card', 'Vinyl', 'Canvas'],
                'print_options': ['Full Color', 'Black & White'],
                'finish_options': ['Matte', 'Gloss', 'Laminated', 'Weather Resistant'],
                'pricing_structure': {
                    'type': 'large_format',
                    'base_per_sqft': 150,
                    'material_multiplier': {'paper': 1, 'vinyl': 1.5, 'canvas': 2}
                },
                'min_quantity': 1,
                'lead_time_days': 3
            }
        ]
        
        # Create all products
        all_products = book_products + stationery_products + marketing_products
        
        for product_data in all_products:
            try:
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
                        'size_options': product_data.get('size_options', []),
                        'paper_options': product_data.get('paper_options', []),
                        'print_options': product_data.get('print_options', []),
                        'binding_options': product_data.get('binding_options', []),
                        'finish_options': product_data.get('finish_options', []),
                        'design_tool_enabled': product_data.get('design_tool_enabled', False),
                        'pricing_structure': product_data.get('pricing_structure', {}),
                        'featured': product_data.get('featured', False),
                        'bestseller': product_data.get('bestseller', False),
                        'min_quantity': product_data.get('min_quantity', 1),
                        'lead_time_days': product_data.get('lead_time_days', 3),
                        'tags': [product_data['product_type'], 'professional', 'quality']
                    }
                )
                if created:
                    self.stdout.write(f'Created product: {product.name}')
            except ProductCategory.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Category {product_data["category_slug"]} not found for {product_data["name"]}')
                )
    
    def create_design_templates(self):
        """Create design templates for products with design tools"""
        templates_data = [
            {
                'name': 'Professional Business Card - Blue Theme',
                'category': 'business-cards',
                'product_types': ['business-cards'],
                'width': 90,
                'height': 54,
                'template_data': {
                    'background': '#ffffff',
                    'elements': [
                        {
                            'type': 'rectangle',
                            'x': 0, 'y': 0, 'width': 90, 'height': 15,
                            'fill': '#2563eb'
                        },
                        {
                            'type': 'text',
                            'content': 'Your Name',
                            'x': 10, 'y': 25,
                            'fontSize': 16, 'fontFamily': 'Arial Bold',
                            'color': '#1f2937'
                        },
                        {
                            'type': 'text', 
                            'content': 'Job Title',
                            'x': 10, 'y': 35,
                            'fontSize': 12, 'fontFamily': 'Arial',
                            'color': '#6b7280'
                        }
                    ]
                },
                'tags': ['professional', 'blue', 'corporate'],
                'is_featured': True
            },
            {
                'name': 'Modern Letterhead - Corporate',
                'category': 'letterhead',
                'product_types': ['letter-head'],
                'width': 210,
                'height': 297,
                'template_data': {
                    'background': '#ffffff',
                    'elements': [
                        {
                            'type': 'rectangle',
                            'x': 0, 'y': 0, 'width': 210, 'height': 50,
                            'fill': '#f8fafc'
                        },
                        {
                            'type': 'text',
                            'content': 'Company Name',
                            'x': 20, 'y': 30,
                            'fontSize': 24, 'fontFamily': 'Arial Bold',
                            'color': '#1f2937'
                        }
                    ]
                },
                'tags': ['corporate', 'professional', 'modern'],
                'is_featured': True
            },
            {
                'name': 'Creative Sticker Template',
                'category': 'stickers',
                'product_types': ['sticker'],
                'width': 100,
                'height': 100,
                'template_data': {
                    'background': '#ffffff',
                    'elements': [
                        {
                            'type': 'circle',
                            'x': 50, 'y': 50, 'radius': 45,
                            'fill': '#667eea'
                        },
                        {
                            'type': 'text',
                            'content': 'Your Logo',
                            'x': 50, 'y': 50,
                            'fontSize': 14, 'fontFamily': 'Arial Bold',
                            'color': '#ffffff', 'textAlign': 'center'
                        }
                    ]
                },
                'tags': ['creative', 'circular', 'logo'],
                'is_featured': True
            }
        ]
        
        for template_data in templates_data:
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

    def add_sample_bestsellers(self):
        """Add sample bestselling products for homepage"""
        bestsellers = [
            {
                'name': 'Book Printing',
                'slug': 'book-printing-general',
                'category_slug': 'book-printing',
                'product_type': 'book',
                'base_price': Decimal('299.00'),
                'description': 'On Demand Digital Book Printing in India with premium paper quality and fast delivery options.',
                'short_description': 'Premium quality book printing with various binding options',
                'bestseller': True,
                'featured': True
            },
            {
                'name': 'Paper Boxes',
                'slug': 'paper-boxes-general',
                'category_slug': 'paper-box-printing',
                'product_type': 'box',
                'base_price': Decimal('199.00'),
                'description': 'Custom paper boxes for retail, medical, and cosmetic packaging with eco-friendly materials.',
                'short_description': 'Custom paper boxes for various industries',
                'bestseller': True,
                'featured': True
            },
            {
                'name': 'Marketing Materials',
                'slug': 'marketing-materials-general',
                'category_slug': 'marketing-products',
                'product_type': 'marketing',
                'base_price': Decimal('249.00'),
                'description': 'Eye-catching brochures, flyers, and marketing materials for business promotion.',
                'short_description': 'Professional marketing and promotional materials',
                'bestseller': True,
                'featured': True,
                'design_tool_enabled': True
            },
            {
                'name': 'Stationery Products',
                'slug': 'stationery-products-general',
                'category_slug': 'stationery-products',
                'product_type': 'stationery',
                'base_price': Decimal('299.00'),
                'description': 'Professional business cards, letterheads, and office stationery with premium finish options.',
                'short_description': 'Complete business stationery solutions',
                'bestseller': True,
                'featured': True,
                'design_tool_enabled': True
            }
        ]
        
        for product_data in bestsellers:
            try:
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
                        'pricing_structure': {
                            'type': 'general',
                            'features': ['Premium Quality', 'Fast Delivery', 'Professional Service']
                        },
                        'bestseller': product_data.get('bestseller', False),
                        'featured': product_data.get('featured', False),
                        'design_tool_enabled': product_data.get('design_tool_enabled', False),
                        'tags': ['bestseller', 'featured', 'quality']
                    }
                )
                if created:
                    self.stdout.write(f'Created bestseller: {product.name}')
            except ProductCategory.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Category {product_data["category_slug"]} not found for {product_data["name"]}')
                )