# apps/products/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from decimal import Decimal

# class User(AbstractUser):
#     """Extended User model for customer information"""
#     phone = models.CharField(max_length=15, blank=True)
#     gst_number = models.CharField(max_length=15, blank=True)
#     company_name = models.CharField(max_length=255, blank=True)
#     is_verified = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}" if self.first_name else self.username

class ProductCategory(models.Model):
    """Product categories matching your navbar structure"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Products with flexible pricing structure"""
    PRODUCT_TYPES = [
        ('book', 'Book Printing'),
        ('box', 'Paper Box'),
        ('marketing', 'Marketing Material'), 
        ('stationery', 'Stationery'),
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    description = models.TextField()
    short_description = models.TextField(max_length=500)
    
    # Basic pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Complex pricing structure (JSON field for your Excel data)
    pricing_structure = models.JSONField(default=dict, help_text="Complex pricing data from Excel")
    
    # Product specifications
    size_options = models.JSONField(default=list, help_text="Available sizes")
    paper_options = models.JSONField(default=list, help_text="Paper types and GSM")
    print_options = models.JSONField(default=list, help_text="Print types (B&W, Color)")
    binding_options = models.JSONField(default=list, help_text="Binding options for books")
    finish_options = models.JSONField(default=list, help_text="Finish options")
    
    # Design tool integration
    design_tool_enabled = models.BooleanField(default=False)
    design_templates = models.JSONField(default=list, help_text="Available templates")
    custom_size_allowed = models.BooleanField(default=False)
    
    # Quantity limits
    min_quantity = models.IntegerField(default=1)
    max_quantity = models.IntegerField(null=True, blank=True)
    
    # Inventory and fulfillment
    STOCK_STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('made_to_order', 'Made to Order'),
    ]
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS_CHOICES, default='made_to_order')
    lead_time_days = models.IntegerField(default=3)
    rush_available = models.BooleanField(default=True)
    
    # Marketing flags
    featured = models.BooleanField(default=False)
    bestseller = models.BooleanField(default=False)
    
    # SEO fields
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-featured', '-bestseller', 'name']
    
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    """Product images"""
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order']

