# apps/orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, QuoteRequest

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'guest_email', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'guest_email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'guest_email')
        }),
        ('Status', {
            'fields': ('status', 'payment_status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'discount_amount', 'shipping_cost', 'gst_amount', 'total_amount')
        }),
        ('Addresses', {
            'fields': ('billing_address', 'shipping_address'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'special_instructions', 'estimated_delivery'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Send status update email if status changed
        if change and 'status' in form.changed_data:
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            from django.conf import settings
            
            try:
                send_mail(
                    f'Order Status Update - {obj.order_number}',
                    render_to_string('emails/order_status_update.txt', {'order': obj}),
                    settings.DEFAULT_FROM_EMAIL,
                    [obj.guest_email],
                    fail_silently=True,
                )
            except Exception as e:
                pass

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'name', 'email', 'product_type', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'product_type', 'created_at']
    search_fields = ['request_number', 'name', 'email', 'company']
    readonly_fields = ['request_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_number', 'name', 'email', 'phone', 'company')
        }),
        ('Product Details', {
            'fields': ('product_type', 'quantity', 'specifications', 'special_requirements')
        }),
        ('Quote Details', {
            'fields': ('status', 'quoted_amount', 'quote_notes', 'valid_until')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
