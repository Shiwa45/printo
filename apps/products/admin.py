# apps/products/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import ProductCategory, Product, ProductImage

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'sort_order', 'is_active', 'products_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']
    
    def products_count(self, obj):
        return obj.product_set.count()
    products_count.short_description = 'Products'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'product_type', 'base_price', 'status', 'featured', 'bestseller', 'design_tool_enabled']
    list_filter = ['status', 'product_type', 'featured', 'bestseller', 'design_tool_enabled', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'product_type', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('base_price', 'pricing_structure')
        }),
        ('Product Options', {
            'fields': ('size_options', 'paper_options', 'print_options', 'binding_options', 'finish_options'),
            'classes': ('collapse',)
        }),
        ('Design Tool', {
            'fields': ('design_tool_enabled', 'design_templates', 'custom_size_allowed'),
            'classes': ('collapse',)
        }),
        ('Inventory', {
            'fields': ('min_quantity', 'max_quantity', 'stock_status', 'lead_time_days', 'rush_available')
        }),
        ('Marketing', {
            'fields': ('featured', 'bestseller', 'tags')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Clear cache when product is updated
        from django.core.cache import cache
        cache.delete_pattern("search_*")

