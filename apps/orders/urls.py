# apps/orders/urls.py
from django.urls import path
from .views import CartView, CheckoutView, OrderHistoryView

app_name = 'orders'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('history/', OrderHistoryView.as_view(), name='history'),
]