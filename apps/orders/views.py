# apps/orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
import json
import razorpay
import logging
from django.views.generic import TemplateView

from .models import Cart, CartItem, Order, OrderItem, QuoteRequest
from apps.users.models import UserAddress
from apps.products.models import Product

logger = logging.getLogger(__name__)

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all().select_related('product').prefetch_related('product__images')
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    shipping_cost = Decimal('50.00') if subtotal < 1000 else Decimal('0.00')  # Free shipping above ₹1000
    gst_rate = Decimal('0.18')  # 18% GST
    gst_amount = subtotal * gst_rate
    total = subtotal + shipping_cost + gst_amount
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'gst_amount': gst_amount,
        'total': total,
    }
    
    return render(request, 'orders/cart.html', context)

@login_required
@require_http_methods(["POST"])
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity'))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        if quantity <= 0:
            cart_item.delete()
            message = 'Item removed from cart'
        else:
            cart_item.quantity = quantity
            cart_item.save()
            message = 'Cart updated successfully'
        
        # Recalculate cart totals
        cart = cart_item.cart
        cart_items = cart.items.all()
        subtotal = sum(item.total_price for item in cart_items)
        cart_count = sum(item.quantity for item in cart_items)
        
        return JsonResponse({
            'success': True,
            'message': message,
            'subtotal': str(subtotal),
            'cart_count': cart_count,
            'item_total': str(cart_item.total_price) if quantity > 0 else '0'
        })
        
    except Exception as e:
        logger.error(f"Update cart error: {e}")
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all().select_related('product')
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('orders:cart')
    
    # Get user's addresses
    addresses = UserAddress.objects.filter(user=request.user).order_by('-is_default')
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    shipping_cost = Decimal('50.00') if subtotal < 1000 else Decimal('0.00')
    gst_amount = subtotal * Decimal('0.18')
    total = subtotal + shipping_cost + gst_amount
    
    if request.method == 'POST':
        # Process checkout
        billing_address_id = request.POST.get('billing_address')
        shipping_address_id = request.POST.get('shipping_address')
        payment_method = request.POST.get('payment_method')
        
        billing_address = get_object_or_404(UserAddress, id=billing_address_id, user=request.user)
        shipping_address = get_object_or_404(UserAddress, id=shipping_address_id, user=request.user)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            gst_amount=gst_amount,
            total_amount=total,
            billing_address={
                'full_name': billing_address.full_name,
                'address_line_1': billing_address.address_line_1,
                'address_line_2': billing_address.address_line_2,
                'city': billing_address.city,
                'state': billing_address.state,
                'pincode': billing_address.pincode,
                'phone': billing_address.phone,
            },
            shipping_address={
                'full_name': shipping_address.full_name,
                'address_line_1': shipping_address.address_line_1,
                'address_line_2': shipping_address.address_line_2,
                'city': shipping_address.city,
                'state': shipping_address.state,
                'pincode': shipping_address.pincode,
                'phone': shipping_address.phone,
            }
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_options=cart_item.product_options,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                design_files=cart_item.design.design_data if cart_item.design else {}
            )
        
        # Clear cart
        cart_items.delete()
        
        # Handle payment
        if payment_method == 'razorpay':
            return redirect('orders:payment', order_id=order.id)
        elif payment_method == 'cod':
            order.payment_status = 'pending'
            order.status = 'confirmed'
            order.save()
            
            # Send confirmation email
            try:
                send_mail(
                    f'Order Confirmation - {order.order_number}',
                    render_to_string('emails/order_confirmation.txt', {'order': order}),
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Order confirmation email error: {e}")
            
            messages.success(request, f'Order {order.order_number} placed successfully!')
            return redirect('orders:order_detail', order_number=order.order_number)
    
    context = {
        'cart_items': cart_items,
        'addresses': addresses,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'gst_amount': gst_amount,
        'total': total,
    }
    
    return render(request, 'orders/checkout.html', context)

@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = order.items.all().select_related('product')
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    
    return render(request, 'orders/order_detail.html', context)

def quote_request_view(request):
    if request.method == 'POST':
        try:
            # Handle both regular form and AJAX requests
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
            
            quote_request = QuoteRequest.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone', ''),
                company=data.get('company', ''),
                product_type=data.get('product_type'),
                quantity=int(data.get('quantity')),
                specifications=data.get('specifications'),
                special_requirements=data.get('special_requirements', '')
            )
            
            # Send notification email to admin
            try:
                send_mail(
                    f'New Quote Request - {quote_request.request_number}',
                    render_to_string('emails/new_quote_request.txt', {'quote': quote_request}),
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],  # Send to admin
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Quote request email error: {e}")
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Quote request submitted successfully!',
                    'quote_number': quote_request.request_number
                })
            else:
                messages.success(request, f'Quote request {quote_request.request_number} submitted successfully!')
                return redirect('core:home')
                
        except Exception as e:
            logger.error(f"Quote request error: {e}")
            if request.content_type == 'application/json':
                return JsonResponse({'error': str(e)}, status=400)
            else:
                messages.error(request, 'Error submitting quote request. Please try again.')
                return render(request, 'quote_request.html')
    
    return render(request, 'quote_request.html')

class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_items = cart.items.all().select_related('product').prefetch_related('product__images')
        
        # Calculate totals
        subtotal = sum(item.total_price for item in cart_items)
        shipping_cost = Decimal('50.00') if subtotal < 1000 else Decimal('0.00')
        gst_rate = Decimal('0.18')
        gst_amount = subtotal * gst_rate
        total = subtotal + shipping_cost + gst_amount
        
        context.update({
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'gst_amount': gst_amount,
            'total': total,
        })
        return context

class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/checkout.html'

class OrderHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/history.html'
