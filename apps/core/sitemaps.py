# apps/core/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.products.models import Product, ProductCategory
from apps.core.models import BlogPost

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['home:home', 'home:about', 'home:contact', 'products:home']

    def location(self, item):
        return reverse(item)

class ProductCategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return ProductCategory.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None

    def location(self, obj):
        return reverse('products:category', kwargs={'category_slug': obj.slug})

class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Product.objects.filter(status='active').select_related('category')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('products:detail', kwargs={
            'category_slug': obj.category.slug,
            'product_slug': obj.slug
        })

class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog:detail', kwargs={'slug': obj.slug})