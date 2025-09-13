# apps/api/views/core_views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import uuid
import requests
from PIL import Image
from io import BytesIO

from apps.design_tool.models import UserDesign, DesignAsset
from apps.products.models import Product
from .serializers import FileUploadSerializer, PricingCalculationSerializer


class FileUploadAPIView(APIView):
    """
    API endpoint for file uploads (images, assets for design tool)
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            file_type = serializer.validated_data.get('type', 'asset')
            
            # Generate unique filename
            file_extension = uploaded_file.name.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Save file
            file_path = f"uploads/{file_type}s/{unique_filename}"
            saved_path = default_storage.save(file_path, uploaded_file)
            file_url = default_storage.url(saved_path)
            
            # Create asset record if it's a design asset
            if file_type == 'asset':
                asset = DesignAsset.objects.create(
                    user=request.user,
                    name=uploaded_file.name,
                    file_path=saved_path,
                    file_type=file_extension,
                    file_size=uploaded_file.size
                )
                
                return Response({
                    'id': asset.id,
                    'url': file_url,
                    'name': asset.name,
                    'type': asset.file_type,
                    'size': asset.file_size,
                    'message': 'File uploaded successfully'
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'url': file_url,
                'path': saved_path,
                'message': 'File uploaded successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PricingCalculatorAPIView(APIView):
    """
    API endpoint for calculating product pricing based on specifications
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def post(self, request):
        serializer = PricingCalculationSerializer(data=request.data)
        if serializer.is_valid():
            product_slug = serializer.validated_data['product_slug']
            quantity = serializer.validated_data['quantity']
            specifications = serializer.validated_data.get('specifications', {})
            
            try:
                product = Product.objects.get(slug=product_slug, status='active')
                
                # Basic pricing calculation (you can enhance this logic)
                base_price = float(product.base_price)
                total_price = base_price * quantity
                
                # Apply specifications pricing (if product has complex pricing)
                if hasattr(product, 'pricing_data') and product.pricing_data:
                    # Complex pricing logic based on specifications
                    # This would use your existing pricing calculation logic
                    pass
                
                # Calculate discounts, taxes, etc.
                gst_rate = settings.BUSINESS_CONFIG.get('GST_RATE', 0.18)
                gst_amount = total_price * gst_rate
                final_total = total_price + gst_amount
                
                return Response({
                    'product': {
                        'name': product.name,
                        'slug': product.slug,
                        'base_price': base_price
                    },
                    'quantity': quantity,
                    'subtotal': total_price,
                    'gst_amount': gst_amount,
                    'total': final_total,
                    'specifications': specifications
                })
                
            except Product.DoesNotExist:
                return Response({
                    'error': 'Product not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageSearchAPIView(APIView):
    """
    API endpoint for searching images from free APIs (Pixabay, Unsplash, etc.)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.GET.get('query', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        source = request.GET.get('source', 'pixabay')  # pixabay, unsplash, pexels
        
        if not query:
            return Response({
                'error': 'Query parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if source == 'pixabay':
                results = self._search_pixabay(query, page, per_page)
            elif source == 'unsplash':
                results = self._search_unsplash(query, page, per_page)
            else:
                results = {'images': [], 'total': 0}
            
            return Response(results)
            
        except Exception as e:
            return Response({
                'error': f'Image search failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _search_pixabay(self, query, page, per_page):
        """Search Pixabay API"""
        api_key = settings.PIXABAY_API_KEY
        if not api_key:
            return {'images': [], 'total': 0, 'error': 'Pixabay API key not configured'}
        
        url = "https://pixabay.com/api/"
        params = {
            'key': api_key,
            'q': query,
            'page': page,
            'per_page': min(per_page, 200),
            'safesearch': 'true',
            'image_type': 'photo'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        images = []
        for hit in data.get('hits', []):
            images.append({
                'id': hit['id'],
                'url': hit['webformatURL'],
                'preview_url': hit['previewURL'],
                'large_url': hit['largeImageURL'],
                'tags': hit['tags'],
                'user': hit['user'],
                'source': 'pixabay'
            })
        
        return {
            'images': images,
            'total': data.get('totalHits', 0),
            'page': page,
            'per_page': per_page
        }
    
    def _search_unsplash(self, query, page, per_page):
        """Search Unsplash API (if configured)"""
        # Implementation for Unsplash API
        return {'images': [], 'total': 0}


class SaveDesignAPIView(APIView):
    """
    API endpoint for saving design data
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        design_data = request.data.get('design_data')
        design_id = request.data.get('design_id')
        name = request.data.get('name', 'Untitled Design')
        
        if not design_data:
            return Response({
                'error': 'Design data is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if design_id:
                # Update existing design
                design = UserDesign.objects.get(id=design_id, user=request.user)
                design.canvas_data = design_data
                design.name = name
                design.save()
            else:
                # Create new design
                design = UserDesign.objects.create(
                    user=request.user,
                    name=name,
                    canvas_data=design_data
                )
            
            return Response({
                'design_id': design.id,
                'name': design.name,
                'message': 'Design saved successfully'
            })
            
        except UserDesign.DoesNotExist:
            return Response({
                'error': 'Design not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to save design: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExportDesignAPIView(APIView):
    """
    API endpoint for exporting designs in various formats
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        design_id = request.data.get('design_id')
        export_format = request.data.get('format', 'png')  # png, jpg, pdf, svg
        
        if not design_id:
            return Response({
                'error': 'Design ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            design = UserDesign.objects.get(id=design_id, user=request.user)
            
            # Export logic would go here
            # For now, return a placeholder response
            export_url = f"/media/exports/{design.id}.{export_format}"
            
            return Response({
                'export_url': export_url,
                'format': export_format,
                'message': 'Design exported successfully'
            })
            
        except UserDesign.DoesNotExist:
            return Response({
                'error': 'Design not found'
            }, status=status.HTTP_404_NOT_FOUND)


class UserAssetsAPIView(APIView):
    """
    API endpoint for managing user's design assets
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        assets = DesignAsset.objects.filter(user=request.user).order_by('-created_at')
        
        assets_data = []
        for asset in assets:
            assets_data.append({
                'id': asset.id,
                'name': asset.name,
                'url': asset.file_path.url if asset.file_path else None,
                'type': asset.file_type,
                'size': asset.file_size,
                'created_at': asset.created_at
            })
        
        return Response({
            'assets': assets_data,
            'count': len(assets_data)
        })