from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone_number', 'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed User information"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone_number', 'role', 'is_active', 
                  'permissions', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user with password"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'name', 'phone_number', 'password', 'password_confirm', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields don't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user details without password"""
    
    class Meta:
        model = User
        fields = ['name', 'phone_number', 'is_active']


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing user password"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields don't match."})
        return attrs
