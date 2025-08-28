# apps/orders/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
# from apps.products.models import Product, UserDesign

class Order(models.Model):
    """Order management"""
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    guest_email = models.EmailField(blank=True)
    
    # Order status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_production', 'In Production'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Addresses (stored as JSON)
    billing_address = models.JSONField()
    shipping_address = models.JSONField()
    
    # Additional info
    notes = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        import time
        import random
        timestamp = str(int(time.time()))[-6:]
        random_num = str(random.randint(100, 999))
        return f"DP{timestamp}{random_num}"

class OrderItem(models.Model):
    """Order line items"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Product details at time of order
    product_name = models.CharField(max_length=255)
    product_options = models.JSONField(default=dict, help_text="Size, paper type, binding, etc.")
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Design files
    design_files = models.JSONField(default=list, help_text="URLs to uploaded design files")
    design_notes = models.TextField(blank=True)
    
    # Production details
    PRODUCTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_queue', 'In Queue'),
        ('printing', 'Printing'),
        ('finishing', 'Finishing'),
        ('completed', 'Completed'),
    ]
    production_status = models.CharField(max_length=20, choices=PRODUCTION_STATUS_CHOICES, default='pending')
    production_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

# UserAddress is now in apps.users.models

class Cart(models.Model):
    """Shopping cart"""
    session_id = models.CharField(max_length=255, null=True, blank=True)  # For guest users
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # For logged-in users
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if hasattr(self, 'user') and self.user:
            return f"Cart - {self.user.username}"
        return f"Cart - Session {self.session_id[:8] if self.session_id else 'Unknown'}"

class CartItem(models.Model):
    """Shopping cart items"""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    product_options = models.JSONField(default=dict, help_text="Selected size, paper, etc.")
    # design = models.ForeignKey(UserDesign, on_delete=models.SET_NULL, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart Item x {self.quantity}"
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity

class QuoteRequest(models.Model):
    """Quote requests for custom orders"""
    request_number = models.CharField(max_length=50, unique=True)
    
    # Customer info
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=255, blank=True)
    
    # Request details
    product_type = models.CharField(max_length=255)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    specifications = models.TextField()
    special_requirements = models.TextField(blank=True)
    
    # Files
    attachment_files = models.JSONField(default=list)
    
    # Status
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_review', 'In Review'),
        ('quoted', 'Quoted'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    quoted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quote_notes = models.TextField(blank=True)
    valid_until = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Quote #{self.request_number} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.request_number:
            self.request_number = self.generate_request_number()
        super().save(*args, **kwargs)
    
    def generate_request_number(self):
        import time
        import random
        timestamp = str(int(time.time()))[-6:]
        random_num = str(random.randint(100, 999))
        return f"QR{timestamp}{random_num}"