class PricingCalculator(models.Model):
    """Pricing calculator based on your Excel structure"""
    
    # Book printing rates from your Excel
    BOOK_SIZES = {
        'A4': {'width': 210, 'height': 297, 'display': 'A4 (8.27 x 11.69 in)'},
        'Letter': {'width': 216, 'height': 279, 'display': 'Letter (8.5 x 11 in)'},
        'Executive': {'width': 178, 'height': 254, 'display': 'Executive (7 x 10 in)'},
        'A5': {'width': 148, 'height': 210, 'display': 'A5 (5.83 x 8.27 in)'},
    }
    
    # Rates from your Excel sheet
    BOOK_RATES = {
        'A4': {
            'bw_standard': {'75gsm': 1.1, '100gsm': 1.35, '100gsm_art': 1.8, '130gsm_art': 2.1},
            'bw_premium': {'75gsm': 1.3, '100gsm': 1.55, '100gsm_art': 2.0, '130gsm_art': 2.3},
            'color_standard': {'75gsm': 2.5, '100gsm': 2.7, '100gsm_art': 2.9, '130gsm_art': 3.15},
            'color_premium': {'75gsm': 2.7, '100gsm': 2.9, '100gsm_art': 3.1, '130gsm_art': 3.3},
            'shipping': {'bw': 0.1, 'color': 0.13}
        },
        'Letter': {
            'bw_standard': {'75gsm': 1.1, '100gsm': 1.35, '100gsm_art': 1.8, '130gsm_art': 2.1},
            'bw_premium': {'75gsm': 1.3, '100gsm': 1.55, '100gsm_art': 2.0, '130gsm_art': 2.3},
            'color_standard': {'75gsm': 2.5, '100gsm': 2.7, '100gsm_art': 2.9, '130gsm_art': 3.15},
            'color_premium': {'75gsm': 2.7, '100gsm': 2.9, '100gsm_art': 3.1, '130gsm_art': 3.3},
            'shipping': {'bw': 0.1, 'color': 0.13}
        },
        'Executive': {
            'bw_standard': {'75gsm': 1.1, '100gsm': 1.35, '100gsm_art': 1.8, '130gsm_art': 2.1},
            'bw_premium': {'75gsm': 1.3, '100gsm': 1.55, '100gsm_art': 2.0, '130gsm_art': 2.3},
            'color_standard': {'75gsm': 2.5, '100gsm': 2.7, '100gsm_art': 2.9, '130gsm_art': 3.15},
            'color_premium': {'75gsm': 2.7, '100gsm': 2.9, '100gsm_art': 3.1, '130gsm_art': 3.3},
            'shipping': {'bw': 0.1, 'color': 0.13}
        },
        'A5': {
            'bw_standard': {'75gsm': 0.6, '100gsm': 0.75, '100gsm_art': 0.9, '130gsm_art': 1.1},
            'bw_premium': {'75gsm': 0.75, '100gsm': 0.9, '100gsm_art': 1.1, '130gsm_art': 1.25},
            'color_standard': {'75gsm': 1.25, '100gsm': 1.35, '100gsm_art': 1.45, '130gsm_art': 1.58},
            'color_premium': {'75gsm': 1.35, '100gsm': 1.45, '100gsm_art': 1.6, '130gsm_art': 1.75},
            'shipping': {'bw': 0.05, 'color': 0.07}
        }
    }
    
    # Binding options from your Excel
    BINDING_OPTIONS = {
        'paperback_perfect': {'name': 'Paperback (Perfect)', 'rate': 40, 'min_pages': 32, 'max_pages': 800},
        'spiral_binding': {'name': 'Spiral Binding', 'rate': 40, 'min_pages': 20, 'max_pages': 470},
        'hardcover': {'name': 'Hardcover', 'rate': 150, 'min_pages': 32, 'max_pages': 800},
        'saddle_stitch': {'name': 'Saddle Stitch', 'rate': 25, 'min_pages': 8, 'max_pages': 48},
        'wire_o_bound': {'name': 'Wire-O Bound', 'rate': 60, 'min_pages': 32, 'max_pages': None}
    }
    
    # Quantity discounts from your Excel
    QUANTITY_DISCOUNTS = [
        {'min': 25, 'discount': 0.02, 'label': '2%'},
        {'min': 50, 'discount': 0.04, 'label': '4%'},
        {'min': 75, 'discount': 0.06, 'label': '6%'},
        {'min': 100, 'discount': 0.08, 'label': '8%'},
        {'min': 150, 'discount': 0.10, 'label': '10%'},
        {'min': 200, 'discount': 0.12, 'label': '12%'},
        {'min': 250, 'discount': 0.14, 'label': '14%'},
        {'min': 300, 'discount': 0.16, 'label': '16%'}
    ]
    
    # Design services from your Excel
    DESIGN_RATES = {
        'cover_design': 1500,
        'isbn_allocation': 1500,
        'design_support': {'A4': 50, 'Letter': 50, 'Executive': 50, 'A5': 40}
    }
    
    @classmethod
    def calculate_book_price(cls, size='A4', paper_type='75gsm', print_type='bw_standard', 
                           pages=100, quantity=50, binding_type='paperback_perfect',
                           include_cover_design=False, include_isbn=False, include_design_support=False):
        """Calculate book printing price based on your Excel structure"""
        
        result = {
            'breakdown': [],
            'subtotal': Decimal('0.00'),
            'discount': Decimal('0.00'),
            'total': Decimal('0.00'),
            'per_book': Decimal('0.00'),
            'errors': []
        }
        
        # Validate inputs
        if size not in cls.BOOK_RATES:
            result['errors'].append(f"Invalid size: {size}")
            return result
            
        if print_type not in cls.BOOK_RATES[size]:
            result['errors'].append(f"Invalid print type: {print_type}")
            return result
            
        if paper_type not in cls.BOOK_RATES[size][print_type]:
            result['errors'].append(f"Invalid paper type: {paper_type}")
            return result
            
        if binding_type not in cls.BINDING_OPTIONS:
            result['errors'].append(f"Invalid binding type: {binding_type}")
            return result
        
        # Check page limits
        binding = cls.BINDING_OPTIONS[binding_type]
        if pages < binding['min_pages']:
            result['errors'].append(f"Minimum {binding['min_pages']} pages required for {binding['name']}")
            return result
        if binding['max_pages'] and pages > binding['max_pages']:
            result['errors'].append(f"Maximum {binding['max_pages']} pages allowed for {binding['name']}")
            return result
        
        # Calculate printing cost
        page_rate = Decimal(str(cls.BOOK_RATES[size][print_type][paper_type]))
        printing_cost = pages * page_rate * quantity
        result['breakdown'].append({
            'item': f'Printing ({pages} pages × {quantity} books × ₹{page_rate})',
            'cost': printing_cost
        })
        
        # Calculate binding cost
        binding_cost = Decimal(str(binding['rate'])) * quantity
        result['breakdown'].append({
            'item': f'{binding["name"]} ({quantity} books × ₹{binding["rate"]})',
            'cost': binding_cost
        })
        
        # Calculate shipping
        shipping_type = 'color' if 'color' in print_type else 'bw'
        shipping_rate = Decimal(str(cls.BOOK_RATES[size]['shipping'][shipping_type]))
        shipping_cost = pages * shipping_rate * quantity
        result['breakdown'].append({
            'item': f'Shipping ({pages} pages × {quantity} books × ₹{shipping_rate})',
            'cost': shipping_cost
        })
        
        result['subtotal'] = printing_cost + binding_cost + shipping_cost
        
        # Add one-time costs
        if include_cover_design:
            cover_cost = Decimal(str(cls.DESIGN_RATES['cover_design']))
            result['breakdown'].append({
                'item': 'Cover Design (One-time)',
                'cost': cover_cost
            })
            result['subtotal'] += cover_cost
            
        if include_isbn:
            isbn_cost = Decimal(str(cls.DESIGN_RATES['isbn_allocation']))
            result['breakdown'].append({
                'item': 'ISBN Allocation (One-time)',
                'cost': isbn_cost
            })
            result['subtotal'] += isbn_cost
            
        if include_design_support:
            design_cost = Decimal(str(cls.DESIGN_RATES['design_support'][size]))
            result['breakdown'].append({
                'item': f'Design Support ({size})',
                'cost': design_cost
            })
            result['subtotal'] += design_cost
        
        # Calculate quantity discount
        discount_info = cls.get_quantity_discount(quantity)
        if discount_info['percentage'] > 0:
            result['discount'] = result['subtotal'] * Decimal(str(discount_info['percentage']))
            result['breakdown'].append({
                'item': f'Quantity Discount ({quantity} books - {discount_info["label"]})',
                'cost': -result['discount']
            })
        
        result['total'] = result['subtotal'] - result['discount']
        result['per_book'] = result['total'] / quantity if quantity > 0 else Decimal('0.00')
        
        return result
    
    @classmethod
    def get_quantity_discount(cls, quantity):
        """Get applicable quantity discount"""
        for tier in reversed(cls.QUANTITY_DISCOUNTS):
            if quantity >= tier['min']:
                return {
                    'percentage': tier['discount'],
                    'label': tier['label'],
                    'min_quantity': tier['min']
                }
        return {'percentage': 0, 'label': 'No Discount', 'min_quantity': 0}

