# apps/products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.db import models
from django.urls import reverse
import json
import logging

from .models import Product, ProductCategory, ProductImage, PricingCalculator, DesignOption
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
    """Redirect product detail pages to service URLs"""
    model = Product
    slug_field = 'slug'
    slug_url_kwarg = 'product_slug'
    
    def get_queryset(self):
        return Product.objects.filter(
            status='active'
        ).select_related('category')
    
    def get(self, request, *args, **kwargs):
        """Redirect to the corresponding service URL"""
        product = self.get_object()
        
        # Map product categories to service sections or specific services
        category_slug = product.category.slug.lower() if product.category else ''
        product_slug = product.slug.lower()
        
        # Direct service mappings for specific products
        direct_service_mapping = {
            'business-cards': 'business_cards',
            'letterhead': 'letter_head',
            'letterheads': 'letter_head',
            'letter-head': 'letter_head',
            'brochures': 'brochures',
            'brochure': 'brochures',
            'flyers': 'flyers',
            'flyer': 'flyers',
            'posters': 'poster',
            'poster': 'poster',
            'stickers': 'sticker',
            'sticker': 'sticker',
            'envelopes': 'envelopes',
            'envelope': 'envelopes',
            'notebooks': 'notebooks',
            'folders': 'folders',
            'calendars': 'calendars',
            'invitations': 'invitations',
            'id-cards': 'id_cards',
            'bill-books': 'bill_book',
            'document-printing': 'document_printing'
        }
        
        # Check for direct service mapping first
        service_name = direct_service_mapping.get(product_slug) or direct_service_mapping.get(category_slug)
        
        if service_name:
            try:
                return redirect('services:' + service_name)
            except:
                pass
        
        # For book printing products, redirect to services directory with book section
        if 'book' in category_slug or 'book' in product_slug:
            return redirect('services:services_directory')
        
        # Fallback to services directory
        return redirect('services:services_directory')
    
    def get_context_data(self, **kwargs):
        # This won't be used since we're redirecting
        return super().get_context_data(**kwargs)

class EnhancedProductDetailView(DetailView):
    """Redirect enhanced product detail pages to service URLs"""
    model = Product
    slug_field = 'slug'
    slug_url_kwarg = 'product_slug'
    
    def get_queryset(self):
        return Product.objects.filter(
            status='active'
        ).select_related('category')
    
    def get(self, request, *args, **kwargs):
        """Redirect to the corresponding service URL"""
        product = self.get_object()
        
        # Map product categories to service sections or specific services
        category_slug = product.category.slug.lower() if product.category else ''
        product_slug = product.slug.lower()
        
        # Direct service mappings for specific products
        direct_service_mapping = {
            'business-cards': 'business_cards',
            'letterhead': 'letter_head',
            'letterheads': 'letter_head',
            'letter-head': 'letter_head',
            'brochures': 'brochures',
            'brochure': 'brochures',
            'flyers': 'flyers',
            'flyer': 'flyers',
            'posters': 'poster',
            'poster': 'poster',
            'stickers': 'sticker',
            'sticker': 'sticker',
            'envelopes': 'envelopes',
            'envelope': 'envelopes',
            'notebooks': 'notebooks',
            'folders': 'folders',
            'calendars': 'calendars',
            'invitations': 'invitations',
            'id-cards': 'id_cards',
            'bill-books': 'bill_book',
            'document-printing': 'document_printing'
        }
        
        # Check for direct service mapping first
        service_name = direct_service_mapping.get(product_slug) or direct_service_mapping.get(category_slug)
        
        if service_name:
            try:
                return redirect('services:' + service_name)
            except:
                pass
        
        # For book printing products, redirect to services directory with book section
        if 'book' in category_slug or 'book' in product_slug:
            return redirect('services:services_directory')
        
        # Fallback to services directory
        return redirect('services:services_directory')
    
    def get_context_data(self, **kwargs):
        # This won't be used since we're redirecting
        return super().get_context_data(**kwargs)

