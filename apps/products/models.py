# apps/products/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import json
from decimal import Decimal
import uuid

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
    """Enhanced product categories with comprehensive features"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # SEO and marketing
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    featured = models.BooleanField(default=False)
    
    # Design tool integration
    default_bleed = models.DecimalField(max_digits=5, decimal_places=2, default=3.0, help_text="Default bleed in mm")
    default_safe_zone = models.DecimalField(max_digits=5, decimal_places=2, default=2.0, help_text="Default safe zone in mm")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_full_path(self):
        """Get full category path for breadcrumbs"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)
    
    def get_active_children(self):
        """Get active child categories"""
        return self.children.filter(is_active=True).order_by('sort_order', 'name')
    
    def get_all_products(self):
        """Get all products in this category and subcategories"""
        from django.db.models import Q
        categories = [self.id]
        
        def get_descendant_ids(category):
            children = category.children.all()
            for child in children:
                categories.append(child.id)
                get_descendant_ids(child)
        
        get_descendant_ids(self)
        return Product.objects.filter(category_id__in=categories, status='active')

class ProductSubcategory(models.Model):
    """Product subcategories for hierarchical organization"""
    parent_product = models.ForeignKey('Product', related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='subcategories/', blank=True)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    # Specifications specific to this subcategory
    size_options = models.JSONField(default=list, help_text="Available sizes for this subcategory")
    paper_options = models.JSONField(default=list, help_text="Paper types for this subcategory")
    
    class Meta:
        verbose_name_plural = "Product Subcategories"
        ordering = ['sort_order', 'name']
        unique_together = ['parent_product', 'slug']
    
    def __str__(self):
        return f"{self.parent_product.name} - {self.name}"

class ProductOption(models.Model):
    """Product options (paper, finish, binding, etc.)"""
    OPTION_TYPES = [
        ('paper', 'Paper Type'),
        ('finish', 'Finish'),
        ('binding', 'Binding'),
        ('color', 'Color Mode'),
        ('size', 'Size'),
        ('coating', 'Coating'),
        ('corners', 'Corner Style'),
        ('quantity', 'Quantity'),
        ('orientation', 'Orientation'),
        ('lamination', 'Lamination'),
        ('perforation', 'Perforation'),
        ('folding', 'Folding'),
        ('cutting', 'Cutting'),
        ('embossing', 'Embossing'),
        ('foiling', 'Foiling'),
    ]
    
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)
    option_type = models.CharField(max_length=20, choices=OPTION_TYPES)
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    # Display configuration
    display_as_grid = models.BooleanField(default=False, help_text="Display as visual grid instead of dropdown")
    show_images = models.BooleanField(default=False, help_text="Show images for option values")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = ['product', 'name']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"

class OptionValue(models.Model):
    """Values for product options"""
    option = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_name='values')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Pricing
    price_modifier = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Additional cost for this option")
    price_modifier_type = models.CharField(max_length=10, choices=[
        ('fixed', 'Fixed Amount'),
        ('percent', 'Percentage')
    ], default='fixed')
    
    # Visual representation
    image = models.ImageField(upload_to='option_values/', blank=True, null=True)
    color_code = models.CharField(max_length=7, blank=True, help_text="Hex color code for visual representation")
    
    # Specifications
    specifications = models.JSONField(default=dict, help_text="Technical specifications (GSM, dimensions, etc.)")
    
    # Configuration
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    # Stock and availability
    stock_quantity = models.IntegerField(null=True, blank=True, help_text="Stock quantity (null = unlimited)")
    lead_time_days = models.IntegerField(default=0, help_text="Additional lead time for this option")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = ['option', 'name']
    
    def __str__(self):
        return f"{self.option.name} - {self.name}"
    
    def get_price_display(self):
        """Get formatted price modifier for display"""
        if self.price_modifier == 0:
            return "No additional cost"
        elif self.price_modifier_type == 'percent':
            return f"+{self.price_modifier}%"
        else:
            return f"+₹{self.price_modifier:.1f}"

