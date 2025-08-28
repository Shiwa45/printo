# apps/products/serializers.py
from rest_framework import serializers
from .models import Product, ProductCategory, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary']

class ProductCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'subcategories']
    
    def get_subcategories(self, obj):
        subcategories = obj.productcategory_set.filter(is_active=True).order_by('sort_order')
        return ProductCategorySerializer(subcategories, many=True).data

class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'product_type', 'description', 
            'short_description', 'base_price', 'pricing_structure', 'size_options',
            'paper_options', 'print_options', 'binding_options', 'finish_options',
            'design_tool_enabled', 'design_templates', 'min_quantity', 'max_quantity',
            'stock_status', 'lead_time_days', 'rush_available', 'featured', 
            'bestseller', 'images', 'primary_image', 'tags'
        ]
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return primary.image.url if primary.image else None
        first_image = obj.images.first()
        return first_image.image.url if first_image and first_image.image else None
