from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Blog

User = get_user_model()


class BlogListSerializer(serializers.ModelSerializer):
    """Serializer for listing blog posts"""
    
    author_name = serializers.ReadOnlyField(source='author.name')
    
    class Meta:
        model = Blog
        fields = ['id', 'title', 'excerpt', 'date', 'author_name', 'category', 
                  'image', 'featured', 'status']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BlogDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed blog post information"""
    
    author = serializers.SerializerMethodField()
    
    class Meta:
        model = Blog
        fields = ['id', 'title', 'excerpt', 'content', 'date', 'author', 'category', 
                 'image', 'featured', 'status', 'rejection_reason', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'name': obj.author.name,
            'email': obj.author.email
        }


class BlogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new blog post"""
    
    class Meta:
        model = Blog
        fields = ['title', 'excerpt', 'content', 'date', 'author', 'category', 'image', 'featured']
    
    def validate_author(self, value):
        # Ensure the requesting user is the author or has admin permissions
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.role == 'ADMIN' or request.user.role == 'MANAGER' or request.user.id == value.id:
                return value
        raise serializers.ValidationError("You don't have permission to create posts for this author.")


class BlogUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating blog posts"""
    
    class Meta:
        model = Blog
        fields = ['title', 'excerpt', 'content', 'date', 'category', 'image', 'featured']


class BlogStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating blog post status (admins only)"""
    
    class Meta:
        model = Blog
        fields = ['status', 'rejection_reason']
        
    def validate(self, attrs):
        if attrs.get('status') == 'REJECTED' and not attrs.get('rejection_reason'):
            raise serializers.ValidationError({"rejection_reason": "Rejection reason is required when rejecting a blog post."})
        return attrs
