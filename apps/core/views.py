# apps/core/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from apps.products.models import Product, ProductCategory
from apps.orders.models import Cart, CartItem
from apps.core.models import BlogPost, SiteSetting

class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get bestselling products (matching your current homepage)
        context['bestselling_products'] = Product.objects.filter(
            bestseller=True, 
            status='active'
        ).select_related('category').prefetch_related('images')[:4]
        
        # Get design tool products (for "No Design? No Problem" section)
        context['design_tool_products'] = Product.objects.filter(
            design_tool_enabled=True,
            status='active'
        ).select_related('category').prefetch_related('images')[:6]
        
        # Get main categories for navigation
        context['main_categories'] = ProductCategory.objects.filter(
            parent=None,
            is_active=True
        ).prefetch_related('productcategory_set').order_by('sort_order')
        
        return context

class AboutView(TemplateView):
    template_name = 'about.html'

class ContactView(TemplateView):
    template_name = 'contact.html'
    
    def post(self, request, *args, **kwargs):
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        # Here you would typically save to database or send email
        # For now, just return success
        
        return JsonResponse({'success': True, 'message': 'Thank you for your message!'})

class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/list.html'
    context_object_name = 'posts'
    paginate_by = 12
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published').order_by('-published_at')



