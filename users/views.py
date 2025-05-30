from rest_framework import viewsets, permissions, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import (
    UserSerializer, UserDetailSerializer, UserCreateSerializer,
    UserUpdateSerializer, PasswordChangeSerializer
)
from .permissions import IsAdminOrManager, IsAdminOrManagerOrOwner

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users management
    """
    queryset = User.objects.all().order_by('-date_joined')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'date_joined']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'retrieve' or self.action == 'me':
            return UserDetailSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManagerOrOwner()]
        elif self.action == 'me':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdminOrManager()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retrieve the authenticated user's details
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def change_password(self, request):
        """
        Change the authenticated user's password
        """
        user = request.user
        serializer = PasswordChangeSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.data.get('old_password')):
                return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'status': 'password changed'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
