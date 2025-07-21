from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, EventRegistration

User = get_user_model()


class EventListSerializer(serializers.ModelSerializer):
    """Serializer for listing events"""
    
    created_by_name = serializers.ReadOnlyField(source='created_by.name')
    is_past = serializers.ReadOnlyField()
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'date', 'time', 'location', 'image', 'attendees',
                  'status', 'is_featured', 'is_registration_open', 'created_by_name', 'is_past']
        read_only_fields = ['id', 'attendees', 'created_at', 'updated_at']


class EventDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed event information"""
    
    created_by = serializers.SerializerMethodField()
    is_past = serializers.ReadOnlyField()
    registrations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'time', 'location', 'image', 
                  'attendees', 'status', 'is_featured', 'is_registration_open', 
                  'created_by', 'is_past', 'registrations_count', 'created_at', 'updated_at', 'important_reminders']
        read_only_fields = ['id', 'created_at', 'updated_at', 'registrations_count']
    
    def get_created_by(self, obj):
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'name': obj.created_by.name,
                'email': obj.created_by.email
            }
        return None
    
    def get_registrations_count(self, obj):
        return obj.registrations.count()


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new event"""
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'image', 
                  'is_featured', 'is_registration_open', 'created_by', 'important_reminders']
    
    def validate_created_by(self, value):
        # Ensure the requesting user is the creator or has admin permissions
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.role == 'ADMIN' or request.user.role == 'MANAGER' or request.user.id == value.id:
                return value
        raise serializers.ValidationError("You don't have permission to create events for this user.")


class EventUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating events"""
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'image', 
                  'status', 'is_featured', 'is_registration_open', 'important_reminders']


class EventRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for event registrations"""
    
    user_name = serializers.ReadOnlyField(source='user.name')
    event_title = serializers.ReadOnlyField(source='event.title')
    
    class Meta:
        model = EventRegistration
        fields = ['id', 'event', 'user', 'user_name', 'event_title', 'registration_date', 'attended']
        read_only_fields = ['id', 'registration_date', 'user']
    
    def validate(self, attrs):
        event = attrs.get('event')
        user = self.context['request'].user
        
        # Check if the event is open for registration
        if not event.is_registration_open:
            raise serializers.ValidationError("This event is not open for registration.")
        
        # Check if the event is in the past
        if event.is_past:
            raise serializers.ValidationError("Cannot register for past events.")
        
        # Check if the user is already registered
        if EventRegistration.objects.filter(event=event, user=user).exists():
            raise serializers.ValidationError("You are already registered for this event.")
        
        return attrs
    
    def create(self, validated_data):
        # Automatically set the user to the authenticated user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class EventAttendanceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating attendance status (admin only)"""
    
    class Meta:
        model = EventRegistration
        fields = ['attended']
