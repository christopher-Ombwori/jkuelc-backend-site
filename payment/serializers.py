from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment, MembershipPayment, Notification, Feedback, MpesaTransaction
from merchandise.models import Order

User = get_user_model()


class PaymentListSerializer(serializers.ModelSerializer):
    """Serializer for listing payments"""
    
    user_name = serializers.ReadOnlyField(source='user.name')
    
    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_name', 'amount', 'payment_type', 'status', 
                  'payment_method', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed payment information"""
    
    user = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = ['id', 'user', 'amount', 'payment_type', 'status', 'payment_method',
                  'transaction_id', 'reference_id', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.name,
            'email': obj.user.email
        }
    
    def get_order(self, obj):
        if obj.order:
            return {
                'id': obj.order.id,
                'total_amount': obj.order.total_amount,
                'status': obj.order.status
            }
        return None


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new payment"""
    
    class Meta:
        model = Payment
        fields = ['user', 'amount', 'payment_type', 'payment_method', 
                  'transaction_id', 'reference_id', 'order']
    
    def validate_user(self, value):
        # Ensure the requesting user is the payment user or has admin permissions
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.role == 'ADMIN' or request.user.role == 'MANAGER' or request.user.id == value.id:
                return value
        raise serializers.ValidationError("You don't have permission to create payments for this user.")
    
    def validate_order(self, value):
        if value and value.status != 'PENDING':
            raise serializers.ValidationError("Can only make payments for orders with 'PENDING' status.")
        return value
    
    def validate(self, attrs):
        payment_type = attrs.get('payment_type')
        order = attrs.get('order')
        
        # Validate order-related payment
        if payment_type == 'ORDER' and not order:
            raise serializers.ValidationError("Order is required for payment type 'ORDER'.")
        
        if payment_type != 'ORDER' and order:
            raise serializers.ValidationError("Order should only be specified for payment type 'ORDER'.")
        
        # If order is provided, validate amount matches
        if order and attrs.get('amount') != order.total_amount:
            raise serializers.ValidationError(f"Payment amount must match order total: {order.total_amount}")
        
        return attrs


class PaymentStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating payment status (admin only)"""
    
    class Meta:
        model = Payment
        fields = ['status', 'transaction_id']
    
    def validate(self, attrs):
        if attrs.get('status') == 'COMPLETED' and not attrs.get('transaction_id'):
            raise serializers.ValidationError("Transaction ID is required for completed payments.")
        return attrs


class MembershipPaymentSerializer(serializers.ModelSerializer):
    """Serializer for membership payments"""
    
    payment = PaymentDetailSerializer(read_only=True)
    payment_id = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all(), write_only=True, source='payment')
    
    class Meta:
        model = MembershipPayment
        fields = ['id', 'payment', 'payment_id', 'membership_period']
        read_only_fields = ['id']
    
    def validate_payment_id(self, value):
        if value.payment_type != 'MEMBERSHIP':
            raise serializers.ValidationError("Payment must be of type 'MEMBERSHIP'.")
        
        if MembershipPayment.objects.filter(payment=value).exists():
            raise serializers.ValidationError("This payment is already associated with a membership.")
        
        return value


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer for listing notifications"""
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'type', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed notification information"""
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'content', 'type', 'is_read', 
                  'reference_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new notification"""
    
    class Meta:
        model = Notification
        fields = ['user', 'title', 'content', 'type', 'reference_id']
    
    def validate_user(self, value):
        # Only admins can create notifications for other users
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.role == 'ADMIN' or request.user.role == 'MANAGER' or request.user.id == value.id:
                return value
        raise serializers.ValidationError("You don't have permission to create notifications for this user.")


class NotificationReadUpdateSerializer(serializers.ModelSerializer):
    """Serializer for marking notifications as read"""
    
    class Meta:
        model = Notification
        fields = ['is_read']


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for feedback"""
    
    user_name = serializers.ReadOnlyField(source='user.name')
    
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_name', 'content', 'type', 'reference_id', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeedbackCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new feedback"""
    
    class Meta:
        model = Feedback
        fields = ['type', 'content', 'reference_id']
        
    def create(self, validated_data):
        # Set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MpesaTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaTransaction
        fields = '__all__'
        read_only_fields = [
            'payment', 'merchant_request_id', 'checkout_request_id', 
            'mpesa_receipt_number', 'transaction_date', 'result_code', 
            'result_description', 'status', 'raw_request', 'raw_response', 
            'created_at', 'updated_at'
        ]


class MpesaTransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaTransaction
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MpesaTransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaTransaction
        fields = ['phone_number', 'amount', 'reference', 'description']
    
    def create(self, validated_data):
        # Set raw_request as empty JSON object
        validated_data['raw_request'] = {}
        return super().create(validated_data)
