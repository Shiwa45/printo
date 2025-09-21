# apps/core/models.py - Blog and Settings
from django.db import models

class BlogPost(models.Model):
    """Blog posts"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    
    featured_image = models.ImageField(upload_to='blog/', blank=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title

class SiteSetting(models.Model):
    """System settings"""
    setting_key = models.CharField(max_length=100, unique=True)
    setting_value = models.JSONField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.setting_key


class HeroSlide(models.Model):
    """Admin-managed hero slider entries for homepage"""
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='hero_slides/', blank=True)
    background_gradient_from = models.CharField(max_length=50, default='from-gray-100')
    background_gradient_via = models.CharField(max_length=50, default='via-gray-200')
    background_gradient_to = models.CharField(max_length=50, default='to-gray-300')
    primary_cta_text = models.CharField(max_length=50, blank=True)
    primary_cta_url = models.CharField(max_length=255, blank=True)
    secondary_cta_text = models.CharField(max_length=50, blank=True)
    secondary_cta_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    """Customer testimonials"""
    customer_name = models.CharField(max_length=100)
    customer_title = models.CharField(max_length=100, blank=True, help_text="Job title or company")
    customer_photo = models.ImageField(upload_to='testimonials/', blank=True)
    review_text = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    
    # Product/service reviewed
    product_name = models.CharField(max_length=100, blank=True)
    service_type = models.CharField(max_length=50, blank=True)
    
    # Display settings
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    # Metadata
    submitted_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', 'sort_order', '-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars"
    
    def get_star_range(self):
        """Get range for template star display"""
        return range(self.rating)
    
    def get_empty_star_range(self):
        """Get range for empty stars"""
        return range(5 - self.rating)

class ContactSubmission(models.Model):
    """Contact form submissions"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Additional fields
    interested_services = models.JSONField(default=list, blank=True, help_text="Services they're interested in")
    budget_range = models.CharField(max_length=50, blank=True)
    timeline = models.CharField(max_length=50, blank=True)
    
    # Status tracking
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('quoted', 'Quoted'),
        ('converted', 'Converted'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"