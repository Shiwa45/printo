# apps/core/templatetags/seo_tags.py
import json
from django import template
from django.utils.safestring import mark_safe
from apps.core.seo_utils import StructuredDataGenerator, generate_meta_tags

register = template.Library()

@register.simple_tag(takes_context=True)
def structured_data(context, data_type, obj=None):
    """Generate structured data JSON-LD"""
    request = context.get('request')
    
    if data_type == 'organization':
        data = StructuredDataGenerator.get_organization_data()
    elif data_type == 'product' and obj:
        data = StructuredDataGenerator.get_product_data(obj, request)
    elif data_type == 'blog_post' and obj:
        data = StructuredDataGenerator.get_blog_post_data(obj, request)
    elif data_type == 'breadcrumb' and obj:
        data = StructuredDataGenerator.get_breadcrumb_data(obj, request)
    else:
        return ''
    
    if data:
        return mark_safe(f'<script type="application/ld+json">{json.dumps(data, indent=2)}</script>')
    return ''

@register.inclusion_tag('core/meta_tags.html', takes_context=True)
def meta_tags(context, title=None, description=None, image=None, url=None):
    """Generate meta tags for SEO"""
    request = context.get('request')
    meta_data = generate_meta_tags(title, description, image, url, request)
    return {'meta': meta_data}

@register.simple_tag
def canonical_url(url, request=None):
    """Generate canonical URL"""
    if request and not url.startswith('http'):
        return request.build_absolute_uri(url)
    return url

@register.filter
def truncate_description(text, length=160):
    """Truncate text for meta descriptions"""
    if not text:
        return ''
    
    if len(text) <= length:
        return text
    
    # Find the last space before the limit
    truncated = text[:length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + '...'