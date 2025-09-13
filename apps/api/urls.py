# apps/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import viewsets from different apps
from apps.products.api import ProductViewSet, CategoryViewSet
from apps.orders.api import CartViewSet, OrderViewSet
from apps.design_tool.api import TemplateViewSet, UserDesignViewSet
from .views import auth_views, core_views

# Create router and register viewsets
router = DefaultRouter()

# Products API
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

# Orders API
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

# Design Tool API
router.register(r'design/templates', TemplateViewSet, basename='template')
router.register(r'design/user-designs', UserDesignViewSet, basename='userdesign')

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/', include([
        path('login/', auth_views.LoginAPIView.as_view(), name='login'),
        path('register/', auth_views.RegisterAPIView.as_view(), name='register'),
        path('logout/', auth_views.LogoutAPIView.as_view(), name='logout'),
        path('profile/', auth_views.UserProfileAPIView.as_view(), name='profile'),
        path('change-password/', auth_views.ChangePasswordAPIView.as_view(), name='change_password'),
    ])),
    
    # Core functionality endpoints
    path('upload/', core_views.FileUploadAPIView.as_view(), name='file_upload'),
    path('pricing/calculate/', core_views.PricingCalculatorAPIView.as_view(), name='pricing_calculate'),
    
    # Design tool specific endpoints
    path('design/', include([
        path('search/images/', core_views.ImageSearchAPIView.as_view(), name='image_search'),
        path('save/', core_views.SaveDesignAPIView.as_view(), name='save_design'),
        path('export/', core_views.ExportDesignAPIView.as_view(), name='export_design'),
        path('assets/', core_views.UserAssetsAPIView.as_view(), name='user_assets'),
    ])),
    
    # Include all router URLs
    path('', include(router.urls)),
]