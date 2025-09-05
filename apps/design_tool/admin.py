# apps/design_tool/admin.py - Enhanced Admin Interface
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import DesignTemplate, UserDesign

@admin.register(DesignTemplate)
class DesignTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'template_preview', 'status', 'is_featured', 
        'usage_count', 'uploaded_by', 'upload_date'
    ]
    list_filter = [
        'status', 'is_featured', 'is_premium', 'category', 'color_mode', 'upload_date'
    ]
    search_fields = ['name', 'tags', 'category__name']
    list_editable = ['status', 'is_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'product_types', 'tags')
        }),
        ('Template Files', {
            'fields': ('template_file', 'preview_image', 'thumbnail_image'),
            'description': 'Upload SVG files for templates. Preview images will be auto-generated.'
        }),
        ('Specifications', {
            'fields': ('width', 'height', 'dpi', 'color_mode'),
            'description': 'Dimensions should be in millimeters (mm)'
        }),
        ('Settings', {
            'fields': ('is_premium', 'is_featured', 'status'),
        }),
        ('Advanced', {
            'fields': ('template_data',),
            'classes': ('collapse',),
            'description': 'Auto-generated canvas data from SVG. Edit with caution.'
        })
    )
    
    readonly_fields = ['usage_count', 'uploaded_by', 'upload_date']
    
    def template_preview(self, obj):
        if obj.preview_image:
            return format_html(
                '<img src="{}" width="60" height="40" style="border-radius: 4px;" />',
                obj.preview_image.url
            )
        return "No preview"
    template_preview.short_description = "Preview"
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new template
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Non-superuser admins can only see their own templates
            return qs.filter(uploaded_by=request.user)
        return qs
    
    actions = ['make_featured', 'make_active', 'make_inactive']
    
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = "Mark as featured"
    
    def make_active(self, request, queryset):
        queryset.update(status='active')
    make_active.short_description = "Make active"
    
    def make_inactive(self, request, queryset):
        queryset.update(status='inactive')
    make_inactive.short_description = "Make inactive"

@admin.register(UserDesign)
class UserDesignAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'product', 'design_preview', 'is_ready_for_print', 
        'is_ordered', 'order_count', 'last_modified'
    ]
    list_filter = [
        'is_ready_for_print', 'is_ordered', 'is_favorite', 'product__category', 'last_modified'
    ]
    search_fields = ['name', 'user__username', 'user__email', 'product__name']
    readonly_fields = ['design_preview_large', 'created_at', 'last_modified']
    
    fieldsets = (
        ('Design Information', {
            'fields': ('name', 'user', 'product', 'template')
        }),
        ('Preview', {
            'fields': ('design_preview_large',),
        }),
        ('Specifications', {
            'fields': ('final_width_mm', 'final_height_mm'),
        }),
        ('Status', {
            'fields': ('is_favorite', 'is_ready_for_print', 'is_ordered', 'order_count'),
        }),
        ('Technical Data', {
            'fields': ('design_data',),
            'classes': ('collapse',),
        })
    )
    
    def design_preview(self, obj):
        if obj.preview_image:
            return format_html(
                '<img src="{}" width="60" height="40" style="border-radius: 4px;" />',
                obj.preview_image.url
            )
        return "No preview"
    design_preview.short_description = "Preview"
    
    def design_preview_large(self, obj):
        if obj.preview_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />',
                obj.preview_image.url
            )
        return "No preview available"
    design_preview_large.short_description = "Design Preview"