class ProductVariant(models.Model):
    """Product variants (different sizes, materials, etc.)"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    
    # Dimensions
    width = models.DecimalField(max_digits=8, decimal_places=2, help_text="Width in mm")
    height = models.DecimalField(max_digits=8, decimal_places=2, help_text="Height in mm")
    depth = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Depth in mm (for 3D products)")
    unit = models.CharField(max_length=10, choices=[('mm', 'MM'), ('in', 'Inches'), ('cm', 'CM')], default='mm')
    
    # Pricing modifiers
    price_modifier = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_modifier_type = models.CharField(max_length=10, choices=[
        ('fixed', 'Fixed Amount'),
        ('percent', 'Percentage')
    ], default='fixed')
    
    # Design tool specifications
    bleed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Bleed in mm (overrides product default)")
    safe_zone = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Safe zone in mm (overrides product default)")
    
    # Stock and availability
    stock_quantity = models.IntegerField(null=True, blank=True, help_text="Stock quantity (null = unlimited)")
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = ['product', 'name']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    def get_dimensions_display(self):
        """Get formatted dimensions for display"""
        if self.depth:
            return f"{self.width:.2f} × {self.height:.2f} × {self.depth:.2f} {self.unit}"
        return f"{self.width:.2f} × {self.height:.2f} {self.unit}"
    
    def get_effective_bleed(self):
        """Get effective bleed (variant-specific or product default)"""
        return self.bleed if self.bleed is not None else self.product.category.default_bleed
    
    def get_effective_safe_zone(self):
        """Get effective safe zone (variant-specific or product default)"""
        return self.safe_zone if self.safe_zone is not None else self.product.category.default_safe_zone

class PricingRule(models.Model):
    """Pricing rules for complex pricing calculations"""
    RULE_TYPES = [
        ('base', 'Base Price'),
        ('quantity', 'Quantity Break'),
        ('option', 'Option Surcharge'),
        ('regional', 'Regional Pricing'),
        ('bulk', 'Bulk Discount'),
        ('seasonal', 'Seasonal Pricing'),
        ('customer_tier', 'Customer Tier Pricing'),
    ]
    
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='pricing_rules')
    name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    description = models.TextField(blank=True)
    
    # Rule conditions
    min_quantity = models.IntegerField(null=True, blank=True)
    max_quantity = models.IntegerField(null=True, blank=True)
    required_options = models.JSONField(default=dict, help_text="Required option combinations")
    customer_groups = models.JSONField(default=list, help_text="Applicable customer groups")
    
    # Date range
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher priority rules are applied first")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"

class PricingTier(models.Model):
    """Pricing tiers for quantity-based pricing"""
    pricing_rule = models.ForeignKey(PricingRule, on_delete=models.CASCADE, related_name='tiers')
    min_quantity = models.IntegerField()
    max_quantity = models.IntegerField(null=True, blank=True, help_text="Leave blank for unlimited")
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    price_modifier = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_modifier_type = models.CharField(max_length=20, choices=[
        ('fixed', 'Fixed Amount'),
        ('percent', 'Percentage'),
        ('discount_percent', 'Discount Percentage')
    ], default='fixed')
    
    # Additional costs
    setup_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    shipping_modifier = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['min_quantity']
        unique_together = ['pricing_rule', 'min_quantity']
    
    def __str__(self):
        max_qty = self.max_quantity if self.max_quantity else "∞"
        return f"{self.pricing_rule.name} - {self.min_quantity}-{max_qty}"
    
    def applies_to_quantity(self, quantity):
        """Check if this tier applies to the given quantity"""
        if quantity < self.min_quantity:
            return False
        if self.max_quantity and quantity > self.max_quantity:
            return False
        return True

class Product(models.Model):
    """Enhanced products with comprehensive features"""
    PRODUCT_TYPES = [
        ('book', 'Book Printing'),
        ('business_card', 'Business Cards'),
        ('brochure', 'Brochures'),
        ('flyer', 'Flyers'),
        ('poster', 'Posters'),
        ('banner', 'Banners'),
        ('sticker', 'Stickers'),
        ('label', 'Labels'),
        ('envelope', 'Envelopes'),
        ('letterhead', 'Letterheads'),
        ('invoice', 'Invoices'),
        ('catalog', 'Catalogs'),
        ('magazine', 'Magazines'),
        ('packaging', 'Packaging'),
        ('box', 'Paper Boxes'),
        ('bag', 'Paper Bags'),
        ('calendar', 'Calendars'),
        ('notebook', 'Notebooks'),
        ('folder', 'Folders'),
        ('menu', 'Menus'),
        ('wedding', 'Wedding Cards'),
        ('invitation', 'Invitations'),
        ('certificate', 'Certificates'),
        ('id_card', 'ID Cards'),
        ('badge', 'Badges'),
        ('bookmark', 'Bookmarks'),
        ('door_hanger', 'Door Hangers'),
        ('table_tent', 'Table Tents'),
        ('yard_sign', 'Yard Signs'),
        ('vehicle_magnet', 'Vehicle Magnets'),
        ('window_cling', 'Window Clings'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    description = models.TextField()
    short_description = models.TextField(max_length=500)
    
    # Basic specifications
    base_width = models.DecimalField(max_digits=8, decimal_places=2, help_text="Base width in mm")
    base_height = models.DecimalField(max_digits=8, decimal_places=2, help_text="Base height in mm")
    unit = models.CharField(max_length=10, choices=[('mm', 'MM'), ('in', 'Inches'), ('cm', 'CM')], default='mm')
    
    # Basic pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_quantity = models.IntegerField(default=1)
    
    # Legacy pricing structure (for migration)
    pricing_structure = models.JSONField(default=dict, help_text="Legacy pricing data from Excel")
    
    # Legacy product specifications (for migration)
    size_options = models.JSONField(default=list, help_text="Legacy: Available sizes")
    paper_options = models.JSONField(default=list, help_text="Legacy: Paper types and GSM")
    print_options = models.JSONField(default=list, help_text="Legacy: Print types (B&W, Color)")
    binding_options = models.JSONField(default=list, help_text="Legacy: Binding options for books")
    finish_options = models.JSONField(default=list, help_text="Legacy: Finish options")
    
    # Design tool integration
    has_design_tool = models.BooleanField(default=True, help_text="Enable design tool for this product")
    design_tool_enabled = models.BooleanField(default=False, help_text="Legacy field - use has_design_tool")
    front_back_design_enabled = models.BooleanField(default=False, help_text="Enable front and back design options")
    design_templates = models.JSONField(default=list, help_text="Available templates", blank=True)
    custom_size_allowed = models.BooleanField(default=False)
    
    # Design specifications
    default_bleed = models.DecimalField(max_digits=5, decimal_places=2, default=3.0, help_text="Default bleed in mm")
    default_safe_zone = models.DecimalField(max_digits=5, decimal_places=2, default=2.0, help_text="Default safe zone in mm")
    
    # File upload settings
    supports_upload = models.BooleanField(default=True, help_text="Allow users to upload their own designs")
    accepted_file_formats = models.JSONField(default=list, help_text="Accepted file formats (PDF, PNG, JPG, etc.)")
    max_file_size_mb = models.IntegerField(default=50, help_text="Maximum file size in MB")
    min_resolution_dpi = models.IntegerField(default=300, help_text="Minimum resolution in DPI")
    
    # Subcategory support (legacy)
    has_subcategories = models.BooleanField(default=False, help_text="Legacy: Enable subcategories for this product")
    
    # Quantity limits
    min_quantity = models.IntegerField(default=1)
    max_quantity = models.IntegerField(null=True, blank=True)
    
    # Production and fulfillment
    STOCK_STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('made_to_order', 'Made to Order'),
    ]
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS_CHOICES, default='made_to_order')
    production_time_days = models.IntegerField(default=3, help_text="Standard production time")
    lead_time_days = models.IntegerField(default=3, help_text="Legacy field - use production_time_days")
    rush_available = models.BooleanField(default=True)
    rush_time_days = models.IntegerField(default=1, help_text="Rush production time")
    rush_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=50, help_text="Rush fee as percentage")
    
    # Marketing and display
    featured = models.BooleanField(default=False)
    bestseller = models.BooleanField(default=False)
    new_product = models.BooleanField(default=False)
    on_sale = models.BooleanField(default=False)
    
    # SEO and metadata
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    
    # Status and visibility
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-featured', '-bestseller', 'name']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['product_type', 'status']),
            models.Index(fields=['featured', 'bestseller']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Ensure unique slug
        if not self.pk:
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate product configuration"""
        super().clean()
        
        if self.front_back_design_enabled and not self.has_design_tool:
            raise ValidationError({
                'front_back_design_enabled': 'Design tool must be enabled to use front/back design feature.'
            })
        
        if self.min_quantity > (self.max_quantity or float('inf')):
            raise ValidationError({
                'max_quantity': 'Maximum quantity must be greater than minimum quantity.'
            })
    
    def get_active_variants(self):
        """Get active product variants"""
        return self.variants.filter(is_active=True).order_by('sort_order', 'name')
    
    def get_active_options(self):
        """Get active product options"""
        return self.options.prefetch_related('values').order_by('sort_order', 'name')
    
    def get_default_variant(self):
        """Get the default variant (first active variant)"""
        return self.get_active_variants().first()
    
    def get_price_range(self):
        """Get price range for this product"""
        variants = self.get_active_variants()
        if not variants:
            return {'min': self.base_price, 'max': self.base_price}
        
        prices = []
        for variant in variants:
            if variant.price_modifier_type == 'percent':
                price = self.base_price * (1 + variant.price_modifier / 100)
            else:
                price = self.base_price + variant.price_modifier
            prices.append(price)
        
        return {'min': min(prices), 'max': max(prices)}
    
    def get_effective_bleed(self):
        """Get effective bleed (product-specific or category default)"""
        return self.default_bleed if self.default_bleed else self.category.default_bleed
    
    def get_effective_safe_zone(self):
        """Get effective safe zone (product-specific or category default)"""
        return self.default_safe_zone if self.default_safe_zone else self.category.default_safe_zone
    
    def get_design_tool_config(self):
        """Get design tool configuration for this product"""
        return {
            'enabled': self.has_design_tool,
            'front_back': self.front_back_design_enabled,
            'custom_size': self.custom_size_allowed,
            'width': float(self.base_width),
            'height': float(self.base_height),
            'unit': self.unit,
            'bleed': float(self.get_effective_bleed()),
            'safe_zone': float(self.get_effective_safe_zone()),
            'dpi': self.min_resolution_dpi,
            'accepted_formats': self.accepted_file_formats or ['PDF', 'PNG', 'JPG', 'AI', 'PSD'],
            'max_file_size': self.max_file_size_mb,
        }
    
    def has_front_template(self):
        """Check if product has front templates available"""
        from apps.design_tool.models import DesignTemplate
        return DesignTemplate.objects.filter(
            category=self.category,
            side='front',
            status='active'
        ).exists()
    
    def has_back_template(self):
        """Check if product has back templates available"""
        from apps.design_tool.models import DesignTemplate
        return DesignTemplate.objects.filter(
            category=self.category,
            side='back',
            status='active'
        ).exists()
    
    def get_subcategories(self):
        """Get active subcategories for this product"""
        return self.subcategories.filter(is_active=True).order_by('sort_order')
    
    def clean(self):
        """Validate product configuration"""
        from django.core.exceptions import ValidationError
        super().clean()
        
        if self.front_back_design_enabled and not self.design_tool_enabled:
            raise ValidationError({
                'front_back_design_enabled': 'Design tool must be enabled to use front/back design feature.'
            })

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

