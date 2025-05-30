from django.db import models
from django.utils import timezone
from django.conf import settings
from events.models import Event


class Gallery(models.Model):
    CATEGORY_CHOICES = (
        ('events', 'Events'),
        ('community', 'Community'),
        ('workshops', 'Workshops'),
        ('networking', 'Networking'),
        ('leadership', 'Leadership'),
        ('mentorship', 'Mentorship'),
        ('competitions', 'Competitions'),
        ('education', 'Education'),
        ('international', 'International'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.URLField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='gallery_images')
    drive_link = models.URLField(null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gallery_uploads')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Gallery Item'
        verbose_name_plural = 'Gallery Items'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

