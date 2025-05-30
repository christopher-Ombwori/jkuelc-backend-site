from django.db import models
from django.utils import timezone
from django.conf import settings


class Blog(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('PUBLISHED', 'Published'),
        ('REJECTED', 'Rejected'),
    )
    
    CATEGORY_CHOICES = (
        ('Leadership', 'Leadership'),
        ('Success Stories', 'Success Stories'),
        ('Community', 'Community'),
        ('Events', 'Events'),
        ('Education', 'Education'),
    )
    
    title = models.CharField(max_length=255)
    excerpt = models.TextField()
    content = models.TextField()
    date = models.DateField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blogs')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.URLField()
    featured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    rejection_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'
        ordering = ['-date']
    
    def __str__(self):
        return self.title

