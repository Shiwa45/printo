# apps/products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Legacy pricing endpoint
    path('api/calculate-price/', views.calculate_product_price, name='calculate_price'),
    
    # Enhanced pricing endpoints
    path('api/pricing/calculate/', views.calculate_advanced_pricing, name='calculate_advanced_pricing'),
    path('api/pricing/advanced/', views.calculate_advanced_pricing, name='calculate_advanced_pricing_alt'),
    path('api/price-breaks/<int:product_id>/', views.get_price_breaks, name='get_price_breaks'),
    path('api/pricing/validate/', views.validate_product_configuration, name='validate_configuration'),
    
    # Product catalog endpoints
    path('api/product/<int:product_id>/', views.get_product_details, name='product_details'),
    path('api/catalog/', views.get_product_catalog, name='product_catalog'),
    path('api/categories/', views.get_categories, name='categories'),
    
    # Enhanced product pages
    path('', views.product_catalog_page, name='list'),  # Default products list
    path('catalog/', views.product_catalog_page, name='catalog'),
    path('compare/', views.product_comparison_page, name='comparison'),
    path('<slug:product_slug>/', views.enhanced_product_detail, name='enhanced_product_detail'),
]