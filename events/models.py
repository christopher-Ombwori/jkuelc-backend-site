from django.db import models
from django.utils import timezone
from django.conf import settings


class Event(models.Model):
    STATUS_CHOICES = (
        ('UPCOMING', 'Upcoming'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.CharField(max_length=50)  # Storing as string for flexibility (e.g., "9:00 AM - 4:00 PM")
    location = models.CharField(max_length=255)
    image = models.URLField()
    attendees = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPCOMING')
    is_featured = models.BooleanField(default=False)
    is_registration_open = models.BooleanField(default=True)
    important_reminders = models.JSONField(default=list, blank=True, help_text="List of important reminders for attendees")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_past(self):
        return self.date < timezone.now().date()


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(default=timezone.now)
    attended = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Event Registration'
        verbose_name_plural = 'Event Registrations'
        unique_together = ('event', 'user')
    
    def __str__(self):
        return f"{self.user.name} - {self.event.title}"

