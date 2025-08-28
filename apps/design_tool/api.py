# apps/design_tool/api.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import DesignTemplate, UserDesign
from .serializers import DesignTemplateSerializer, UserDesignSerializer

class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DesignTemplate.objects.filter(status='active')
    serializer_class = DesignTemplateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['category', 'is_premium', 'is_featured']
    ordering = ['-is_featured', '-usage_count', 'name']

class UserDesignViewSet(viewsets.ModelViewSet):
    serializer_class = UserDesignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserDesign.objects.filter(user=self.request.user).order_by('-last_modified')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
