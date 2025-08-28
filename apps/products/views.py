# apps/products/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.db import models
import json
import logging

from .models import Product, ProductCategory, ProductImage, PricingCalculator
from apps.orders.models import Cart, CartItem

logger = logging.getLogger(__name__)

class ProductCategoryView(ListView):
    model = Product
    template_name = 'products/category.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            self.category = get_object_or_404(
                ProductCategory, 
                slug=category_slug
            )
            queryset = Product.objects.filter(
                category=self.category,
                status='active'
            )
        else:
            self.category = None
            queryset = Product.objects.filter(
                status='active'
            )
        
        queryset = queryset.select_related('category').prefetch_related('images').order_by('-featured', 'name')
        
        # Filter by search query if provided
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                models.Q(name__icontains=search_query) |
                models.Q(description__icontains=search_query) |
                models.Q(tags__icontains=search_query)
            )
        
        # Filter by price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        if self.category:
            context['subcategories'] = ProductCategory.objects.filter(
                parent=self.category,
                is_active=True
            ).order_by('sort_order')
        else:
            context['subcategories'] = []
        
        # Add filter options
        context['price_ranges'] = [
            {'min': 0, 'max': 500, 'label': 'Under ₹500'},
            {'min': 500, 'max': 1000, 'label': '₹500 - ₹1000'},
            {'min': 1000, 'max': 2500, 'label': '₹1000 - ₹2500'},
            {'min': 2500, 'max': None, 'label': 'Above ₹2500'}
        ]
        
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'product_slug'
    
    def get_queryset(self):
        return Product.objects.filter(
            status='active'
        ).select_related('category').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Related products
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            status='active'
        ).exclude(id=self.object.id).select_related('category').prefetch_related('images')[:4]
        
        # Check if user has this in cart
        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
            context['in_cart'] = CartItem.objects.filter(
                cart=cart, 
                product=self.object
            ).exists()
        
        return context

@csrf_exempt
@require_http_methods(["POST"])
def calculate_price(request):
    try:
        data = json.loads(request.body)
        product_type = data.get('product_type', 'book')
        
        if product_type == 'book':
            result = PricingCalculator.calculate_book_price(
                size=data.get('size', 'A4'),
                paper_type=data.get('paper_type', '75gsm'),
                print_type=data.get('print_type', 'bw_standard'),
                pages=int(data.get('pages', 100)),
                quantity=int(data.get('quantity', 50)),
                binding_type=data.get('binding_type', 'paperback_perfect'),
                include_cover_design=data.get('include_cover_design', False),
                include_isbn=data.get('include_isbn', False),
                include_design_support=data.get('include_design_support', False)
            )
        elif product_type == 'standard':
            # Handle standard products (business cards, etc.)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            customizations = data.get('customizations', {})
            
            product = get_object_or_404(Product, id=product_id)
            
            base_cost = product.base_price * quantity
            total_cost = base_cost
            
            breakdown = [{
                'item': f'{product.name} ({quantity} units × ₹{product.base_price})',
                'cost': base_cost
            }]
            
            # Add customization costs
            if customizations.get('rush_delivery'):
                rush_cost = base_cost * 0.2
                breakdown.append({
                    'item': 'Rush Delivery (24hrs)',
                    'cost': rush_cost
                })
                total_cost += rush_cost
                
            if customizations.get('premium_paper'):
                premium_cost = base_cost * 0.15
                breakdown.append({
                    'item': 'Premium Paper',
                    'cost': premium_cost
                })
                total_cost += premium_cost
            
            result = {
                'breakdown': breakdown,
                'subtotal': total_cost,
                'discount': 0,
                'total': total_cost,
                'per_unit': total_cost / quantity,
                'errors': []
            }
        else:
            result = {'errors': ['Product type not supported']}
        
        # Convert Decimal to string for JSON serialization
        if 'breakdown' in result:
            for item in result['breakdown']:
                item['cost'] = str(item['cost'])
        for key in ['subtotal', 'discount', 'total', 'per_unit', 'per_book']:
            if key in result:
                result[key] = str(result[key])
        
        return JsonResponse(result)
    
    except Exception as e:
        logger.error(f"Price calculation error: {e}")
        return JsonResponse({'errors': [str(e)]}, status=400)

@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        product_options = data.get('options', {})
        design_id = data.get('design_id')
        
        product = get_object_or_404(Product, id=product_id, status='active')
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if item already exists in cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            product_options=product_options,
            defaults={
                'quantity': quantity,
                'unit_price': product.base_price,
                'design_id': design_id if design_id else None
            }
        )
        
        if not item_created:
            # Update existing item
            cart_item.quantity += quantity
            cart_item.save()
        
        # Get cart total for response
        cart_total = sum(item.total_price for item in cart.items.all())
        cart_count = sum(item.quantity for item in cart.items.all())
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_total': str(cart_total),
            'cart_count': cart_count
        })
        
    except Exception as e:
        logger.error(f"Add to cart error: {e}")
        return JsonResponse({'error': str(e)}, status=400)

def search_products(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category')
    
    if len(query) < 3:
        return JsonResponse({'results': []})
    
    # Cache search results for 5 minutes
    cache_key = f"search_{query}_{category_slug}"
    cached_results = cache.get(cache_key)
    
    if cached_results:
        return JsonResponse({'results': cached_results})
    
    queryset = Product.objects.filter(
        status='active',
        name__icontains=query
    ).select_related('category')[:10]
    
    if category_slug:
        category = get_object_or_404(ProductCategory, slug=category_slug)
        queryset = queryset.filter(category=category)
    
    results = []
    for product in queryset:
        results.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'category': product.category.name,
            'price': str(product.base_price),
            'image': product.images.first().image.url if product.images.first() else None,
            'url': f'/products/category/{product.category.slug}/{product.slug}/'
        })
    
    cache.set(cache_key, results, 300)  # Cache for 5 minutes
    return JsonResponse({'results': results})