class ProductsHomeView(ListView):
    model = Product
    template_name = 'products/products_home.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(
            status='active'
        ).select_related('category').prefetch_related('images').order_by('-featured', '-bestseller', 'name')
        
        # Filter by search query if provided
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                models.Q(name__icontains=search_query) |
                models.Q(description__icontains=search_query) |
                models.Q(tags__icontains=search_query)
            )
        
        # Filter by category
        category_filter = self.request.GET.get('category')
        if category_filter:
            categories = category_filter.split(',')
            queryset = queryset.filter(category__slug__in=categories)
        
        # Filter by price range
        price_filter = self.request.GET.get('price')
        if price_filter:
            price_ranges = price_filter.split(',')
            for price_range in price_ranges:
                if price_range == '0-500':
                    queryset = queryset.filter(base_price__lte=500)
                elif price_range == '500-1000':
                    queryset = queryset.filter(base_price__gte=500, base_price__lte=1000)
                elif price_range == '1000-2500':
                    queryset = queryset.filter(base_price__gte=1000, base_price__lte=2500)
                elif price_range == '2500-':
                    queryset = queryset.filter(base_price__gte=2500)
        
        # Filter by features
        features_filter = self.request.GET.get('features')
        if features_filter:
            features = features_filter.split(',')
            for feature in features:
                if feature == 'design_tool':
                    queryset = queryset.filter(design_tool_enabled=True)
                elif feature == 'front_back':
                    queryset = queryset.filter(front_back_design_enabled=True)
                elif feature == 'rush_delivery':
                    queryset = queryset.filter(rush_available=True)
        
        # Sort products
        sort_by = self.request.GET.get('sort', 'name')
        if sort_by == 'price_low':
            queryset = queryset.order_by('base_price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-base_price')
        elif sort_by == 'featured':
            queryset = queryset.order_by('-featured', '-bestseller', 'name')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all categories
        context['categories'] = ProductCategory.objects.filter(
            is_active=True
        ).annotate(
            product_count=models.Count('product', filter=models.Q(product__status='active'))
        ).order_by('sort_order', 'name')
        
        # Get featured products
        context['featured_products'] = Product.objects.filter(
            status='active',
            featured=True
        ).select_related('category').prefetch_related('images')[:8]
        
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
            subcategory_id = data.get('subcategory_id')
            quantity = int(data.get('quantity', 1))
            customizations = data.get('customizations', {})
            
            product = get_object_or_404(Product, id=product_id)
            
            # Use subcategory price if specified, otherwise use product base price
            if subcategory_id:
                from .models import ProductSubcategory
                subcategory = get_object_or_404(ProductSubcategory, id=subcategory_id, parent_product=product)
                base_price = subcategory.base_price
                item_name = f'{product.name} - {subcategory.name}'
            else:
                base_price = product.base_price
                item_name = product.name
            
            base_cost = base_price * quantity
            total_cost = base_cost
            
            breakdown = [{
                'item': f'{item_name} ({quantity} units × ₹{base_price})',
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
            
            # Apply quantity discounts
            discount_info = PricingCalculator.get_quantity_discount(quantity)
            discount_amount = 0
            if discount_info['percentage'] > 0:
                discount_amount = total_cost * discount_info['percentage']
                breakdown.append({
                    'item': f'Quantity Discount ({quantity} units - {discount_info["label"]})',
                    'cost': -discount_amount
                })
                total_cost -= discount_amount
            
            result = {
                'breakdown': breakdown,
                'subtotal': base_cost,
                'discount': discount_amount,
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

@require_http_methods(["GET"])
def get_product_design_options(request, product_id):
    """Get design options for a specific product"""
    try:
        product = get_object_or_404(Product, id=product_id, status='active')
        
        # Get or create design options
        design_option, created = DesignOption.objects.get_or_create(
            product=product,
            defaults={
                'supports_front_back': product.front_back_design_enabled,
                'accepted_formats': ['pdf', 'png', 'jpg', 'ai', 'psd'],
                'max_file_size_mb': 50,
                'min_resolution_dpi': 300
            }
        )
        
        return JsonResponse({
            'product_id': product.id,
            'product_name': product.name,
            'design_tool_enabled': product.design_tool_enabled,
            'front_back_design_enabled': product.front_back_design_enabled,
            'supports_upload': product.supports_upload,
            'supports_front_back': design_option.supports_front_back,
            'accepted_formats': design_option.accepted_formats,
            'max_file_size_mb': design_option.max_file_size_mb,
            'min_resolution_dpi': design_option.min_resolution_dpi,
            'has_templates': product.has_front_template() or product.has_back_template()
        })
        
    except Exception as e:
        logger.error(f"Error getting design options: {e}")
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
