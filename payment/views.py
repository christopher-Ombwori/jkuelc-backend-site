from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Payment, MembershipPayment, Notification, Feedback
from membership.models import Member
from .serializers import (
    PaymentListSerializer, PaymentDetailSerializer, PaymentCreateSerializer,
    PaymentStatusUpdateSerializer, MembershipPaymentSerializer,
    NotificationListSerializer, NotificationDetailSerializer, NotificationCreateSerializer,
    NotificationReadUpdateSerializer, FeedbackSerializer, FeedbackCreateSerializer
)
from users.permissions import IsAdminOrManager, IsAdminOrManagerOrOwner


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payments management
    """
    queryset = Payment.objects.all().order_by('-created_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__name', 'user__email', 'transaction_id']
    ordering_fields = ['created_at', 'amount']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'retrieve':
            return PaymentDetailSerializer
        elif self.action == 'update_status':
            return PaymentStatusUpdateSerializer
        return PaymentListSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        elif self.action == 'update_status':
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Filter by payment type if provided
        payment_type = self.request.query_params.get('payment_type', None)
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by payment method if provided
        payment_method = self.request.query_params.get('payment_method', None)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Regular users can only see their own payments
        if self.request.user.is_authenticated and self.request.user.role not in ['ADMIN', 'MANAGER']:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """
        Retrieve the authenticated user's payments
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        queryset = Payment.objects.filter(user=request.user).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = PaymentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PaymentListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @transaction.atomic
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update a payment's status (admin only)
        """
        payment = self.get_object()
        serializer = self.get_serializer(payment, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Save the payment with updated status
            payment = serializer.save()
            
            # If the payment is for membership and is now completed, update the member's status
            if payment.payment_type == 'MEMBERSHIP' and payment.status == 'COMPLETED':
                try:
                    # Check if there's an associated MembershipPayment
                    membership_payment = MembershipPayment.objects.get(payment=payment)
                    
                    # Get or create the member record
                    member, created = Member.objects.get_or_create(
                        user=payment.user,
                        defaults={
                            'membership_status': 'PENDING',
                            'payment_status': 'PENDING'
                        }
                    )
                    
                    # Update the member's payment and membership status
                    member.payment_status = 'PAID'
                    member.membership_status = 'ACTIVE'
                    
                    # Calculate membership expiry based on membership period
                    from datetime import timedelta
                    member.membership_expiry = timezone.now() + timedelta(days=30 * membership_payment.membership_period)
                    member.save()
                    
                    # Create a notification for the user
                    Notification.objects.create(
                        user=payment.user,
                        title='Membership Payment Successful',
                        content=f'Your membership payment has been processed successfully. Your membership is now active until {member.membership_expiry.date()}.',
                        type='PAYMENT',
                        reference_id=str(payment.id)
                    )
                    
                except MembershipPayment.DoesNotExist:
                    # No associated membership payment, just create a notification
                    Notification.objects.create(
                        user=payment.user,
                        title='Payment Successful',
                        content='Your payment has been processed successfully.',
                        type='PAYMENT',
                        reference_id=str(payment.id)
                    )
            
            # If the payment is for an order and is now completed, update the order status
            elif payment.payment_type == 'ORDER' and payment.status == 'COMPLETED' and payment.order:
                order = payment.order
                order.status = 'PAID'
                order.save()
                
                # Create a notification for the user
                Notification.objects.create(
                    user=payment.user,
                    title='Order Payment Successful',
                    content=f'Your payment for order #{order.id} has been processed successfully. Your order status is now "Paid".',
                    type='PAYMENT',
                    reference_id=str(payment.id)
                )
            
            return Response(PaymentDetailSerializer(payment).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MembershipPaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for membership payments management
    """
    queryset = MembershipPayment.objects.all().order_by('-payment__created_at')
    serializer_class = MembershipPaymentSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Regular users can only see their own membership payments
        if self.request.user.is_authenticated and self.request.user.role not in ['ADMIN', 'MANAGER']:
            queryset = queryset.filter(payment__user=self.request.user)
        
        return queryset


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for notifications management
    """
    queryset = Notification.objects.all().order_by('-created_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        elif self.action == 'retrieve':
            return NotificationDetailSerializer
        elif self.action == 'mark_read':
            return NotificationReadUpdateSerializer
        return NotificationListSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Filter by type if provided
        notification_type = self.request.query_params.get('type', None)
        if notification_type:
            queryset = queryset.filter(type=notification_type)
        
        # Filter by read status if provided
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        # Regular users can only see their own notifications
        if self.request.user.is_authenticated and self.request.user.role not in ['ADMIN', 'MANAGER']:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_notifications(self, request):
        """
        Retrieve the authenticated user's notifications
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        queryset = Notification.objects.filter(user=request.user).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = NotificationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = NotificationListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        """
        Mark a notification as read
        """
        notification = self.get_object()
        
        # Check if the user owns this notification
        if notification.user != request.user and request.user.role not in ['ADMIN', 'MANAGER']:
            return Response(
                {"detail": "You do not have permission to modify this notification."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.is_read = True
        notification.save()
        return Response(NotificationDetailSerializer(notification).data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all of the authenticated user's notifications as read
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"status": "All notifications marked as read"}, status=status.HTTP_200_OK)


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint for feedback management
    """
    queryset = Feedback.objects.all().order_by('-created_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content', 'type']
    ordering_fields = ['created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FeedbackCreateSerializer
        return FeedbackSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Filter by type if provided
        feedback_type = self.request.query_params.get('type', None)
        if feedback_type:
            queryset = queryset.filter(type=feedback_type)
        
        # Regular users can only see their own feedback
        if self.request.user.is_authenticated and self.request.user.role not in ['ADMIN', 'MANAGER']:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_feedback(self, request):
        """
        Retrieve the authenticated user's feedback
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        queryset = Feedback.objects.filter(user=request.user).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = FeedbackSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = FeedbackSerializer(queryset, many=True)
        return Response(serializer.data)
