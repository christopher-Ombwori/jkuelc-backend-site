from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Member

User = get_user_model()


class MemberSerializer(serializers.ModelSerializer):
    """Basic serializer for the Member model"""
    
    user_name = serializers.ReadOnlyField(source='user.name')
    user_email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = Member
        fields = ['id', 'user_id', 'user_name', 'user_email', 'membership_status', 
                  'payment_status', 'membership_expiry', 'is_active']
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']


class MemberDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for the Member model"""
    
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = ['id', 'user', 'membership_status', 'payment_status', 
                 'membership_expiry', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.name,
            'email': obj.user.email,
            'phone_number': obj.user.phone_number
        }


class MemberCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new member"""
    
    class Meta:
        model = Member
        fields = ['user_id', 'membership_status', 'payment_status', 'membership_expiry']
    
    def validate_user_id(self, value):
        # Check if a member already exists for this user
        if Member.objects.filter(user_id=value).exists():
            raise serializers.ValidationError("A member already exists for this user.")
        return value


class MemberUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating member details"""
    
    class Meta:
        model = Member
        fields = ['membership_status', 'payment_status', 'membership_expiry']
