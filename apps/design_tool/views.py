# apps/design_tool/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files.base import ContentFile
import json
import base64
import logging

from .models import DesignTemplate, UserDesign
from apps.products.models import Product

logger = logging.getLogger(__name__)

def template_list_view(request):
    category = request.GET.get('category', '')
    
    templates = DesignTemplate.objects.filter(status='active')
    if category:
        templates = templates.filter(category=category)
    
    templates = templates.order_by('-is_featured', 'name')
    
    context = {
        'templates': templates,
        'categories': DesignTemplate.objects.values_list('category', flat=True).distinct()
    }
    
    return render(request, 'design_tool/templates.html', context)

@login_required
def design_editor_view(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, design_tool_enabled=True)
    
    # Get templates for this product type
    templates = DesignTemplate.objects.filter(
        status='active',
        product_types__contains=[product.category.slug]
    ).order_by('-is_featured', 'name')
    
    # Get user's saved designs for this product
    user_designs = UserDesign.objects.filter(
        user=request.user,
        product=product
    ).order_by('-last_modified')
    
    context = {
        'product': product,
        'templates': templates,
        'user_designs': user_designs,
    }
    
    return render(request, 'design_tool/editor.html', context)

@login_required
@require_http_methods(["POST"])
def save_design_view(request):
    try:
        data = json.loads(request.body)
        
        product_id = data.get('product_id')
        template_id = data.get('template_id')
        design_name = data.get('name', 'Untitled Design')
        design_data = data.get('design_data')
        preview_image_data = data.get('preview_image')  # Base64 encoded
        
        product = get_object_or_404(Product, id=product_id, design_tool_enabled=True)
        template = None
        if template_id:
            template = get_object_or_404(DesignTemplate, id=template_id)
        
        # Create or update design
        design_id = data.get('design_id')
        if design_id:
            design = get_object_or_404(UserDesign, id=design_id, user=request.user)
            design.design_data = design_data
            design.name = design_name
        else:
            design = UserDesign.objects.create(
                user=request.user,
                product=product,
                template=template,
                name=design_name,
                design_data=design_data
            )
        
        # Save preview image if provided
        if preview_image_data:
            format, imgstr = preview_image_data.split(';base64,')
            ext = format.split('/')[-1]
            preview_image = ContentFile(
                base64.b64decode(imgstr),
                name=f'design_preview_{design.id}.{ext}'
            )
            design.preview_image = preview_image
        
        design.save()
        
        return JsonResponse({
            'success': True,
            'design_id': design.id,
            'message': 'Design saved successfully!'
        })
        
    except Exception as e:
        logger.error(f"Save design error: {e}")
        return JsonResponse({'error': str(e)}, status=400)