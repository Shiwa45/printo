# apps/design_tool/views.py - Enhanced Open Source Design Tool Views
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
import json
import base64
import logging
from io import BytesIO
from PIL import Image
import uuid
from typing import Dict, List

from .models import (
    DesignTemplate, UserDesign, DesignAsset, 
    DesignHistory, StockImage, DesignShare
)
from apps.products.models import Product, ProductCategory
from apps.orders.models import Cart, CartItem
from .services.free_apis import image_search_service
from .services.renderer import design_renderer

logger = logging.getLogger(__name__)


def template_list_view(request):
    """Display all available design templates"""
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    templates = DesignTemplate.objects.filter(status='active')
    
    if category:
        templates = templates.filter(category__slug=category)
    
    if search:
        templates = templates.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__contains=[search])
        )
    
    templates = templates.order_by('-is_featured', '-usage_count', 'name')
    
    # Paginate results
    paginator = Paginator(templates, 24)  # 24 templates per page
    page = request.GET.get('page', 1)
    templates = paginator.get_page(page)
    
    # Get all categories that have templates
    categories = ProductCategory.objects.filter(
        design_templates__status='active'
    ).distinct().order_by('name')
    
    context = {
        'templates': templates,
        'categories': categories,
        'selected_category': category,
        'search': search
    }
    
    return render(request, 'design_tool/templates.html', context)


def design_editor_view(request, product_slug):
    """Enhanced design editor with Konva.js"""
    product = get_object_or_404(Product, slug=product_slug, design_tool_enabled=True)
    
    # Get templates for this product category
    templates = DesignTemplate.objects.filter(
        status='active',
        category=product.category
    ).order_by('-is_featured', '-usage_count', 'name')[:12]  # Limit for performance
    
    # Get user's saved designs if authenticated
    user_designs = []
    if request.user.is_authenticated:
        user_designs = UserDesign.objects.filter(
            user=request.user,
            product=product
        ).order_by('-last_modified')[:8]  # Show recent 8
    
    # Get canvas dimensions based on product type
    canvas_dimensions = get_canvas_dimensions_for_product(product)
    
    canvas_config = {
        'width_mm': canvas_dimensions['width'],
        'height_mm': canvas_dimensions['height'],
        'width_px': canvas_dimensions['width_px'],
        'height_px': canvas_dimensions['height_px'],
        'dpi': 300,
        'color_mode': 'CMYK',
        'bleed_mm': 3.0,
        'safe_area_mm': 5.0
    }
    
    context = {
        'product': product,
        'templates': templates,
        'user_designs': user_designs,
        'canvas_config': canvas_config,
        'canvas_config_json': json.dumps(canvas_config)
    }
    
    return render(request, 'design_tool/enhanced_editor.html', context)


def get_canvas_dimensions_for_product(product):
    """Get canvas dimensions based on product category"""
    dimensions = {
        'business-cards': {'width': 89, 'height': 54},
        'brochures': {'width': 210, 'height': 297},  # A4
        'flyers': {'width': 210, 'height': 297},     # A4
        'letter-head': {'width': 210, 'height': 297}, # A4
        'stickers': {'width': 100, 'height': 100},   # Square default
        'bill-book': {'width': 148, 'height': 210},  # A5
    }
    
    category_slug = product.category.slug if product.category else 'business-cards'
    dims = dimensions.get(category_slug, dimensions['business-cards'])
    
    # Convert mm to pixels at 300 DPI
    dpi = 300
    mm_to_px = dpi / 25.4
    
    return {
        'width': dims['width'],
        'height': dims['height'],
        'width_px': int(dims['width'] * mm_to_px),
        'height_px': int(dims['height'] * mm_to_px)
    }


# API Endpoints

