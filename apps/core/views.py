# apps/core/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from apps.products.models import Product, ProductCategory
from apps.orders.models import Cart, CartItem
from apps.core.models import BlogPost, SiteSetting, HeroSlide, Testimonial, ContactSubmission
from apps.core.email_utils import EmailNotificationService

class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Hero slides
        context['hero_slides'] = HeroSlide.objects.filter(is_active=True).order_by('sort_order', 'id')

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
        
        # Get testimonials for homepage
        context['testimonials'] = Testimonial.objects.filter(
            is_active=True,
            is_featured=True
        ).order_by('sort_order')[:6]
        
        return context

class AboutView(TemplateView):
    template_name = 'about.html'

class ContactView(TemplateView):
    template_name = 'contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add service options for the contact form
        context['service_options'] = [
            'Business Cards',
            'Book Printing',
            'Marketing Materials',
            'Stationery',
            'Custom Design',
            'Other'
        ]
        
        context['budget_ranges'] = [
            'Under ₹5,000',
            '₹5,000 - ₹15,000',
            '₹15,000 - ₹50,000',
            'Above ₹50,000'
        ]
        
        context['timeline_options'] = [
            'ASAP',
            'Within 1 week',
            'Within 2 weeks',
            'Within 1 month',
            'No rush'
        ]
        
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Create contact submission
            submission = ContactSubmission.objects.create(
                name=request.POST.get('name', ''),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
                company=request.POST.get('company', ''),
                subject=request.POST.get('subject', ''),
                message=request.POST.get('message', ''),
                interested_services=request.POST.getlist('services', []),
                budget_range=request.POST.get('budget_range', ''),
                timeline=request.POST.get('timeline', ''),
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referrer=request.META.get('HTTP_REFERER', '')
            )
            
            # Send email notifications
            EmailNotificationService.send_contact_notification(submission)
            EmailNotificationService.send_contact_confirmation(submission)
            
            return JsonResponse({
                'success': True, 
                'message': 'Thank you for your message! We\'ll get back to you soon.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Sorry, there was an error submitting your message. Please try again.'
            }, status=400)

class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/list.html'
    context_object_name = 'posts'
    paginate_by = 12
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published').order_by('-published_at')



