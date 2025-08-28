
# apps/products/urls.py
from django.urls import path
from .views import ProductCategoryView, ProductDetailView, calculate_price

app_name = 'products'

urlpatterns = [
    path('', ProductCategoryView.as_view(), name='list'),  # Product list page
    path('business-cards/', ProductCategoryView.as_view(), name='business_cards'),  # Business cards page
    path('category/<slug:category_slug>/', ProductCategoryView.as_view(), name='category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', ProductDetailView.as_view(), name='detail'),
    path('ajax/calculate-price/', calculate_price, name='calculate_price'),
]
