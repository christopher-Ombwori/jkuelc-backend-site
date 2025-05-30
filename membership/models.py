from django.db import models
from django.utils import timezone
from django.conf import settings


class Member(models.Model):
    MEMBERSHIP_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='member')
    membership_status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    membership_expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
    
    def __str__(self):
        return f"{self.user.name} - {self.membership_status}"
    
    @property
    def is_active(self):
        if self.membership_status != 'ACTIVE':
            return False
        if self.membership_expiry and self.membership_expiry < timezone.now():
            return False
        return True

