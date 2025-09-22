# apps/products/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
import json
from .models import Product, ProductVariant, ProductCategory, EnhancedPricingCalculator
from .services import PricingService

@csrf_exempt
@require_http_methods(["POST"])
def calculate_product_price(request):
    """
    API endpoint to calculate product pricing
    """
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        options = data.get('options', {})
        quantity = int(data.get('quantity', 1))
        
        # Get product
        product = get_object_or_404(Product, id=product_id, status='active')
        
        # Get variant if specified
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product, is_active=True)
        
        # Calculate pricing
        calculator = EnhancedPricingCalculator(product)
        pricing_result = calculator.calculate_price(
            variant=variant,
            options=options,
            quantity=quantity,
            user=request.user if request.user.is_authenticated else None
        )
        
        # Format response
        response_data = {
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'base_price': float(product.base_price)
            },
            'variant': {
                'id': variant.id,
                'name': variant.name,
                'dimensions': variant.get_dimensions_display()
            } if variant else None,
            'quantity': quantity,
            'pricing': {
                'base_price': float(pricing_result['base_price']),
                'variant_modifier': float(pricing_result['variant_modifier']),
                'option_modifiers': float(pricing_result['option_modifiers']),
                'quantity_discount': float(pricing_result['quantity_discount']),
                'setup_fees': float(pricing_result['setup_fees']),
                'rush_fee': float(pricing_result['rush_fee']),
                'subtotal': float(pricing_result['subtotal']),
                'tax': float(pricing_result['tax']),
                'shipping': float(pricing_result['shipping']),
                'total': float(pricing_result['total']),
                'unit_price': float(pricing_result['unit_price']),
                'breakdown': [
                    {
                        'item': item['item'],
                        'quantity': item['quantity'],
                        'unit_price': float(item['unit_price']),
                        'total': float(item['total']),
                        'type': item['type']
                    }
                    for item in pricing_result['breakdown']
                ]
            },
            'errors': pricing_result['errors'],
            'warnings': pricing_result['warnings']
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_product_details(request, product_id):
    """
    Get detailed product information including variants and options
    """
    try:
        product = get_object_or_404(Product, id=product_id, status='active')
        
        # Get variants
        variants = []
        for variant in product.get_active_variants():
            variants.append({
                'id': variant.id,
                'name': variant.name,
                'sku': variant.sku,
                'dimensions': variant.get_dimensions_display(),
                'price_modifier': float(variant.price_modifier),
                'price_modifier_type': variant.price_modifier_type
            })
        
        # Get options
        options = []
        for option in product.get_active_options():
            option_values = []
            for value in option.values.filter(is_active=True).order_by('sort_order', 'name'):
                option_values.append({
                    'id': value.id,
                    'name': value.name,
                    'description': value.description,
                    'price_display': value.get_price_display(),
                    'price_modifier': float(value.price_modifier),
                    'price_modifier_type': value.price_modifier_type,
                    'is_default': value.is_default,
                    'specifications': value.specifications,
                    'image_url': value.image.url if value.image else None,
                    'color_code': value.color_code
                })
            
            options.append({
                'id': option.id,
                'name': option.name,
                'option_type': option.option_type,
                'description': option.description,
                'is_required': option.is_required,
                'display_as_grid': option.display_as_grid,
                'show_images': option.show_images,
                'values': option_values
            })
        
        # Get design tool configuration
        design_config = product.get_design_tool_config()
        
        response_data = {
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'description': product.description,
                'short_description': product.short_description,
                'base_price': float(product.base_price),
                'minimum_quantity': product.minimum_quantity,
                'price_range': {
                    'min': float(product.get_price_range()['min']),
                    'max': float(product.get_price_range()['max'])
                },
                'design_tool_config': design_config,
                'production_time_days': product.production_time_days,
                'rush_available': product.rush_available,
                'rush_time_days': product.rush_time_days,
                'rush_fee_percent': float(product.rush_fee_percent)
            },
            'variants': variants,
            'options': options
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
@csrf_exempt
@require_http_methods(["POST"])
def calculate_advanced_pricing(request):
    """
    Advanced pricing calculation API using the PricingService
    """
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        # Get product
        product = get_object_or_404(Product, id=product_id, status='active')
        
        # Prepare configuration
        configuration = {
            'variant_id': data.get('variant_id'),
            'options': data.get('options', {}),
            'quantity': int(data.get('quantity', 1)),
            'user_id': request.user.id if request.user.is_authenticated else None,
            'country_code': data.get('country_code', 'IN'),
            'rush_delivery': data.get('rush_delivery', False),
            'design_service': data.get('design_service', False),
            'existing_design_id': data.get('existing_design_id')
        }
        
        # Calculate pricing using the service
        pricing_service = PricingService()
        result = pricing_service.calculate_comprehensive_price(product, configuration)
        
        # Convert Decimal values to float for JSON serialization
        def convert_decimals(obj):
            if isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            elif hasattr(obj, '__dict__'):
                return convert_decimals(obj.__dict__)
            elif str(type(obj)) == "<class 'decimal.Decimal'>":
                return float(obj)
            else:
                return obj
        
        result = convert_decimals(result)
        result['success'] = True
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_price_breaks(request, product_id):
    """
    Get quantity price breaks for a product
    """
    try:
        product = get_object_or_404(Product, id=product_id, status='active')
        
        variant_id = request.GET.get('variant_id')
        options = {}
        
        # Parse options from query parameters
        for key, value in request.GET.items():
            if key.startswith('option_'):
                option_name = key.replace('option_', '')
                try:
                    options[option_name] = int(value)
                except ValueError:
                    continue
        
        pricing_service = PricingService()
        price_breaks = pricing_service.get_quantity_price_breaks(
            product, 
            variant_id=int(variant_id) if variant_id else None,
            options=options
        )
        
        return JsonResponse({
            'success': True,
            'product_id': product.id,
            'product_name': product.name,
            'price_breaks': price_breaks
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def validate_product_configuration(request):
    """
    Validate a product configuration
    """
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        product = get_object_or_404(Product, id=product_id, status='active')
        
        configuration = {
            'variant_id': data.get('variant_id'),
            'options': data.get('options', {}),
            'quantity': int(data.get('quantity', 1)),
        }
        
        pricing_service = PricingService()
        validation_result = pricing_service.validate_configuration(product, configuration)
        
        return JsonResponse({
            'success': True,
            'valid': len(validation_result['errors']) == 0,
            'errors': validation_result['errors'],
            'warnings': validation_result['warnings']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_product_catalog(request):
    """
    Get paginated product catalog with filtering
    """
    try:
        # Get query parameters
        category_id = request.GET.get('category')
        product_type = request.GET.get('type')
        search = request.GET.get('search')
        featured = request.GET.get('featured')
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 12)), 50)  # Max 50 per page
        
        # Build query
        queryset = Product.objects.filter(status='active').select_related('category')
        
        if category_id:
            try:
                category = ProductCategory.objects.get(id=category_id)
                # Include products from subcategories
                category_ids = [category.id]
                for child in category.get_active_children():
                    category_ids.append(child.id)
                queryset = queryset.filter(category_id__in=category_ids)
            except ProductCategory.DoesNotExist:
                pass
        
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(short_description__icontains=search)
            )
        
        if featured == 'true':
            queryset = queryset.filter(featured=True)
        
        # Order by featured, bestseller, then name
        queryset = queryset.order_by('-featured', '-bestseller', 'name')
        
        # Paginate
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize products
        products = []
        for product in page_obj:
            price_range = product.get_price_range()
            
            products.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'short_description': product.short_description,
                'category': {
                    'id': product.category.id,
                    'name': product.category.name,
                    'slug': product.category.slug
                },
                'product_type': product.product_type,
                'price_range': {
                    'min': float(price_range['min']),
                    'max': float(price_range['max'])
                },
                'minimum_quantity': product.minimum_quantity,
                'featured': product.featured,
                'bestseller': product.bestseller,
                'new_product': product.new_product,
                'on_sale': product.on_sale,
                'has_design_tool': product.has_design_tool,
                'production_time_days': product.production_time_days,
                'rush_available': product.rush_available,
                'images': [
                    {
                        'url': img.image.url,
                        'alt_text': img.alt_text,
                        'is_primary': img.is_primary
                    }
                    for img in product.images.all()[:3]  # Limit to 3 images
                ]
            })
        
        return JsonResponse({
            'success': True,
            'products': products,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_products': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'per_page': per_page
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_categories(request):
    """
    Get product categories with hierarchy
    """
    try:
        categories = []
        
        # Get top-level categories
        top_categories = ProductCategory.objects.filter(
            parent__isnull=True, 
            is_active=True
        ).order_by('sort_order', 'name')
        
        for category in top_categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'icon': category.icon,
                'image_url': category.image.url if category.image else None,
                'featured': category.featured,
                'product_count': category.products.filter(status='active').count(),
                'children': []
            }
            
            # Get child categories
            for child in category.get_active_children():
                category_data['children'].append({
                    'id': child.id,
                    'name': child.name,
                    'slug': child.slug,
                    'description': child.description,
                    'product_count': child.products.filter(status='active').count()
                })
            
            categories.append(category_data)
        
        return JsonResponse({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["GET"])
def enhanced_product_detail(request, product_slug):
    """
    Enhanced product detail page with visual configuration
    """
    try:
        product = get_object_or_404(
            Product.objects.select_related('category').prefetch_related(
                'images', 'variants', 'options__values'
            ), 
            slug=product_slug, 
            status='active'
        )
        
        context = {
            'product': product,
        }
        
        return render(request, 'products/enhanced_product_detail.html', context)
        
    except Exception as e:
        return render(request, '404.html', status=404)

@require_http_methods(["GET"])
def product_catalog_page(request):
    """
    Product catalog page with enhanced filtering and search
    """
    return render(request, 'products/catalog.html')

@require_http_methods(["GET"])
def product_comparison_page(request):
    """
    Product comparison page
    """
    return render(request, 'products/comparison.html')