from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Merchandise, Order, OrderItem

User = get_user_model()


class MerchandiseListSerializer(serializers.ModelSerializer):
    """Serializer for listing merchandise items"""
    
    created_by_name = serializers.ReadOnlyField(source='created_by.name')
    in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Merchandise
        fields = ['id', 'name', 'price', 'image', 'category', 'stock', 'in_stock',
                  'featured', 'rating', 'created_by_name']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MerchandiseDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed merchandise item information"""
    
    created_by = serializers.SerializerMethodField()
    in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Merchandise
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 
                  'stock', 'in_stock', 'featured', 'rating', 'created_by', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_created_by(self, obj):
        return {
            'id': obj.created_by.id,
            'name': obj.created_by.name,
            'email': obj.created_by.email
        }


class MerchandiseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new merchandise item"""
    
    class Meta:
        model = Merchandise
        fields = ['name', 'description', 'price', 'image', 'category', 
                  'stock', 'featured', 'rating', 'created_by']
    
    def validate_created_by(self, value):
        # Ensure the requesting user is the creator or has admin permissions
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.role == 'ADMIN' or request.user.role == 'MANAGER' or request.user.id == value.id:
                return value
        raise serializers.ValidationError("You don't have permission to create merchandise for this user.")


class MerchandiseUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating merchandise items"""
    
    class Meta:
        model = Merchandise
        fields = ['name', 'description', 'price', 'image', 'category', 
                  'stock', 'featured', 'rating']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    
    merchandise_details = serializers.SerializerMethodField()
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'merchandise', 'merchandise_details', 'quantity', 'unit_price', 'subtotal']
    
    def get_merchandise_details(self, obj):
        return {
            'id': obj.merchandise.id,
            'name': obj.merchandise.name,
            'image': obj.merchandise.image
        }


class OrderCreateItemSerializer(serializers.Serializer):
    """Serializer for creating order items"""
    
    merchandise_id = serializers.PrimaryKeyRelatedField(queryset=Merchandise.objects.all(), source='merchandise')
    quantity = serializers.IntegerField(min_value=1)
    
    def validate(self, attrs):
        merchandise = attrs.get('merchandise')
        quantity = attrs.get('quantity')
        
        if not merchandise.in_stock:
            raise serializers.ValidationError(f"'{merchandise.name}' is out of stock.")
        
        if quantity > merchandise.stock:
            raise serializers.ValidationError(f"Not enough stock for '{merchandise.name}'. Available: {merchandise.stock}")
        
        return attrs


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for listing orders"""
    
    user_name = serializers.ReadOnlyField(source='user.name')
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_name', 'total_amount', 'status', 'items_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed order information"""
    
    user = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_amount', 'status', 'shipping_address', 
                  'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.name,
            'email': obj.user.email,
            'phone_number': obj.user.phone_number
        }


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new order"""
    
    items = OrderCreateItemSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = ['user', 'shipping_address', 'items']
    
    def validate_user(self, value):
        # Ensure the requesting user is the order user or has admin permissions
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.role == 'ADMIN' or request.user.role == 'MANAGER' or request.user.id == value.id:
                return value
        raise serializers.ValidationError("You don't have permission to create orders for this user.")
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        total_amount = 0
        
        # Calculate the total amount
        for item_data in items_data:
            merchandise = item_data['merchandise']
            quantity = item_data['quantity']
            total_amount += merchandise.price * quantity
        
        # Create the order
        validated_data['total_amount'] = total_amount
        order = Order.objects.create(**validated_data)
        
        # Create the order items
        for item_data in items_data:
            merchandise = item_data['merchandise']
            quantity = item_data['quantity']
            
            OrderItem.objects.create(
                order=order,
                merchandise=merchandise,
                quantity=quantity,
                unit_price=merchandise.price
            )
            
            # Update the merchandise stock
            merchandise.stock -= quantity
            merchandise.save()
        
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status (admin only)"""
    
    class Meta:
        model = Order
        fields = ['status']
