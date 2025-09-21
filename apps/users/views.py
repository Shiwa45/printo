
# apps/users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import json

from .models import User, UserAddress
from .forms import UserRegistrationForm, UserProfileForm, AddressForm
from apps.design_tool.models import UserDesign

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'users/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            
            # Send welcome email
            try:
                send_mail(
                    'Welcome to Drishthi Printing',
                    render_to_string('emails/welcome.txt', {'user': user}),
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Welcome email error: {e}")
            
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Get user's addresses
    addresses = UserAddress.objects.filter(user=request.user).order_by('-is_default', 'id')
    
    # Get user's recent orders
    from apps.orders.models import Order
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'form': form,
        'addresses': addresses,
        'recent_orders': recent_orders
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def add_address_view(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is set as default, unset others
            if address.is_default:
                UserAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('users:profile')
    else:
        form = AddressForm()
    
    return render(request, 'users/add_address.html', {'form': form})

class LoginView(TemplateView):
    template_name = 'users/login.html'
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
            return self.get(request)

class RegisterView(TemplateView):
    template_name = 'users/register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = UserRegistrationForm()
        return context
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            
            # Send welcome email
            try:
                send_mail(
                    'Welcome to Drishthi Printing',
                    render_to_string('emails/welcome.txt', {'user': user}),
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except Exception as e:
                pass  # logger not imported in class context
            
            return redirect('users:login')
        
        return self.render_to_response(self.get_context_data(form=form))

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = UserProfileForm(instance=self.request.user)
        
        # Get user's addresses
        context['addresses'] = UserAddress.objects.filter(user=self.request.user).order_by('-is_default', 'id')
        
        # Get user's recent orders
        from apps.orders.models import Order
        context['recent_orders'] = Order.objects.filter(user=self.request.user).order_by('-created_at')[:5]
        
        # Get user's designs
        context['my_designs'] = UserDesign.objects.filter(user=self.request.user).order_by('-last_modified')[:8]
        
        return context
    
    def post(self, request):
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
        
        return self.render_to_response(self.get_context_data(form=form))

class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('home:home')