@require_http_methods(["POST"])
@csrf_exempt
def save_design_api(request):
    """Enhanced save design with preview generation"""
    try:
        data = json.loads(request.body)
        
        product_id = data.get('product_id')
        design_name = data.get('name', 'Untitled Design')
        design_data = data.get('design_data')
        
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Please login to save your design',
                'login_required': True
            })
        
        product = get_object_or_404(Product, id=product_id, design_tool_enabled=True)
        
        # Create or update design
        design_id = data.get('design_id')
        if design_id:
            try:
                design = get_object_or_404(UserDesign, id=design_id, user=request.user)
                design.design_data = design_data
                design.name = design_name
            except:
                # Create new if not found
                design = UserDesign.objects.create(
                    user=request.user,
                    product=product,
                    name=design_name,
                    design_data=design_data
                )
        else:
            design = UserDesign.objects.create(
                user=request.user,
                product=product,
                name=design_name,
                design_data=design_data
            )
        
        # Generate preview using renderer service
        try:
            preview_file = design_renderer.generate_preview(design_data)
            design.preview_image.save(
                f'preview_{design.id}_{uuid.uuid4().hex[:8]}.jpg',
                preview_file,
                save=False
            )
        except Exception as e:
            logger.warning(f"Could not generate preview: {e}")
        
        design.save()
        
        # Save to history for undo/redo
        DesignHistory.objects.create(
            design=design,
            action='save_design',
            canvas_state=design_data
        )
        
        return JsonResponse({
            'success': True,
            'design_id': str(design.id),
            'message': 'Design saved successfully!',
            'preview_url': design.preview_image.url if design.preview_image else None
        })
        
    except Exception as e:
        logger.error(f"Save design error: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["POST"])
@csrf_exempt
def export_design_api(request):
    """Export design to PNG or PDF"""
    try:
        data = json.loads(request.body)
        
        design_data = data.get('design_data')
        format = data.get('format', 'png').lower()
        width_mm = float(data.get('width_mm', 89))
        height_mm = float(data.get('height_mm', 54))
        dpi = int(data.get('dpi', 300))
        
        if format == 'png':
            # Convert mm to pixels
            width_px = int(width_mm * dpi / 25.4)
            height_px = int(height_mm * dpi / 25.4)
            
            file_content = design_renderer.export_to_png(design_data, width_px, height_px, dpi)
            
            response = HttpResponse(file_content.read(), content_type='image/png')
            response['Content-Disposition'] = 'attachment; filename="design.png"'
            
        elif format == 'pdf':
            file_content = design_renderer.export_to_pdf(design_data, width_mm, height_mm, dpi)
            
            response = HttpResponse(file_content.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="design.pdf"'
        
        else:
            return JsonResponse({'success': False, 'message': 'Unsupported format'})
        
        return response
        
    except Exception as e:
        logger.error(f"Export design error: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["GET"])
def search_images_api(request):
    """Search stock images from free APIs"""
    try:
        query = request.GET.get('q', '')
        source = request.GET.get('source', 'all')  # 'all', 'unsplash', 'pixabay', 'pexels'
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        if not query:
            return JsonResponse({'success': False, 'message': 'Search query required'})
        
        if source == 'all':
            results = image_search_service.search_all_sources(query, page, per_page)
        else:
            results = image_search_service.search_single_source(source, query, page, per_page)
        
        return JsonResponse({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Image search error: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["GET"])
def search_pixabay_api(request):
    """Search Pixabay images directly"""
    try:
        query = request.GET.get('q', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 12))
        image_type = request.GET.get('image_type', 'all')
        category = request.GET.get('category', '')
        
        if not query:
            return JsonResponse({'success': False, 'message': 'Search query required'})
        
        # Build API request parameters
        import requests
        from django.conf import settings
        
        url = "https://pixabay.com/api/"
        # Use hardcoded API key for now due to settings loading issue
        api_key = getattr(settings, 'PIXABAY_API_KEY', '52058938-73b864e28b7dc377c6a8fce66')
        if not api_key:
            api_key = '52058938-73b864e28b7dc377c6a8fce66'
        
        params = {
            'key': api_key,
            'q': query,
            'safesearch': 'true',
            'page': page,
            'per_page': min(per_page, 200)
        }
        
        if image_type != 'all':
            params['image_type'] = image_type
        
        if category:
            params['category'] = category
        
        response = requests.get(url, params=params, timeout=10, verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        # Format results for frontend
        results = {
            'total': data.get('total', 0),
            'totalHits': data.get('totalHits', 0),
            'hits': []
        }
        
        for hit in data.get('hits', []):
            results['hits'].append({
                'id': hit['id'],
                'webformatURL': hit['webformatURL'],
                'largeImageURL': hit.get('largeImageURL', hit['webformatURL']),
                'tags': hit['tags'],
                'user': hit['user'],
                'user_id': hit['user_id'],
                'imageWidth': hit['imageWidth'],
                'imageHeight': hit['imageHeight'],
                'webformatWidth': hit['webformatWidth'],
                'webformatHeight': hit['webformatHeight']
            })
        
        return JsonResponse({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Pixabay search error: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["GET"])
def search_pixabay_templates_api(request):
    """Search Pixabay for design templates (vectors and illustrations)"""
    try:
        query = request.GET.get('q', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 12))
        template_type = request.GET.get('template_type', 'all')  # 'all', 'vector', 'illustration'
        category = request.GET.get('category', '')
        
        if not query:
            query = 'template design business'  # Default search for templates
        
        # Build API request parameters
        import requests
        from django.conf import settings
        
        url = "https://pixabay.com/api/"
        # Use hardcoded API key for now due to settings loading issue
        api_key = getattr(settings, 'PIXABAY_API_KEY', '52058938-73b864e28b7dc377c6a8fce66')
        if not api_key:
            api_key = '52058938-73b864e28b7dc377c6a8fce66'
        
        params = {
            'key': api_key,
            'q': query,
            'safesearch': 'true',
            'page': page,
            'per_page': min(per_page, 200),
            'order': 'popular',
            'min_width': 800,  # Ensure good quality for templates
            'min_height': 600
        }
        
        # Set image type for templates
        if template_type == 'vector':
            params['image_type'] = 'vector'
        elif template_type == 'illustration':
            params['image_type'] = 'illustration'
        else:
            params['image_type'] = 'all'
        
        # Template-friendly categories
        template_categories = [
            'backgrounds', 'business', 'computer', 'education', 
            'fashion', 'graphics', 'industry', 'science'
        ]
        
        if category and category in template_categories:
            params['category'] = category
        elif not category:
            # If no category specified, focus on business/graphics
            params['category'] = 'business'
        
        response = requests.get(url, params=params, timeout=10, verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        # Format results for frontend - filter for template-suitable images
        results = {
            'total': data.get('total', 0),
            'totalHits': data.get('totalHits', 0),
            'hits': []
        }
        
        for hit in data.get('hits', []):
            # Check if image is suitable as template (good aspect ratio, not too narrow/wide)
            width = hit['imageWidth']
            height = hit['imageHeight']
            aspect_ratio = width / height if height > 0 else 1
            
            # Filter for reasonable aspect ratios for templates
            if 0.5 <= aspect_ratio <= 2.0:
                template_data = {
                    'id': hit['id'],
                    'webformatURL': hit['webformatURL'],
                    'largeImageURL': hit.get('largeImageURL', hit['webformatURL']),
                    'tags': hit['tags'],
                    'user': hit['user'],
                    'user_id': hit['user_id'],
                    'imageWidth': width,
                    'imageHeight': height,
                    'webformatWidth': hit['webformatWidth'],
                    'webformatHeight': hit['webformatHeight'],
                    'type': hit.get('type', 'photo'),
                    'aspectRatio': round(aspect_ratio, 2),
                    'isVector': hit.get('type') == 'vector' or 'vector' in hit['tags'].lower(),
                    'previewURL': hit['previewURL']
                }
                results['hits'].append(template_data)
        
        return JsonResponse({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Pixabay template search error: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["POST"])
@csrf_exempt
def upload_asset_api(request):
    """Upload user assets (images, logos, etc.)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'})
    
    try:
        uploaded_file = request.FILES.get('file')
        asset_type = request.POST.get('type', 'image')
        
        if not uploaded_file:
            return JsonResponse({'success': False, 'message': 'No file provided'})
        
        # Validate file type
        allowed_types = {
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
            'logo': ['jpg', 'jpeg', 'png', 'svg'],
            'icon': ['png', 'svg'],
        }
        
        file_ext = uploaded_file.name.lower().split('.')[-1]
        if file_ext not in allowed_types.get(asset_type, allowed_types['image']):
            return JsonResponse({'success': False, 'message': 'Invalid file type'})
        
        # Create asset
        asset = DesignAsset.objects.create(
            user=request.user,
            name=uploaded_file.name,
            file=uploaded_file,
            asset_type=asset_type,
            file_size=uploaded_file.size
        )
        
        # Generate thumbnail for images
        if asset_type == 'image':
            try:
                img = Image.open(uploaded_file)
                asset.width, asset.height = img.size
                
                # Create thumbnail
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                thumb_buffer = BytesIO()
                img.save(thumb_buffer, format='JPEG', quality=85)
                thumb_buffer.seek(0)
                
                asset.thumbnail.save(
                    f'thumb_{asset.id}.jpg',
                    ContentFile(thumb_buffer.getvalue()),
                    save=False
                )
                
            except Exception as e:
                logger.warning(f"Could not process image: {e}")
        
        asset.save()
        
        return JsonResponse({
            'success': True,
            'asset': {
                'id': str(asset.id),
                'name': asset.name,
                'url': asset.file.url,
                'thumbnail_url': asset.thumbnail.url if asset.thumbnail else asset.file.url,
                'type': asset.asset_type,
                'width': asset.width,
                'height': asset.height
            }
        })
        
    except Exception as e:
        logger.error(f"Asset upload error: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["GET"])
def get_user_assets_api(request):
    """Get user's uploaded assets"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'})
    
    try:
        asset_type = request.GET.get('type', 'all')
        
        assets = DesignAsset.objects.filter(user=request.user)
        
        if asset_type != 'all':
            assets = assets.filter(asset_type=asset_type)
        
        assets = assets.order_by('-created_at')[:50]  # Limit for performance
        
        assets_data = []
        for asset in assets:
            assets_data.append({
                'id': str(asset.id),
                'name': asset.name,
                'url': asset.file.url,
                'thumbnail_url': asset.thumbnail.url if asset.thumbnail else asset.file.url,
                'type': asset.asset_type,
                'width': asset.width,
                'height': asset.height,
                'created_at': asset.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'assets': assets_data
        })
        
    except Exception as e:
        logger.error(f"Get user assets error: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["GET"])
def get_template_data(request, template_id):
    """Get template data for loading in editor"""
    try:
        template = get_object_or_404(DesignTemplate, id=template_id, status='active')
        
        # Increment usage count
        template.increment_usage()
        
        return JsonResponse({
            'success': True,
            'template_data': template.template_data,
            'name': template.name,
            'width_mm': template.width,
            'height_mm': template.height,
            'canvas_width': template.canvas_width_px,
            'canvas_height': template.canvas_height_px,
            'dpi': template.dpi,
            'color_mode': template.color_mode
        })
    except Exception as e:
        logger.error(f"Get template data error: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["GET"])
def get_design_data(request, design_id):
    """Get user design data for loading in editor"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'})
    
    try:
        design = get_object_or_404(UserDesign, id=design_id, user=request.user)
        return JsonResponse({
            'success': True,
            'design_data': design.design_data,
            'name': design.name,
            'design_id': str(design.id),
            'product_id': design.product.id
        })
    except Exception as e:
        logger.error(f"Get design data error: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_http_methods(["POST"])
def finalize_and_order_view(request):
    """Finalize design and proceed to order"""
    try:
        data = json.loads(request.body)
        design_id = data.get('design_id')
        quantity = int(data.get('quantity', 1))
        
        design = get_object_or_404(UserDesign, id=design_id, user=request.user)
        
        # Generate print-ready PDF
        try:
            pdf_file = design_renderer.export_to_pdf(
                design.design_data,
                design.final_width_mm or 89,
                design.final_height_mm or 54
            )
            design.print_ready_pdf.save(
                f'print_{design.id}_{uuid.uuid4().hex[:8]}.pdf',
                pdf_file,
                save=False
            )
        except Exception as e:
            logger.warning(f"Could not generate PDF: {e}")
        
        # Mark as ready for print and ordered
        design.is_ready_for_print = True
        design.is_ordered = True
        design.order_count += quantity
        design.last_ordered = timezone.now()
        design.save()
        
        # Add to cart (simplified - you may need to adjust based on your cart model)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Create cart item with design reference
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            # Add product field and custom options based on your CartItem model
            defaults={
                'quantity': quantity,
                # Add other required fields
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Design finalized and added to cart!',
            'cart_url': reverse('orders:cart'),
            'design_id': str(design.id)
        })
        
    except Exception as e:
        logger.error(f"Finalize and order error: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@staff_member_required
def admin_template_upload_view(request):
    """Admin view for bulk template upload"""
    if request.method == 'POST':
        template_files = request.FILES.getlist('template_files')
        category_id = request.POST.get('category')
        
        if not category_id:
            messages.error(request, 'Please select a category.')
            return redirect('design_tool:admin_template_upload')
        
        try:
            category = get_object_or_404(ProductCategory, id=category_id)
        except:
            messages.error(request, 'Invalid category selected.')
            return redirect('design_tool:admin_template_upload')
        
        created_count = 0
        error_count = 0
        
        for file in template_files:
            if file.name.lower().endswith(('.svg', '.json')):
                try:
                    name = file.name.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
                    
                    if DesignTemplate.objects.filter(name=name, category=category).exists():
                        logger.warning(f"Template {name} already exists, skipping")
                        continue
                    
                    # Get default dimensions for category
                    dims = get_canvas_dimensions_for_product(
                        type('MockProduct', (), {'category': category})()
                    )
                    
                    template = DesignTemplate.objects.create(
                        name=name,
                        category=category,
                        template_file=file,
                        uploaded_by=request.user,
                        width=dims['width'],
                        height=dims['height'],
                        product_types=[category.slug]
                    )
                    created_count += 1
                    
                except Exception as e:
                    logger.error(f"Error creating template {file.name}: {e}")
                    error_count += 1
            else:
                error_count += 1
        
        if created_count > 0:
            messages.success(request, f'Successfully uploaded {created_count} templates.')
        if error_count > 0:
            messages.warning(request, f'{error_count} files could not be processed.')
            
        return redirect('admin:design_tool_designtemplate_changelist')
    
    categories = ProductCategory.objects.filter(
        product__design_tool_enabled=True
    ).distinct().order_by('name')
    
    context = {
        'categories': categories,
        'title': 'Upload Design Templates'
    }
    
    return render(request, 'admin/design_tool/template_upload.html', context)


@login_required
def my_designs_view(request):
    """User's saved designs dashboard"""
    designs = UserDesign.objects.filter(user=request.user).order_by('-last_modified')
    
    # Filter options
    product_filter = request.GET.get('product')
    if product_filter:
        designs = designs.filter(product__slug=product_filter)
    
    # Pagination
    paginator = Paginator(designs, 12)
    page = request.GET.get('page', 1)
    designs = paginator.get_page(page)
    
    # Get user's products for filter
    user_products = Product.objects.filter(
        designs__user=request.user,
        design_tool_enabled=True
    ).distinct()
    
    context = {
        'designs': designs,
        'user_products': user_products,
        'selected_product': product_filter
    }
    
    return render(request, 'design_tool/my_designs.html', context)


@require_http_methods(["GET"])
def get_database_templates_api(request):
    """Get templates from database instead of Pixabay"""
    try:
        category = request.GET.get('category', '')
        search = request.GET.get('q', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 12))
        
        # Start with all active templates
        templates = DesignTemplate.objects.filter(status='active')
        
        # Filter by category if specified
        if category:
            templates = templates.filter(category__slug=category)
        
        # Filter by search term
        if search:
            templates = templates.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__contains=[search])
            )
        
        # Get total count
        total_count = templates.count()
        
        # Apply pagination
        start = (page - 1) * per_page
        end = start + per_page
        templates = templates[start:end]
        
        # Format results similar to Pixabay API
        results = {
            'total': total_count,
            'totalHits': total_count,
            'hits': []
        }
        
        for template in templates:
            # Use preview image if available, otherwise use a placeholder
            preview_url = template.preview_image.url if template.preview_image else '/static/design_tool/placeholder-template.png'
            large_url = template.template_file.url if template.template_file else preview_url
            
            results['hits'].append({
                'id': str(template.id),
                'webformatURL': preview_url,
                'largeImageURL': large_url,
                'templateFileURL': template.template_file.url if template.template_file else '',
                'tags': ', '.join(template.tags) if template.tags else template.name,
                'user': template.uploaded_by.username if template.uploaded_by else 'System',
                'user_id': template.uploaded_by.id if template.uploaded_by else 0,
                'name': template.name,
                'description': template.description,
                'category': template.category.name,
                'width': template.width,
                'height': template.height,
                'is_premium': template.is_premium,
                'is_featured': template.is_featured,
                'template_data': template.template_data,
                'imageWidth': int(template.width * 3.78),  # Convert mm to px
                'imageHeight': int(template.height * 3.78),
                'webformatWidth': int(template.width * 3.78),
                'webformatHeight': int(template.height * 3.78)
            })
        
        return JsonResponse({
            'success': True,
            'data': results,
            'source': 'database'
        })
        
    except Exception as e:
        logger.error(f"Database templates API error: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@require_http_methods(["POST"])
@csrf_exempt
def upload_template_file_api(request):
    """Upload template file from user's computer"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'})
    
    try:
        if 'template_file' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No file provided'})
        
        uploaded_file = request.FILES['template_file']
        
        # Validate file type
        allowed_extensions = ['.svg', '.json']
        file_extension = uploaded_file.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            return JsonResponse({'success': False, 'message': 'Only SVG and JSON files are allowed'})
        
        # Create a temporary template record
        template_name = request.POST.get('name', uploaded_file.name.replace(f'.{file_extension}', ''))
        
        # For now, we'll return the file data for immediate use
        file_content = uploaded_file.read()
        
        if file_extension == 'svg':
            # For SVG files, return the SVG content
            file_data = file_content.decode('utf-8')
            return JsonResponse({
                'success': True,
                'template': {
                    'name': template_name,
                    'type': 'svg',
                    'data': file_data,
                    'source': 'user_upload'
                }
            })
        elif file_extension == 'json':
            # For JSON files, parse and return the canvas data
            import json
            canvas_data = json.loads(file_content.decode('utf-8'))
            return JsonResponse({
                'success': True,
                'template': {
                    'name': template_name,
                    'type': 'json',
                    'data': canvas_data,
                    'source': 'user_upload'
                }
            })
        
    except Exception as e:
        logger.error(f"Template upload error: {e}")
        return JsonResponse({'success': False, 'message': str(e)})