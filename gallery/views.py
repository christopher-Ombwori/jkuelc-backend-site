from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Gallery
from .serializers import (
    GalleryListSerializer, GalleryDetailSerializer,
    GalleryCreateSerializer, GalleryUpdateSerializer
)
from users.permissions import IsAdminOrManager, IsAdminOrManagerOrOwner


class GalleryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for gallery items management
    """
    queryset = Gallery.objects.all().order_by('-created_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category']
    ordering_fields = ['created_at', 'title']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GalleryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return GalleryUpdateSerializer
        elif self.action == 'retrieve':
            return GalleryDetailSerializer
        return GalleryListSerializer
    
    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManagerOrOwner()]
        return [permissions.IsAuthenticated(), IsAdminOrManager()]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Filter by category if provided
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by event if provided
        event_id = self.request.query_params.get('event', None)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        # Filter by uploader if provided
        uploader_id = self.request.query_params.get('uploaded_by', None)
        if uploader_id:
            queryset = queryset.filter(uploaded_by_id=uploader_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_uploads(self, request):
        """
        Retrieve the authenticated user's gallery uploads
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        queryset = Gallery.objects.filter(uploaded_by=request.user).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = GalleryListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = GalleryListSerializer(queryset, many=True)
        return Response(serializer.data)
