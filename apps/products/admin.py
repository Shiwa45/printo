# apps/products/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import ProductCategory, Product, ProductImage, ProductSubcategory

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

class ProductSubcategoryInline(admin.TabularInline):
    model = ProductSubcategory
    extra = 0
    fields = ['name', 'slug', 'base_price', 'is_active', 'sort_order']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'product_type', 'base_price', 'status', 'featured', 'bestseller', 'design_tool_enabled', 'front_back_design_enabled', 'has_subcategories']
    list_filter = ['status', 'product_type', 'featured', 'bestseller', 'design_tool_enabled', 'front_back_design_enabled', 'has_subcategories', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSubcategoryInline]
    
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
            'fields': ('design_tool_enabled', 'front_back_design_enabled', 'design_templates', 'custom_size_allowed', 'supports_upload'),
            'classes': ('collapse',)
        }),
        ('Product Structure', {
            'fields': ('has_subcategories',),
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
    
    class Media:
        js = ('admin/js/product_admin.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text for front_back_design_enabled
        if 'front_back_design_enabled' in form.base_fields:
            form.base_fields['front_back_design_enabled'].help_text = (
                'Enable front and back design options. Design tool must be enabled first.'
            )
        
        return form
    
    def save_model(self, request, obj, form, change):
        # Validate that design_tool_enabled is True if front_back_design_enabled is True
        if obj.front_back_design_enabled and not obj.design_tool_enabled:
            from django.contrib import messages
            messages.error(request, 'Design tool must be enabled to use front/back design feature.')
            obj.front_back_design_enabled = False
        
        super().save_model(request, obj, form, change)
        # Clear cache when product is updated
        from django.core.cache import cache
        try:
            cache.delete_pattern("search_*")
        except AttributeError:
            # delete_pattern not available in all cache backends
            pass

@admin.register(ProductSubcategory)
class ProductSubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_product', 'base_price', 'is_active', 'sort_order']
    list_filter = ['is_active', 'parent_product__category']
    search_fields = ['name', 'description', 'parent_product__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['parent_product', 'sort_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('parent_product', 'name', 'slug', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('base_price',)
        }),
        ('Specifications', {
            'fields': ('size_options', 'paper_options'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'sort_order')
        })
    )

