from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Event, EventRegistration
from .serializers import (
    EventListSerializer, EventDetailSerializer, EventCreateSerializer, 
    EventUpdateSerializer, EventRegistrationSerializer, EventAttendanceUpdateSerializer
)
from users.permissions import IsAdminOrManager, IsAdminOrManagerOrOwner


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for events management
    """
    queryset = Event.objects.all().order_by('date')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['date', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EventCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EventUpdateSerializer
        elif self.action == 'retrieve':
            return EventDetailSerializer
        return EventListSerializer
    
    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManagerOrOwner()]
        elif self.action in ['my_events', 'registered']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdminOrManager()]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by upcoming/past if provided
        time_filter = self.request.query_params.get('time', None)
        if time_filter:
            today = timezone.now().date()
            if time_filter.lower() == 'upcoming':
                queryset = queryset.filter(date__gte=today)
            elif time_filter.lower() == 'past':
                queryset = queryset.filter(date__lt=today)
        
        # Filter by featured if provided
        featured = self.request.query_params.get('featured', None)
        if featured is not None:
            featured_bool = featured.lower() == 'true'
            queryset = queryset.filter(is_featured=featured_bool)
        
        # Filter by registration status if provided
        registration = self.request.query_params.get('registration_open', None)
        if registration is not None:
            registration_bool = registration.lower() == 'true'
            queryset = queryset.filter(is_registration_open=registration_bool)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_events(self, request):
        """
        Retrieve the authenticated user's created events
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        queryset = Event.objects.filter(created_by=request.user).order_by('date')
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = EventListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def registered(self, request):
        """
        Retrieve events the authenticated user is registered for
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get all event IDs the user is registered for
        registrations = EventRegistration.objects.filter(user=request.user).values_list('event_id', flat=True)
        queryset = Event.objects.filter(id__in=registrations).order_by('date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EventListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventListSerializer(queryset, many=True)
        return Response(serializer.data)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for event registrations
    """
    queryset = EventRegistration.objects.all().order_by('-registration_date')
    serializer_class = EventRegistrationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__name', 'event__title']

    

    
    def get_permissions(self):
        # For create action, only require authentication
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        
        # For destroy action, allow users to delete their own registrations or admin/manager
        if self.action == 'destroy':
            return [permissions.IsAuthenticated()]
        
        # For other actions, require admin/manager permissions
        if self.action in ['update', 'partial_update', 'update_attendance']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        
        # For list and retrieve, only require authentication
        return [permissions.IsAuthenticated()]
    

    
    def get_queryset(self):
        queryset = self.queryset
        
        # Filter by event if provided
        event_id = self.request.query_params.get('event', None)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        # Filter by user if provided
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Regular users can only see their own registrations
        if self.request.user.is_authenticated and self.request.user.role not in ['ADMIN', 'MANAGER']:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        # Save the registration
        registration = serializer.save()
        
        # Update event attendee count
        event = registration.event
        event.attendees = EventRegistration.objects.filter(event=event).count()
        event.save()
    
    def perform_destroy(self, instance):
        # Check if user can delete this registration
        if self.request.user.role not in ['ADMIN', 'MANAGER'] and instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own registrations.")
        
        # Save the event before deleting the registration
        event = instance.event
        
        # Delete the registration
        instance.delete()
        
        # Update event attendee count
        event.attendees = EventRegistration.objects.filter(event=event).count()
        event.save()
    
    @action(detail=True, methods=['patch'])
    def update_attendance(self, request, pk=None):
        """
        Update a registration's attendance status (admin only)
        """
        registration = self.get_object()
        serializer = EventAttendanceUpdateSerializer(registration, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