class DesignTemplate(models.Model):
    """Design templates for the design tool"""
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    product_types = models.JSONField(default=list, help_text="Which products can use this template")
    
    # Template data
    template_data = models.JSONField(help_text="Canvas data, elements, etc.")
    preview_image = models.ImageField(upload_to='templates/previews/', blank=True)
    thumbnail_image = models.ImageField(upload_to='templates/thumbnails/', blank=True)
    
    # Specifications
    width = models.IntegerField(help_text="Width in pixels or mm")
    height = models.IntegerField(help_text="Height in pixels or mm")
    dpi = models.IntegerField(default=300)
    
    COLOR_MODES = [
        ('RGB', 'RGB'),
        ('CMYK', 'CMYK'),
    ]
    color_mode = models.CharField(max_length=4, choices=COLOR_MODES, default='CMYK')
    
    # Categorization
    tags = models.JSONField(default=list)
    is_premium = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-usage_count', 'name']
    
    def __str__(self):
        return self.name

# class UserDesign(models.Model):
#     """User saved designs"""
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='designs')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     template = models.ForeignKey(DesignTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
#     name = models.CharField(max_length=255)
#     design_data = models.JSONField(help_text="Canvas data")
#     preview_image = models.ImageField(upload_to='user_designs/previews/', blank=True)
    
#     is_favorite = models.BooleanField(default=False)
#     last_modified = models.DateTimeField(auto_now=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['-last_modified']
    
#     def __str__(self):
#         return f"{self.user.username} - {self.name}"

