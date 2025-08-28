# apps/design_tool/serializers.py
from rest_framework import serializers
from .models import DesignTemplate, UserDesign
from apps.products.serializers import ProductSerializer

class DesignTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignTemplate
        fields = [
            'id', 'name', 'category', 'product_types', 'template_data',
            'preview_image', 'thumbnail_image', 'width', 'height', 'dpi',
            'color_mode', 'tags', 'is_premium', 'is_featured'
        ]

class UserDesignSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    template = DesignTemplateSerializer(read_only=True)
    
    class Meta:
        model = UserDesign
        fields = [
            'id', 'product', 'template', 'name', 'design_data',
            'preview_image', 'is_favorite', 'created_at', 'last_modified'
        ]
        read_only_fields = ['created_at', 'last_modified']