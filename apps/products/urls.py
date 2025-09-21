
# apps/products/urls.py
from django.urls import path
from .views import (
    ProductCategoryView, ProductDetailView, EnhancedProductDetailView, 
    ProductsHomeView, calculate_price, add_to_cart, search_products,
    get_product_design_options
)

app_name = 'products'

urlpatterns = [
    path('', ProductsHomeView.as_view(), name='home'),  # Enhanced products home page
    path('list/', ProductCategoryView.as_view(), name='list'),  # Original product list page
    path('business-cards/', ProductCategoryView.as_view(), name='business_cards'),  # Business cards page
    path('category/<slug:category_slug>/', ProductCategoryView.as_view(), name='category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', EnhancedProductDetailView.as_view(), name='detail'),
    path('ajax/calculate-price/', calculate_price, name='calculate_price'),
    path('api/calculate-price/', calculate_price, name='api_calculate_price'),
    path('ajax/add-to-cart/', add_to_cart, name='add_to_cart'),
    path('ajax/search/', search_products, name='search'),
    path('api/<int:product_id>/design-options/', get_product_design_options, name='design_options'),
    path('api/products/<int:product_id>/design-options/', get_product_design_options, name='api_design_options'),
]
