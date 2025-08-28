# apps/core/admin.py
from django.contrib import admin
from .models import BlogPost, SiteSetting

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