class EnhancedPricingCalculator:
    """Enhanced pricing calculator for complex product pricing"""
    
    def __init__(self, product):
        self.product = product
    
    def calculate_price(self, variant=None, options=None, quantity=1, user=None):
        """
        Calculate comprehensive price based on product, variant, options, and quantity
        """
        options = options or {}
        
        result = {
            'base_price': Decimal('0.00'),
            'variant_modifier': Decimal('0.00'),
            'option_modifiers': Decimal('0.00'),
            'quantity_discount': Decimal('0.00'),
            'setup_fees': Decimal('0.00'),
            'rush_fee': Decimal('0.00'),
            'subtotal': Decimal('0.00'),
            'tax': Decimal('0.00'),
            'shipping': Decimal('0.00'),
            'total': Decimal('0.00'),
            'unit_price': Decimal('0.00'),
            'breakdown': [],
            'errors': [],
            'warnings': []
        }
        
        try:
            # Base price
            result['base_price'] = Decimal(str(self.product.base_price))
            result['breakdown'].append({
                'item': 'Base Price',
                'quantity': quantity,
                'unit_price': result['base_price'],
                'total': result['base_price'] * quantity,
                'type': 'base'
            })
            
            # Variant modifier
            if variant:
                variant_cost = self._calculate_variant_modifier(variant, quantity)
                result['variant_modifier'] = variant_cost
                if variant_cost != 0:
                    result['breakdown'].append({
                        'item': f'Size: {variant.name}',
                        'quantity': quantity,
                        'unit_price': variant_cost,
                        'total': variant_cost * quantity,
                        'type': 'variant'
                    })
            
            # Option modifiers
            option_costs = self._calculate_option_modifiers(options, quantity)
            result['option_modifiers'] = option_costs['total']
            result['breakdown'].extend(option_costs['breakdown'])
            
            # Calculate subtotal before discounts
            unit_before_discount = result['base_price'] + result['variant_modifier'] + result['option_modifiers']
            subtotal_before_discount = unit_before_discount * quantity
            
            # Debug: ensure we have a minimum subtotal
            if subtotal_before_discount == 0:
                subtotal_before_discount = result['base_price'] * quantity
            
            # Quantity discounts
            discount_info = self._calculate_quantity_discount(quantity, subtotal_before_discount)
            result['quantity_discount'] = discount_info['amount']
            if discount_info['amount'] > 0:
                result['breakdown'].append({
                    'item': f'Quantity Discount ({discount_info["label"]})',
                    'quantity': 1,
                    'unit_price': -discount_info['amount'],
                    'total': -discount_info['amount'],
                    'type': 'discount'
                })
            
            # Setup fees
            setup_fees = self._calculate_setup_fees(options)
            result['setup_fees'] = setup_fees['total']
            result['breakdown'].extend(setup_fees['breakdown'])
            
            # Rush fees
            if options.get('rush_delivery'):
                rush_fee = subtotal_before_discount * (self.product.rush_fee_percent / Decimal('100'))
                result['rush_fee'] = rush_fee
                result['breakdown'].append({
                    'item': f'Rush Delivery ({float(self.product.rush_fee_percent)}%)',
                    'quantity': 1,
                    'unit_price': rush_fee,
                    'total': rush_fee,
                    'type': 'fee'
                })
            
            # Calculate final totals
            result['subtotal'] = (subtotal_before_discount - result['quantity_discount'] + 
                                result['setup_fees'] + result['rush_fee'])
            
            # Tax calculation (if applicable)
            tax_rate = self._get_tax_rate(user)
            result['tax'] = result['subtotal'] * tax_rate
            if result['tax'] > 0:
                result['breakdown'].append({
                    'item': f'Tax ({float(tax_rate * 100):.1f}%)',
                    'quantity': 1,
                    'unit_price': result['tax'],
                    'total': result['tax'],
                    'type': 'tax'
                })
            
            # Shipping calculation
            result['shipping'] = self._calculate_shipping(quantity, variant, options, user)
            if result['shipping'] > 0:
                result['breakdown'].append({
                    'item': 'Shipping',
                    'quantity': 1,
                    'unit_price': result['shipping'],
                    'total': result['shipping'],
                    'type': 'shipping'
                })
            
            # Final total
            result['total'] = result['subtotal'] + result['tax'] + result['shipping']
            result['unit_price'] = result['total'] / quantity if quantity > 0 else Decimal('0.00')
            

            
        except Exception as e:
            result['errors'].append(f"Pricing calculation error: {str(e)}")
        
        return result
    
    def _calculate_variant_modifier(self, variant, quantity):
        """Calculate variant price modifier"""
        if variant.price_modifier_type == 'percent':
            return self.product.base_price * (variant.price_modifier / Decimal('100'))
        else:
            return variant.price_modifier
    
    def _calculate_option_modifiers(self, options, quantity):
        """Calculate option price modifiers"""
        result = {
            'total': Decimal('0.00'),
            'breakdown': []
        }
        
        for option_name, value_id in options.items():
            if option_name in ['rush_delivery', 'design_service']:
                continue  # These are handled separately
            
            try:
                # Handle both direct OptionValue ID and option name lookup
                if isinstance(value_id, int) or (isinstance(value_id, str) and value_id.isdigit()):
                    option_value = OptionValue.objects.get(id=int(value_id))
                else:
                    # Try to find by option name and value name
                    continue
                
                if option_value.price_modifier_type == 'percent':
                    modifier = self.product.base_price * (option_value.price_modifier / Decimal('100'))
                else:
                    modifier = option_value.price_modifier
                
                if modifier != 0:
                    result['total'] += modifier
                    result['breakdown'].append({
                        'item': f'{option_value.option.name}: {option_value.name}',
                        'quantity': quantity,
                        'unit_price': modifier,
                        'total': modifier * quantity,
                        'type': 'option'
                    })
                    
            except (OptionValue.DoesNotExist, ValueError):
                continue
        
        return result
    
    def _calculate_quantity_discount(self, quantity, subtotal):
        """Calculate quantity-based discount"""
        # Check for product-specific pricing rules
        applicable_rules = self.product.pricing_rules.filter(
            rule_type='quantity',
            is_active=True,
            min_quantity__lte=quantity
        ).order_by('-priority')
        
        for rule in applicable_rules:
            if rule.max_quantity and quantity > rule.max_quantity:
                continue
            
            # Find applicable tier
            tier = rule.tiers.filter(
                min_quantity__lte=quantity
            ).filter(
                models.Q(max_quantity__gte=quantity) | models.Q(max_quantity__isnull=True)
            ).first()
            
            if tier:
                if tier.price_modifier_type == 'discount_percent':
                    discount_amount = subtotal * (tier.price_modifier / Decimal('100'))
                    return {
                        'amount': discount_amount,
                        'label': f'{float(tier.price_modifier)}% off',
                        'rule': rule.name
                    }
        
        # Default quantity discounts (legacy)
        default_discounts = [
            {'min': 25, 'discount': 0.02, 'label': '2% off'},
            {'min': 50, 'discount': 0.04, 'label': '4% off'},
            {'min': 100, 'discount': 0.08, 'label': '8% off'},
            {'min': 200, 'discount': 0.12, 'label': '12% off'},
            {'min': 300, 'discount': 0.16, 'label': '16% off'},
        ]
        
        for tier in reversed(default_discounts):
            if quantity >= tier['min']:
                discount_amount = subtotal * Decimal(str(tier['discount']))
                return {
                    'amount': discount_amount,
                    'label': tier['label'],
                    'rule': 'Standard Quantity Discount'
                }
        
        return {'amount': Decimal('0.00'), 'label': 'No Discount', 'rule': None}
    
    def _calculate_setup_fees(self, options):
        """Calculate one-time setup fees"""
        result = {
            'total': Decimal('0.00'),
            'breakdown': []
        }
        
        # Design service fees
        if options.get('design_service'):
            design_fee = Decimal('1500.00')  # Base design fee
            result['total'] += design_fee
            result['breakdown'].append({
                'item': 'Design Service (One-time)',
                'quantity': 1,
                'unit_price': design_fee,
                'total': design_fee,
                'type': 'setup'
            })
        
        return result
    
    def _get_tax_rate(self, user):
        """Get applicable tax rate"""
        # Default GST rate for India
        return Decimal('0.18')  # 18% GST
    
    def _calculate_shipping(self, quantity, variant, options, user):
        """Calculate shipping cost"""
        # Basic shipping calculation
        base_shipping = Decimal('50.00')  # Base shipping cost
        
        # Weight-based shipping for large quantities
        if quantity > 100:
            additional_shipping = Decimal(str(quantity - 100)) * Decimal('0.50')
            return base_shipping + additional_shipping
        
        return base_shipping

# Legacy pricing calculator for backward compatibility
class PricingCalculator(models.Model):
    
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

class DesignOption(models.Model):
    """Design options configuration for products"""
    product = models.OneToOneField('Product', on_delete=models.CASCADE, related_name='design_option')
    supports_front_back = models.BooleanField(default=False, help_text="Enable front and back design options")
    template_required = models.BooleanField(default=True, help_text="Require template selection")
    accepted_formats = models.JSONField(default=list, help_text="Accepted file formats for uploads")
    max_file_size_mb = models.PositiveIntegerField(default=50, help_text="Maximum file size in MB")
    min_resolution_dpi = models.PositiveIntegerField(default=300, help_text="Minimum resolution in DPI")
    
    def __str__(self):
        return f"Design Options - {self.product.name}"
    
    def get_accepted_formats_display(self):
        """Get formatted list of accepted formats"""
        if not self.accepted_formats:
            return "PDF, PNG, JPG, AI, PSD"
        return ", ".join(self.accepted_formats).upper()

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

