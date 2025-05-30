from django.db import models
from django.utils import timezone
from django.conf import settings
from merchandise.models import Order


class Payment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    PAYMENT_TYPE_CHOICES = (
        ('MEMBERSHIP', 'Membership'),
        ('ORDER', 'Order'),
        ('DONATION', 'Donation'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('MPESA', 'M-Pesa'),
        ('CARD', 'Card'),
        ('BANK', 'Bank Transfer'),
        ('CASH', 'Cash'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.PositiveIntegerField()
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    reference_id = models.CharField(max_length=100, null=True, blank=True)  # For any external reference
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.payment_type} - {self.amount} KES - {self.status}"


class MembershipPayment(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='membership_payment')
    membership_period = models.PositiveIntegerField(default=12)  # In months
    
    class Meta:
        verbose_name = 'Membership Payment'
        verbose_name_plural = 'Membership Payments'
    
    def __str__(self):
        return f"Membership Payment - {self.payment.user.name}"


class Notification(models.Model):
    TYPE_CHOICES = (
        ('SYSTEM', 'System'),
        ('PAYMENT', 'Payment'),
        ('EVENT', 'Event'),
        ('BLOG', 'Blog'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    reference_id = models.CharField(max_length=100, null=True, blank=True)  # ID of related object
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.name}"


class Feedback(models.Model):
    TYPE_CHOICES = (
        ('GENERAL', 'General'),
        ('EVENT', 'Event'),
        ('MERCHANDISE', 'Merchandise'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback')
    content = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='GENERAL')
    reference_id = models.CharField(max_length=100, null=True, blank=True)  # ID of related object
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.type} Feedback - {self.user.name}"


class MpesaTransaction(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='mpesa_transaction', null=True, blank=True)
    phone_number = models.CharField(max_length=15)  # Format: 254XXXXXXXXX
    amount = models.PositiveIntegerField()
    reference = models.CharField(max_length=100)  # Account reference
    description = models.CharField(max_length=255)
    merchant_request_id = models.CharField(max_length=100, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, null=True, blank=True)
    transaction_date = models.CharField(max_length=20, null=True, blank=True)  # Format from M-Pesa: YYYYMMDDHHmmss
    result_code = models.CharField(max_length=10, null=True, blank=True)
    result_description = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    raw_request = models.JSONField(null=True, blank=True)
    raw_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'M-Pesa Transaction'
        verbose_name_plural = 'M-Pesa Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"M-Pesa Transaction - {self.amount} KES - {self.status}"

