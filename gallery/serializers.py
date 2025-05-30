from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Gallery
from events.models import Event

User = get_user_model()


class GalleryListSerializer(serializers.ModelSerializer):
    """Serializer for listing gallery items"""
    
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.name')
    event_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Gallery
        fields = ['id', 'title', 'image', 'category', 'uploaded_by_name', 'event_title', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_event_title(self, obj):
        if obj.event:
            return obj.event.title
        return None


class GalleryDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed gallery item information"""
    
    uploaded_by = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()
    
    class Meta:
        model = Gallery
        fields = ['id', 'title', 'description', 'image', 'category', 'event',
                  'drive_link', 'uploaded_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_uploaded_by(self, obj):
        return {
            'id': obj.uploaded_by.id,
            'name': obj.uploaded_by.name,
            'email': obj.uploaded_by.email
        }
    
    def get_event(self, obj):
        if obj.event:
            return {
                'id': obj.event.id,
                'title': obj.event.title,
                'date': obj.event.date
            }
        return None


class GalleryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new gallery item"""
    
    class Meta:
        model = Gallery
        fields = ['title', 'description', 'image', 'category', 'event', 'drive_link', 'uploaded_by']
    
    def validate_uploaded_by(self, value):
        # Ensure the requesting user is the uploader or has admin permissions
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.role == 'ADMIN' or request.user.role == 'MANAGER' or request.user.id == value.id:
                return value
        raise serializers.ValidationError("You don't have permission to upload for this user.")
    
    def validate_event(self, value):
        if value and not Event.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Event does not exist.")
        return value


class GalleryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating gallery items"""
    
    class Meta:
        model = Gallery
        fields = ['title', 'description', 'image', 'category', 'event', 'drive_link']
    
    def validate_event(self, value):
        if value and not Event.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Event does not exist.")
        return value
