from django.urls import path
from . import views

app_name = 'design_tool'

urlpatterns = [
    # Design editor views
    path('editor/<slug:product_slug>/', views.design_editor_view, name='editor'),
    
    # Template management
    path('templates/', views.template_list_view, name='templates'),
    path('api/template/<uuid:template_id>/data/', views.get_template_data, name='template_data'),
    
    # User design management
    path('my-designs/', views.my_designs_view, name='my_designs'),
    path('api/design/<uuid:design_id>/data/', views.get_design_data, name='design_data'),
    
    # API endpoints for design operations
    path('api/save/', views.save_design_api, name='save_design_api'),
    path('api/export/', views.export_design_api, name='export_design_api'),
    
    # Image search and asset management APIs
    path('api/search/images/', views.search_images_api, name='search_images_api'),
    path('api/search/pixabay/', views.search_pixabay_api, name='search_pixabay_api'),
    path('api/search/pixabay-templates/', views.search_pixabay_templates_api, name='search_pixabay_templates_api'),
    path('api/upload/asset/', views.upload_asset_api, name='upload_asset_api'),
    path('api/assets/', views.get_user_assets_api, name='get_user_assets_api'),
    
    # Order integration
    path('api/finalize-and-order/', views.finalize_and_order_view, name='finalize_and_order'),
    
    # Admin template management
    path('admin/upload-templates/', views.admin_template_upload_view, name='admin_template_upload'),
]
