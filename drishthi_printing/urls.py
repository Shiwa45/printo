# drishthi_printing/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('products/', include('apps.products.urls')),
    path('services/', include('apps.services.urls')),
    path('orders/', include('apps.orders.urls')),
    path('users/', include('apps.users.urls')),
    path('design-tool/', include('apps.design_tool.urls')),
    path('api/pricing/', include('apps.pricing.urls')),


    # API endpoints (v1)
    path('api/', include('apps.api.urls')),

    # DRF Auth Token endpoint
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    # Legacy Django MVT URLs (keep during transition)
    
]
# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# For production: serve React app on all other routes
# Uncomment this when React frontend is ready
# urlpatterns += [
#     re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
# ]