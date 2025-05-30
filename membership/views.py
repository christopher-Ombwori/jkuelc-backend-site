from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Member
from .serializers import (
    MemberSerializer, MemberDetailSerializer,
    MemberCreateSerializer, MemberUpdateSerializer
)
from users.permissions import IsAdminOrManager, IsAdminOrManagerOrOwner


class MemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint for members management
    """
    queryset = Member.objects.all().order_by('-created_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__name', 'user__email']
    ordering_fields = ['created_at', 'membership_expiry']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MemberCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MemberUpdateSerializer
        elif self.action == 'retrieve' or self.action == 'my_membership':
            return MemberDetailSerializer
        return MemberSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        elif self.action == 'my_membership':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdminOrManager()]
    
    @action(detail=False, methods=['get'])
    def my_membership(self, request):
        """
        Retrieve the authenticated user's membership
        """
        try:
            member = Member.objects.get(user=request.user)
            serializer = self.get_serializer(member)
            return Response(serializer.data)
        except Member.DoesNotExist:
            return Response(
                {"detail": "You don't have a membership record."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update a member's membership status (admin only)
        """
        member = self.get_object()
        membership_status = request.data.get('membership_status')
        
        if not membership_status:
            return Response(
                {"detail": "Membership status is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if membership_status not in [s[0] for s in Member.MEMBERSHIP_STATUS_CHOICES]:
            return Response(
                {"detail": "Invalid membership status."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member.membership_status = membership_status
        member.save()
        serializer = MemberDetailSerializer(member)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_payment_status(self, request, pk=None):
        """
        Update a member's payment status (admin only)
        """
        member = self.get_object()
        payment_status = request.data.get('payment_status')
        
        if not payment_status:
            return Response(
                {"detail": "Payment status is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if payment_status not in [s[0] for s in Member.PAYMENT_STATUS_CHOICES]:
            return Response(
                {"detail": "Invalid payment status."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member.payment_status = payment_status
        member.save()
        serializer = MemberDetailSerializer(member)
        return Response(serializer.data)
