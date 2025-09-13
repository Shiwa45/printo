# apps/products/api.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Product, ProductCategory
from .serializers import ProductSerializer, ProductCategorySerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(status='active').select_related('category').prefetch_related('images')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'product_type', 'featured', 'bestseller', 'design_tool_enabled']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'base_price', 'created_at']
    ordering = ['-featured', 'name']
    lookup_field = 'slug'
    
    @action(detail=False, methods=['get'])
    def bestsellers(self, request):
        bestsellers = self.queryset.filter(bestseller=True)[:4]
        serializer = self.get_serializer(bestsellers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def design_products(self, request):
        design_products = self.queryset.filter(design_tool_enabled=True)[:6]
        serializer = self.get_serializer(design_products, many=True)
        return Response(serializer.data)