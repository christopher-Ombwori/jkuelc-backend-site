from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Blog
from .serializers import (
    BlogListSerializer, BlogDetailSerializer,
    BlogCreateSerializer, BlogUpdateSerializer, BlogStatusUpdateSerializer
)
from users.permissions import IsAdminOrManager, IsAdminOrManagerOrOwner


class BlogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for blog posts management
    """
    queryset = Blog.objects.all().order_by('-date')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'excerpt', 'content', 'author__name']
    ordering_fields = ['date', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BlogCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BlogUpdateSerializer
        elif self.action == 'retrieve':
            return BlogDetailSerializer
        elif self.action == 'update_status':
            return BlogStatusUpdateSerializer
        return BlogListSerializer
    
    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManagerOrOwner()]
        elif self.action == 'update_status':
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Filter by category if provided
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        else:
            # Only show published posts to unauthenticated users
            if not self.request.user.is_authenticated:
                queryset = queryset.filter(status='PUBLISHED')
        
        # Filter by featured if provided
        featured = self.request.query_params.get('featured', None)
        if featured is not None:
            featured_bool = featured.lower() == 'true'
            queryset = queryset.filter(featured=featured_bool)
        
        # Filter by author if provided
        author_id = self.request.query_params.get('author', None)
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        return queryset
    
    def perform_create(self, serializer):
        # Set default status based on user role
        status_value = 'DRAFT'
        if self.request.user.role in ['ADMIN', 'MANAGER']:
            status_value = 'PUBLISHED'
        
        serializer.save(status=status_value)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update a blog post's status (admin only)
        """
        blog = self.get_object()
        serializer = self.get_serializer(blog, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_blogs(self, request):
        """
        Retrieve the authenticated user's blog posts
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        queryset = Blog.objects.filter(author=request.user).order_by('-date')
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = BlogListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BlogListSerializer(queryset, many=True)
        return Response(serializer.data)
