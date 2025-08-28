# apps/services/views.py
from django.shortcuts import render
from django.views.generic import TemplateView

class ServicesDirectoryView(TemplateView):
    template_name = 'services/services_directory.html'

class ServiceDetailView(TemplateView):
    template_name = 'services/service_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_slug = kwargs.get('service_slug')
        
        # Define service data based on your plan.md
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
        
        context.update(service_data)
        context['service_slug'] = service_slug
        
        return context
    
    def get_all_services_data(self):
        """Return all service data"""
        return {
            # Book Printing Services
            'childrens-book-printing': {
                'title': 'Children\'s Book Printing',
                'category': 'Book Printing',
                'hero_title': 'Premium Children\'s Book Printing Services',
                'hero_description': 'Bring stories to life with our high-quality children\'s book printing. Perfect binding, vibrant colors, and child-safe materials.',
                'starting_price': 299,
                'features': [
                    'Child-safe, non-toxic inks',
                    'Durable binding options', 
                    'Vibrant color reproduction',
                    'Custom sizes available',
                    'Quick 3-5 day turnaround',
                    'Bulk pricing discounts'
                ],
                'specifications': {
                    'Paper Types': ['70 GSM', '80 GSM', '100 GSM Art Paper'],
                    'Binding Options': ['Perfect Binding', 'Saddle Stitching', 'Hardcover'],
                    'Print Quality': ['Full Color', 'Black & White'],
                    'Sizes': ['A4', 'A5', 'Custom sizes'],
                    'Minimum Order': ['25 copies']
                },
                'process_steps': [
                    'Upload your manuscript and images',
                    'Choose paper type and binding',
                    'Review digital proof',
                    'Production begins',
                    'Quality check and packaging',
                    'Fast delivery to your doorstep'
                ]
            },
            'business-cards': {
                'title': 'Business Cards',
                'category': 'Stationery',
                'hero_title': 'Professional Business Cards',
                'hero_description': 'Make a lasting first impression with premium business cards. Multiple finishes and paper options available.',
                'starting_price': 299,
                'features': [
                    'Premium 300 GSM cardstock',
                    'Multiple finish options',
                    'Design tool available',
                    'Same-day printing available', 
                    'Bulk quantity discounts',
                    'Free design consultation'
                ],
                'specifications': {
                    'Paper Types': ['300 GSM', '350 GSM', 'Textured'],
                    'Finishes': ['Matte', 'Gloss', 'Spot UV', 'Foiling'],
                    'Sizes': ['Standard 3.5" x 2"', 'Square', 'Custom'],
                    'Print Options': ['Single Side', 'Double Side'],
                    'Minimum Order': ['100 cards']
                },
                'process_steps': [
                    'Choose your design or use our tool',
                    'Select paper and finish options',
                    'Review digital proof',
                    'Production and quality check',
                    'Fast delivery'
                ]
            },
            'brochures': {
                'title': 'Brochure Printing',
                'category': 'Marketing',
                'hero_title': 'High-Quality Brochure Printing',
                'hero_description': 'Professional brochures that showcase your business. Multiple folding options and premium paper stocks.',
                'starting_price': 599,
                'features': [
                    'Multiple folding options',
                    'Premium paper stocks',
                    'Full-color printing',
                    'Gloss or matte finishes',
                    'Quick turnaround',
                    'Bulk pricing available'
                ],
                'specifications': {
                    'Paper Types': ['130 GSM', '150 GSM', '200 GSM Art'],
                    'Fold Types': ['Bi-fold', 'Tri-fold', 'Z-fold', 'Gate fold'],
                    'Sizes': ['A4', 'A5', 'DL', 'Custom'],
                    'Finishes': ['Matte', 'Gloss', 'Satin'],
                    'Minimum Order': ['50 pieces']
                },
                'process_steps': [
                    'Upload your design files',
                    'Choose folding and paper options',
                    'Review digital proof',
                    'Production begins',
                    'Quality check and delivery'
                ]
            },
            # Add basic data for other services (they'll share similar structure)
            'comic-book-printing': {
                'title': 'Comic Book Printing',
                'category': 'Book Printing',
                'hero_title': 'Professional Comic Book Printing',
                'hero_description': 'High-quality comic book printing with vibrant colors and professional binding.',
                'starting_price': 449,
                'features': ['High-resolution printing', 'Multiple binding options', 'Vibrant colors', 'Custom sizes', 'Quick turnaround', 'Bulk discounts'],
                'specifications': {'Paper Types': ['70 GSM', '80 GSM', '100 GSM'], 'Binding': ['Saddle Stitch', 'Perfect Bound'], 'Sizes': ['Standard', 'Custom'], 'Minimum Order': ['25 copies']},
                'process_steps': ['Upload artwork', 'Select specifications', 'Review proof', 'Production', 'Quality check', 'Delivery']
            },
            'coffee-table-book-printing': {
                'title': 'Coffee Table Book Printing',
                'category': 'Book Printing',
                'hero_title': 'Luxury Coffee Table Book Printing',
                'hero_description': 'Premium coffee table books with exceptional print quality for photography and art.',
                'starting_price': 1299,
                'features': ['Premium art paper', 'Hardcover binding', 'Large format', 'Museum quality', 'Dust jackets', 'Premium finishes'],
                'specifications': {'Paper Types': ['150 GSM Art', '200 GSM Art', '250 GSM Art'], 'Binding': ['Hardcover', 'Case Bound'], 'Sizes': ['Large Format', 'Custom'], 'Minimum Order': ['10 copies']},
                'process_steps': ['Design consultation', 'File preparation', 'Proof review', 'Premium production', 'Quality inspection', 'Delivery']
            },
            'flyers': {
                'title': 'Flyer Printing',
                'category': 'Marketing',
                'hero_title': 'Eye-Catching Flyer Printing',
                'hero_description': 'Promote your business with high-quality flyers that grab attention.',
                'starting_price': 199,
                'features': ['Vibrant colors', 'Multiple sizes', 'Bulk pricing', 'Quick turnaround', 'Premium paper', 'Free design support'],
                'specifications': {'Paper Types': ['130 GSM', '170 GSM', '250 GSM'], 'Sizes': ['A4', 'A5', 'DL', 'Custom'], 'Finishes': ['Matte', 'Gloss'], 'Minimum Order': ['50 pieces']},
                'process_steps': ['Design upload', 'Size selection', 'Proof review', 'Mass production', 'Quality check', 'Fast delivery']
            }
        }