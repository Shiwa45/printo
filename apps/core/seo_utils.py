# apps/core/seo_utils.py
import json
from django.conf import settings
from django.urls import reverse

class StructuredDataGenerator:
    """Generate structured data for SEO"""
    
    @staticmethod
    def get_organization_data():
        """Get organization structured data"""
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Drishthi Printing",
            "url": settings.SITE_URL if hasattr(settings, 'SITE_URL') else "https://drishthi.com",
            "logo": f"{settings.SITE_URL}/static/images/logo.png" if hasattr(settings, 'SITE_URL') else None,
            "description": "Professional printing services with custom design solutions",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Your Street Address",
                "addressLocality": "Your City",
                "addressRegion": "Your State",
                "postalCode": "Your Postal Code",
                "addressCountry": "IN"
            },
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+91-XXXXXXXXXX",
                "contactType": "customer service"
            },
            "sameAs": [
                "https://facebook.com/drishthi",
                "https://instagram.com/drishthi",
                "https://twitter.com/drishthi"
            ]
        }
    
    @staticmethod
    def get_product_data(product, request=None):
        """Get product structured data"""
        base_url = request.build_absolute_uri('/') if request else (settings.SITE_URL if hasattr(settings, 'SITE_URL') else "")
        
        data = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product.name,
            "description": product.description,
            "sku": str(product.id),
            "brand": {
                "@type": "Brand",
                "name": "Drishthi Printing"
            },
            "offers": {
                "@type": "Offer",
                "price": str(product.base_price),
                "priceCurrency": "INR",
                "availability": "https://schema.org/InStock" if product.stock_status == 'in_stock' else "https://schema.org/PreOrder",
                "seller": {
                    "@type": "Organization",
                    "name": "Drishthi Printing"
                }
            }
        }
        
        # Add image if available
        if product.images.first():
            if request:
                data["image"] = request.build_absolute_uri(product.images.first().image.url)
            else:
                data["image"] = product.images.first().image.url
        
        # Add category
        if product.category:
            data["category"] = product.category.name
        
        # Add additional properties for printing products
        data["additionalProperty"] = []
        
        if product.design_tool_enabled:
            data["additionalProperty"].append({
                "@type": "PropertyValue",
                "name": "Design Tool Available",
                "value": "Yes"
            })
        
        if product.front_back_design_enabled:
            data["additionalProperty"].append({
                "@type": "PropertyValue",
                "name": "Front & Back Design",
                "value": "Yes"
            })
        
        return data
    
    @staticmethod
    def get_blog_post_data(blog_post, request=None):
        """Get blog post structured data"""
        base_url = request.build_absolute_uri('/') if request else (settings.SITE_URL if hasattr(settings, 'SITE_URL') else "")
        
        data = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": blog_post.title,
            "description": blog_post.excerpt or blog_post.meta_description,
            "datePublished": blog_post.published_at.isoformat() if blog_post.published_at else blog_post.created_at.isoformat(),
            "dateModified": blog_post.updated_at.isoformat(),
            "author": {
                "@type": "Organization",
                "name": "Drishthi Printing"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Drishthi Printing",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{base_url}static/images/logo.png"
                }
            }
        }
        
        # Add featured image if available
        if blog_post.featured_image:
            if request:
                data["image"] = request.build_absolute_uri(blog_post.featured_image.url)
            else:
                data["image"] = blog_post.featured_image.url
        
        # Add URL
        if request:
            data["url"] = request.build_absolute_uri(reverse('blog:detail', kwargs={'slug': blog_post.slug}))
        
        return data
    
    @staticmethod
    def get_breadcrumb_data(breadcrumbs, request=None):
        """Get breadcrumb structured data"""
        if not breadcrumbs:
            return None
        
        items = []
        for i, (name, url) in enumerate(breadcrumbs, 1):
            item = {
                "@type": "ListItem",
                "position": i,
                "name": name
            }
            
            if url:
                if request and not url.startswith('http'):
                    item["item"] = request.build_absolute_uri(url)
                else:
                    item["item"] = url
            
            items.append(item)
        
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }

def generate_meta_tags(title=None, description=None, image=None, url=None, request=None):
    """Generate meta tags for SEO"""
    site_name = "Drishthi Printing"
    default_title = "Professional Printing Services | Drishthi Printing"
    default_description = "Get high-quality custom printing services with our online design tool. Business cards, books, marketing materials and more."
    
    # Build absolute URLs
    if request:
        base_url = request.build_absolute_uri('/')
        current_url = request.build_absolute_uri()
    else:
        base_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else ""
        current_url = url or base_url
    
    # Set defaults
    title = title or default_title
    description = description or default_description
    image = image or f"{base_url}static/images/og-default.jpg"
    url = url or current_url
    
    return {
        'title': title,
        'description': description,
        'image': image,
        'url': url,
        'site_name': site_name,
        'twitter_card': 'summary_large_image',
        'twitter_site': '@drishthi',  # Update with actual Twitter handle
    }