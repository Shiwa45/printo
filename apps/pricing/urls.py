from django.urls import path
from .api import price_quote

app_name = 'pricing'

urlpatterns = [
    path('quote/', price_quote, name='quote'),
]


