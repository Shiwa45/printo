# apps/design_tool/admin.py - Enhanced Admin Interface
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DesignTemplate, UserDesign
from .forms import DesignTemplateAdminForm, BulkTemplateUploadForm

@admin.register(DesignTemplate)
class DesignTemplateAdmin(admin.ModelAdmin):
    form = DesignTemplateAdminForm
    
    list_display = [
        'name', 'category', 'template_preview', 'tags_display', 'status', 'is_featured', 
        'usage_count', 'uploaded_by', 'upload_date'
    ]
    list_filter = [
        'status', 'is_featured', 'is_premium', 'category', 'color_mode', 'upload_date'
    ]
    search_fields = ['name', 'tags', 'category__name']
    list_editable = ['status', 'is_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description'),
            'description': 'Enter basic template information'
        }),
        ('Content & Categorization', {
            'fields': ('tags', 'product_types'),
            'description': 'Add tags and select which products can use this template'
        }),
        ('Template Files', {
            'fields': ('template_file', 'preview_image', 'thumbnail_image'),
            'description': 'Upload SVG files for templates. Preview images will be auto-generated.'
        }),
        ('Specifications', {
            'fields': ('width', 'height', 'dpi', 'color_mode'),
            'description': 'Dimensions should be in millimeters (mm). Standard business card: 89×54mm'
        }),
        ('Print Settings', {
            'fields': ('bleed_mm', 'safe_area_mm', 'min_font_size'),
            'description': 'Print-ready specifications for professional output'
        }),
        ('Settings', {
            'fields': ('is_premium', 'is_featured', 'status'),
            'description': 'Template visibility and premium status'
        }),
        ('Advanced Data', {
            'fields': ('template_data',),
            'classes': ('collapse',),
            'description': 'Auto-generated canvas data from SVG. This field is read-only and managed automatically.'
        })
    )
    
    readonly_fields = ['usage_count', 'uploaded_by', 'upload_date']
    
    def tags_display(self, obj):
        """Display tags in a user-friendly way"""
        if obj.tags:
            return ', '.join(obj.tags[:3]) + ('...' if len(obj.tags) > 3 else '')
        return 'No tags'
    tags_display.short_description = "Tags"
    
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
    change_list_template = 'admin/design_tool/designtemplate/change_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='design_tool_designtemplate_bulk_upload'),
        ]
        return custom_urls + urls
    
    def bulk_upload_view(self, request):
        """Custom bulk upload view"""
        if request.method == 'POST':
            form = BulkTemplateUploadForm(request.POST, request.FILES)
            if form.is_valid():
                # Process bulk upload
                category = form.cleaned_data['category']
                files = request.FILES.getlist('template_files')
                default_width = form.cleaned_data['default_width']
                default_height = form.cleaned_data['default_height']
                is_premium = form.cleaned_data['is_premium']
                is_featured = form.cleaned_data['is_featured']
                
                created_count = 0
                errors = []
                
                for file in files:
                    try:
                        # Extract name from filename
                        name = file.name.replace('.svg', '').replace('_', ' ').replace('-', ' ').title()
                        
                        template = DesignTemplate.objects.create(
                            name=name,
                            category=category,
                            template_file=file,
                            width=default_width,
                            height=default_height,
                            is_premium=is_premium,
                            is_featured=is_featured,
                            uploaded_by=request.user,
                            product_types=[],  # Empty by default
                            tags=[]  # Empty by default
                        )
                        created_count += 1
                    except Exception as e:
                        errors.append(f"{file.name}: {str(e)}")
                
                if created_count:
                    messages.success(request, f'Successfully uploaded {created_count} templates!')
                
                if errors:
                    messages.warning(request, f'Some uploads failed: {"; ".join(errors)}')
                
                return redirect('admin:design_tool_designtemplate_changelist')
        else:
            form = BulkTemplateUploadForm()
        
        return render(request, 'admin/design_tool/bulk_upload.html', {
            'form': form,
            'title': 'Bulk Template Upload',
            'opts': self.model._meta,
        })
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        messages.success(request, f'{updated} templates marked as featured.')
    make_featured.short_description = "Mark selected templates as featured"
    
    def make_active(self, request, queryset):
        updated = queryset.update(status='active')
        messages.success(request, f'{updated} templates activated.')
    make_active.short_description = "Activate selected templates"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(status='inactive')
        messages.success(request, f'{updated} templates deactivated.')
    make_inactive.short_description = "Deactivate selected templates"

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

