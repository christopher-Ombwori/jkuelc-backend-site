from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Merchandise, Order, OrderItem
from .serializers import (
    MerchandiseListSerializer, MerchandiseDetailSerializer,
    MerchandiseCreateSerializer, MerchandiseUpdateSerializer,
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    OrderStatusUpdateSerializer, OrderItemSerializer
)
from users.permissions import IsAdminOrManager, IsAdminOrManagerOrOwner


class MerchandiseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for merchandise management
    """
    queryset = Merchandise.objects.all().order_by('-created_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['name', 'price', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MerchandiseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MerchandiseUpdateSerializer
        elif self.action == 'retrieve':
            return MerchandiseDetailSerializer
        return MerchandiseListSerializer
    
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
        
        # Filter by in_stock if provided
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock is not None:
            in_stock_bool = in_stock.lower() == 'true'
            if in_stock_bool:
                queryset = queryset.filter(stock__gt=0)
            else:
                queryset = queryset.filter(stock=0)
        
        # Filter by featured if provided
        featured = self.request.query_params.get('featured', None)
        if featured is not None:
            featured_bool = featured.lower() == 'true'
            queryset = queryset.filter(featured=featured_bool)
        
        # Filter by min/max price if provided
        min_price = self.request.query_params.get('min_price', None)
        if min_price and min_price.isdigit():
            queryset = queryset.filter(price__gte=int(min_price))
        
        max_price = self.request.query_params.get('max_price', None)
        if max_price and max_price.isdigit():
            queryset = queryset.filter(price__lte=int(max_price))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_merchandise(self, request):
        """
        Retrieve the authenticated user's created merchandise
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        queryset = Merchandise.objects.filter(created_by=request.user).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = MerchandiseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MerchandiseListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_stock(self, request, pk=None):
        """
        Update a merchandise item's stock (admin only)
        """
        merchandise = self.get_object()
        stock = request.data.get('stock')
        
        if stock is None:
            return Response(
                {"detail": "Stock quantity is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stock = int(stock)
            if stock < 0:
                return Response(
                    {"detail": "Stock cannot be negative."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {"detail": "Stock must be a valid number."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        merchandise.stock = stock
        merchandise.save()
        serializer = MerchandiseDetailSerializer(merchandise)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for order management
    """
    queryset = Order.objects.all().order_by('-created_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__name', 'user__email']
    ordering_fields = ['created_at', 'total_amount']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderListSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        elif self.action == 'update_status':
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Regular users can only see their own orders
        if self.request.user.is_authenticated and self.request.user.role not in ['ADMIN', 'MANAGER']:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """
        Retrieve the authenticated user's orders
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        queryset = Order.objects.filter(user=request.user).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update an order's status (admin only)
        """
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
