# apps/services/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.urls import reverse
from apps.products.models import Product, ProductCategory

class ServicesDirectoryView(TemplateView):
    template_name = 'services/services_directory.html'

class ServiceDetailView(TemplateView):
    """
    Redirect service detail views to the enhanced product catalog
    This consolidates services and products into a unified experience
    """
    
    def get(self, request, *args, **kwargs):
        service_slug = kwargs.get('service_slug')
        
        # Map service slugs to product search terms or categories
        service_to_product_mapping = {
            # Book printing services
            'childrens-book-printing': 'children books',
            'comic-book-printing': 'comic books',
            'coffee-table-book-printing': 'coffee table books',
            'coloring-book-printing': 'coloring books',
            'art-book-printing': 'art books',
            'annual-reports-printing': 'annual reports',
            'year-book-printing': 'year books',
            'on-demand-books-printing': 'books',
            
            # Business stationery
            'business-cards': 'business cards',
            'letter-head': 'letterhead',
            'envelopes': 'envelopes',
            'id-cards': 'id cards',
            'bill-book': 'bill books',
            
            # Marketing materials
            'brochures': 'brochures',
            'flyers': 'flyers',
            'catalogue': 'catalogues',
            'poster': 'posters',
            'dangler': 'danglers',
            'standees': 'standees',
            
            # Packaging
            'medical-paper-boxes': 'medical boxes',
            'cosmetic-paper-boxes': 'cosmetic boxes',
            'retail-paper-boxes': 'retail boxes',
            'folding-carton-boxes': 'carton boxes',
            'corrugated-boxes': 'corrugated boxes',
            'kraft-boxes': 'kraft boxes',
            
            # Other services
            'sticker': 'stickers',
            'document-printing': 'document printing',
            'invitations': 'invitations',
            'calendars': 'calendars',
            'notebooks': 'notebooks',
            'folders': 'folders',
            'pen-drives': 'pen drives',
        }
        
        search_term = service_to_product_mapping.get(service_slug, service_slug.replace('-', ' '))
        
        # Redirect to product catalog with search term
        product_url = reverse('products:list')
        return redirect(f"{product_url}?search={search_term}")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_slug = kwargs.get('service_slug')
        
        # Define service data based on your requirements
        services_data = self.get_all_services_data()
        
        service_data = services_data.get(service_slug, {
            'title': 'Service Not Found',
            'category': 'Unknown',
            'hero_title': 'Service Not Found',
            'hero_description': 'The requested service could not be found.',
            'starting_price': 0,
            'features': [],
            'specifications': {}
        })
        
        # Try to get related product data to enhance the service page
        try:
            # Map service slugs to product categories/names
            product_mapping = {
                'business-cards': 'business-cards',
                'letter-head': 'letterheads',
                'brochures': 'brochures',
                'flyers': 'flyers',
                'poster': 'posters',
                'sticker': 'stickers',
                'envelopes': 'envelopes',
                'childrens-book-printing': 'book-printing',
                'comic-book-printing': 'book-printing',
                'coffee-table-book-printing': 'book-printing',
            }
            
            product_category_slug = product_mapping.get(service_slug)
            if product_category_slug:
                # Get products from this category
                try:
                    category = ProductCategory.objects.get(slug=product_category_slug)
                    related_products = Product.objects.filter(
                        category=category,
                        status='active'
                    ).select_related('category').prefetch_related('images')[:4]
                    context['related_products'] = related_products
                    context['product_category'] = category
                    
                    # Get the main product for this service to check design tool support
                    main_product = related_products.first()
                    if main_product:
                        context['main_product'] = main_product
                        context['supports_design_tool'] = main_product.design_tool_enabled
                        context['supports_front_back'] = main_product.front_back_design_enabled
                        context['supports_upload'] = main_product.supports_upload
                        
                except ProductCategory.DoesNotExist:
                    pass
        except Exception:
            pass
        
        context.update(service_data)
        context['service_slug'] = service_slug
        
        return context
    
    def get_all_services_data(self):
        """Return comprehensive service data with Indian pricing"""
        return {
            # Book Printing Services
            'childrens-book-printing': {
                'title': 'Children\'s Book Printing',
                'category': 'Book Printing',
                'hero_title': 'Premium Children\'s Book Printing Services',
                'hero_description': 'Bring magical stories to life with our high-quality children\'s book printing. Child-safe materials, vibrant colors, and durable binding options.',
                'starting_price': 299,
                'features': [
                    'Child-Safe Non-Toxic Inks',
                    'Vibrant Color Reproduction', 
                    'Durable Binding Options',
                    'Custom Sizes Available',
                    'Quick 3-5 Day Turnaround',
                    'Bulk Pricing Discounts',
                    'Free Design Consultation',
                    'Quality Paper Options'
                ],
                'specifications': {
                    'Paper Types': ['70 GSM Maplitho', '80 GSM Maplitho', '100 GSM Art Paper', '130 GSM Art Paper'],
                    'Binding Options': ['Perfect Binding', 'Saddle Stitching', 'Hardcover', 'Spiral Binding'],
                    'Print Quality': ['Full Color CMYK', 'Black & White', 'Spot Colors'],
                    'Sizes': ['A4 (210×297mm)', 'A5 (148×210mm)', 'Letter (216×279mm)', 'Custom sizes'],
                    'Minimum Order': ['25 copies'],
                    'Maximum Order': ['10,000 copies'],
                    'Turnaround Time': ['3-5 business days'],
                    'File Formats': ['PDF (Print Ready)', 'JPG/PNG (High Resolution)']
                },
                'process_steps': [
                    'Upload your manuscript and images or use our design service',
                    'Choose paper type, binding, and customization options',
                    'Review and approve digital proof within 24 hours',
                    'Production begins with quality monitoring',
                    'Quality check and professional packaging',
                    'Fast delivery to your doorstep with tracking'
                ],
                'pricing_structure': {
                    'base_rates': {
                        'A4': {'bw_standard': 1.1, 'bw_premium': 1.3, 'color_standard': 2.5, 'color_premium': 2.7},
                        'A5': {'bw_standard': 0.6, 'bw_premium': 0.75, 'color_standard': 1.25, 'color_premium': 1.35}
                    },
                    'binding_costs': {'perfect': 40, 'saddle': 25, 'hardcover': 150, 'spiral': 40},
                    'quantity_discounts': [
                        {'min': 25, 'discount': 2}, {'min': 50, 'discount': 4},
                        {'min': 100, 'discount': 8}, {'min': 250, 'discount': 14}
                    ]
                }
            },
            
            'comic-book-printing': {
                'title': 'Comic Book Printing',
                'category': 'Book Printing',
                'hero_title': 'Professional Comic Book Printing',
                'hero_description': 'High-quality comic book printing with vibrant colors, crisp graphics, and professional binding that brings your stories to life.',
                'starting_price': 449,
                'features': [
                    'High-Resolution Color Printing',
                    'Professional Comic Paper',
                    'Multiple Binding Options',
                    'Vibrant CMYK Colors',
                    'Custom Sizes Available',
                    'Quick Turnaround Time',
                    'Bulk Order Discounts',
                    'Professional Finishing'
                ],
                'specifications': {
                    'Paper Types': ['70 GSM Maplitho', '80 GSM Maplitho', '100 GSM Art Paper'],
                    'Binding Options': ['Saddle Stitch', 'Perfect Bound', 'Spiral Binding'],
                    'Print Quality': ['Full Color CMYK', 'Spot Colors', 'Pantone Matching'],
                    'Sizes': ['US Comic (170×260mm)', 'Manga Size (128×182mm)', 'Custom'],
                    'Minimum Order': ['25 copies'],
                    'Page Count': ['8-200 pages'],
                    'Turnaround Time': ['4-6 business days']
                },
                'process_steps': [
                    'Submit your comic artwork in print-ready format',
                    'Select paper quality and binding preferences',
                    'Review digital proof and color matching',
                    'Professional printing with color calibration',
                    'Quality control and finishing processes',
                    'Secure packaging and prompt delivery'
                ]
            },

            'coffee-table-book-printing': {
                'title': 'Coffee Table Book Printing',
                'category': 'Book Printing',
                'hero_title': 'Luxury Coffee Table Book Printing',
                'hero_description': 'Premium coffee table books with exceptional print quality for photography, art, and showcase publications.',
                'starting_price': 1299,
                'features': [
                    'Premium Art Paper Quality',
                    'Museum-Quality Printing',
                    'Hardcover Binding Standard',
                    'Large Format Capability',
                    'Dust Jacket Options',
                    'Luxury Finishing Options',
                    'Color Accuracy Guaranteed',
                    'Premium Packaging'
                ],
                'specifications': {
                    'Paper Types': ['150 GSM Art Paper', '200 GSM Art Paper', '250 GSM Art Paper', '300 GSM Art Paper'],
                    'Binding Options': ['Hardcover Case Bound', 'Premium Hardcover', 'Leather Bound (Custom)'],
                    'Print Quality': ['High-Resolution Color', 'Pantone Spot Colors', 'Metallic Inks'],
                    'Sizes': ['A4 Landscape', '25×25cm Square', '30×30cm Square', 'Custom Large Format'],
                    'Minimum Order': ['10 copies'],
                    'Page Count': ['50-300 pages'],
                    'Turnaround Time': ['7-10 business days']
                },
                'process_steps': [
                    'Design consultation for layout and specifications',
                    'High-resolution file preparation and proofing',
                    'Premium paper selection and color matching',
                    'Professional large-format printing',
                    'Luxury binding and finishing processes',
                    'Quality inspection and premium packaging'
                ]
            },

            # Business Stationery
            'business-cards': {
                'title': 'Professional Business Cards',
                'category': 'Stationery',
                'hero_title': 'Premium Business Cards That Make an Impact',
                'hero_description': 'Make a lasting first impression with our premium business cards. Multiple finishes, paper options, and design services available.',
                'starting_price': 299,
                'features': [
                    'Premium 300 GSM Cardstock',
                    'Multiple Finish Options',
                    'Online Design Tool',
                    'Same-Day Printing Available',
                    'Bulk Quantity Discounts',
                    'Free Design Consultation',
                    'Rounded Corner Options',
                    'Spot UV and Foiling'
                ],
                'specifications': {
                    'Paper Types': ['300 GSM Art Card', '350 GSM Art Card', '400 GSM Textured'],
                    'Finishes': ['Matte Lamination', 'Gloss Lamination', 'Spot UV', 'Gold/Silver Foiling'],
                    'Sizes': ['Standard (90×54mm)', 'US Standard (89×51mm)', 'Square (54×54mm)', 'Custom'],
                    'Print Options': ['Single Side', 'Double Side', 'Variable Data Printing'],
                    'Minimum Order': ['100 cards'],
                    'Maximum Order': ['10,000 cards'],
                    'Turnaround Time': ['Same day to 2 business days']
                },
                'process_steps': [
                    'Choose design template or upload your artwork',
                    'Select paper quality and finishing options',
                    'Review digital proof and make revisions',
                    'Professional printing with quality checks',
                    'Finishing processes (lamination, die-cutting)',
                    'Quality packaging and fast delivery'
                ]
            },

            'letter-head': {
                'title': 'Professional Letterheads',
                'category': 'Stationery',
                'hero_title': 'Corporate Letterhead Printing',
                'hero_description': 'Professional letterheads for your business correspondence with custom designs and premium paper quality.',
                'starting_price': 199,
                'features': [
                    'Premium Paper Quality',
                    'Custom Design Service',
                    'Watermark Options',
                    'Multiple Paper Weights',
                    'Bulk Order Discounts',
                    'Quick Setup Process',
                    'Professional Layout',
                    'Brand Consistency'
                ],
                'specifications': {
                    'Paper Types': ['80 GSM Bond Paper', '100 GSM Maplitho', '120 GSM Art Paper'],
                    'Sizes': ['A4 (210×297mm)', 'Letter (216×279mm)', 'Legal (216×356mm)'],
                    'Print Options': ['Single Side', 'Double Side', 'Watermark'],
                    'Colors': ['Full Color', 'Single Color', 'Two Color'],
                    'Minimum Order': ['100 sheets'],
                    'Turnaround Time': ['2-3 business days']
                },
                'process_steps': [
                    'Provide logo and company information',
                    'Choose paper and design preferences',
                    'Review and approve design layout',
                    'Professional printing and cutting',
                    'Quality check and packaging',
                    'Delivery with invoice and receipt'
                ]
            },

            # Marketing Materials
            'brochures': {
                'title': 'Professional Brochures',
                'category': 'Marketing',
                'hero_title': 'High-Impact Brochure Printing',
                'hero_description': 'Professional brochures that showcase your business with premium paper stocks and multiple folding options.',
                'starting_price': 599,
                'features': [
                    'Multiple Folding Options',
                    'Premium Paper Stocks',
                    'Full-Color Printing',
                    'Matte or Gloss Finishes',
                    'Quick Turnaround Time',
                    'Bulk Pricing Available',
                    'Design Assistance',
                    'Professional Finishing'
                ],
                'specifications': {
                    'Paper Types': ['130 GSM Art Paper', '150 GSM Art Paper', '200 GSM Art Paper', '250 GSM Art Card'],
                    'Fold Types': ['Bi-fold (Half Fold)', 'Tri-fold (Letter Fold)', 'Z-fold', 'Gate Fold', 'Accordion Fold'],
                    'Sizes': ['A4 (210×297mm)', 'A5 (148×210mm)', 'DL (99×210mm)', 'Custom Sizes'],
                    'Finishes': ['Matte Lamination', 'Gloss Lamination', 'Satin Finish', 'Spot UV'],
                    'Minimum Order': ['50 pieces'],
                    'Turnaround Time': ['3-4 business days']
                },
                'process_steps': [
                    'Upload design files or use our design service',
                    'Choose folding style and paper specifications',
                    'Review digital proof with fold marks',
                    'Professional printing with color management',
                    'Precision folding and quality control',
                    'Professional packaging and delivery'
                ]
            },

            'flyers': {
                'title': 'Eye-Catching Flyers',
                'category': 'Marketing',
                'hero_title': 'High-Impact Flyer Printing',
                'hero_description': 'Promote your business with vibrant, high-quality flyers that grab attention and drive results.',
                'starting_price': 199,
                'features': [
                    'Vibrant Color Printing',
                    'Multiple Paper Options',
                    'Bulk Pricing Discounts',
                    'Same-Day Printing',
                    'Weather-Resistant Options',
                    'Custom Sizes Available',
                    'Professional Design Support',
                    'High-Speed Production'
                ],
                'specifications': {
                    'Paper Types': ['130 GSM Art Paper', '170 GSM Art Paper', '250 GSM Art Card', '300 GSM Art Card'],
                    'Sizes': ['A4 (210×297mm)', 'A5 (148×210mm)', 'DL (99×210mm)', '6×4 inches', 'Custom'],
                    'Finishes': ['Matte Lamination', 'Gloss Lamination', 'No Lamination'],
                    'Print Options': ['Single Side', 'Double Side'],
                    'Minimum Order': ['50 pieces'],
                    'Maximum Order': ['50,000 pieces'],
                    'Turnaround Time': ['Same day to 2 business days']
                },
                'process_steps': [
                    'Submit your design or choose from templates',
                    'Select paper type and size options',
                    'Review digital proof for approval',
                    'High-speed digital or offset printing',
                    'Quality control and cutting to size',
                    'Fast packaging and distribution ready'
                ]
            },

            # Additional services can be added here following the same pattern
            'poster': {
                'title': 'Professional Posters',
                'category': 'Marketing',
                'hero_title': 'Large Format Poster Printing',
                'hero_description': 'High-quality poster printing for events, promotions, and advertising with vibrant colors and durable materials.',
                'starting_price': 299,
                'features': [
                    'Large Format Printing',
                    'Weather-Resistant Materials',
                    'Vibrant Color Output',
                    'Multiple Size Options',
                    'Indoor/Outdoor Options',
                    'Mounting Services Available',
                    'Quick Turnaround',
                    'Bulk Discounts'
                ],
                'specifications': {
                    'Materials': ['200 GSM Photo Paper', '300 GSM Art Card', 'Vinyl Sticker', 'Canvas'],
                    'Sizes': ['A3 (297×420mm)', 'A2 (420×594mm)', 'A1 (594×841mm)', 'A0 (841×1189mm)', 'Custom'],
                    'Finishes': ['Matte', 'Gloss', 'Satin', 'Laminated'],
                    'Mounting': ['Foam Board', 'Sunboard', 'PVC Board', 'Acrylic'],
                    'Minimum Order': ['1 piece'],
                    'Turnaround Time': ['1-3 business days']
                },
                'process_steps': [
                    'Upload high-resolution artwork files',
                    'Choose material and size specifications',
                    'Select mounting and finishing options',
                    'Large format printing with color accuracy',
                    'Professional mounting and finishing',
                    'Secure packaging for safe delivery'
                ]
            },

            'sticker': {
                'title': 'Custom Stickers & Labels',
                'category': 'Stationery',
                'hero_title': 'Custom Sticker Printing',
                'hero_description': 'Custom stickers and labels in any shape and size for branding, promotions, and product labeling.',
                'starting_price': 149,
                'features': [
                    'Any Shape & Size',
                    'Waterproof Options',
                    'Vibrant Colors',
                    'Die-Cut Services',
                    'Kiss-Cut Available',
                    'Permanent/Removable Adhesive',
                    'UV Resistant',
                    'Food Grade Options'
                ],
                'specifications': {
                    'Materials': ['Vinyl Sticker', 'Paper Sticker', 'Transparent Sticker', 'Metallic Foil'],
                    'Adhesive Types': ['Permanent', 'Removable', 'Ultra Removable', 'Food Safe'],
                    'Finishes': ['Matte', 'Gloss', 'Satin', 'Textured'],
                    'Shapes': ['Round', 'Square', 'Rectangle', 'Oval', 'Custom Die-Cut'],
                    'Sizes': ['1 inch to 12 inches', 'Custom dimensions'],
                    'Minimum Order': ['50 pieces'],
                    'Turnaround Time': ['2-4 business days']
                },
                'process_steps': [
                    'Submit artwork or use our design templates',
                    'Choose material, size, and shape options',
                    'Select adhesive type and finishing',
                    'Digital printing with color matching',
                    'Precision die-cutting or kiss-cutting',
                    'Quality packaging and fast shipping'
                ]
            }
        }
    
    def get_pricing_data(self, service_type):
        """Get detailed pricing structure for different services"""
        if service_type in ['childrens-book-printing', 'comic-book-printing', 'coffee-table-book-printing']:
            return {
                'type': 'book_printing',
                'base_rates': {
                    'A4': {
                        'bw_standard': {'75gsm': 1.1, '100gsm': 1.35, '100gsm_art': 1.8, '130gsm_art': 2.1},
                        'bw_premium': {'75gsm': 1.3, '100gsm': 1.55, '100gsm_art': 2.0, '130gsm_art': 2.3},
                        'color_standard': {'75gsm': 2.5, '100gsm': 2.7, '100gsm_art': 2.9, '130gsm_art': 3.15},
                        'color_premium': {'75gsm': 2.7, '100gsm': 2.9, '100gsm_art': 3.1, '130gsm_art': 3.3}
                    },
                    'A5': {
                        'bw_standard': {'75gsm': 0.6, '100gsm': 0.75, '100gsm_art': 0.9, '130gsm_art': 1.1},
                        'bw_premium': {'75gsm': 0.75, '100gsm': 0.9, '100gsm_art': 1.1, '130gsm_art': 1.25},
                        'color_standard': {'75gsm': 1.25, '100gsm': 1.35, '100gsm_art': 1.45, '130gsm_art': 1.58},
                        'color_premium': {'75gsm': 1.35, '100gsm': 1.45, '100gsm_art': 1.6, '130gsm_art': 1.75}
                    }
                },
                'binding_costs': {
                    'paperback_perfect': 40,
                    'spiral_binding': 40,
                    'hardcover': 150,
                    'saddle_stitch': 25
                },
                'quantity_discounts': [
                    {'min': 25, 'discount': 0.02}, {'min': 50, 'discount': 0.04},
                    {'min': 75, 'discount': 0.06}, {'min': 100, 'discount': 0.08},
                    {'min': 150, 'discount': 0.10}, {'min': 200, 'discount': 0.12},
                    {'min': 250, 'discount': 0.14}, {'min': 300, 'discount': 0.16}
                ]
            }
        else:
            return {
                'type': 'standard_product',
                'base_pricing': True
            }