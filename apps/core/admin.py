# apps/core/admin.py
from django.contrib import admin
from .models import BlogPost, SiteSetting, HeroSlide, Testimonial, ContactSubmission

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'published_at', 'created_at']
    list_filter = ['status', 'published_at', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'tags'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('status', 'published_at')
        })
    )

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['setting_key', 'description', 'updated_at']
    search_fields = ['setting_key', 'description']
    readonly_fields = ['updated_at']


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'sort_order', 'updated_at']
    list_editable = ['is_active', 'sort_order']
    list_filter = ['is_active']
    search_fields = ['title', 'subtitle', 'description']
    fieldsets = (
        ('Texts', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Background', {
            'fields': ('background_gradient_from', 'background_gradient_via', 'background_gradient_to')
        }),
        ('CTAs', {
            'fields': ('primary_cta_text', 'primary_cta_url', 'secondary_cta_text', 'secondary_cta_url')
        }),
        ('Meta', {
            'fields': ('is_active', 'sort_order', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'rating', 'product_name', 'is_featured', 'is_active', 'created_at']
    list_editable = ['is_featured', 'is_active']
    list_filter = ['rating', 'is_featured', 'is_active', 'service_type']
    search_fields = ['customer_name', 'customer_title', 'review_text', 'product_name']
    ordering = ['-is_featured', 'sort_order', '-created_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_title', 'customer_photo')
        }),
        ('Review', {
            'fields': ('review_text', 'rating', 'product_name', 'service_type')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_active', 'sort_order')
        }),
        ('Metadata', {
            'fields': ('submitted_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['submitted_date', 'created_at', 'updated_at']

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_editable = ['status']
    list_filter = ['status', 'created_at', 'budget_range', 'timeline']
    search_fields = ['name', 'email', 'company', 'subject', 'message']
    readonly_fields = ['ip_address', 'user_agent', 'referrer', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'company')
        }),
        ('Inquiry Details', {
            'fields': ('subject', 'message', 'interested_services', 'budget_range', 'timeline')
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes')
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent', 'referrer'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion of contact submissions
        return request.user.is_superuser
