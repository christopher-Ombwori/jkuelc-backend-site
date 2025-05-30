from django.db import models
from django.utils import timezone
from django.conf import settings


class Merchandise(models.Model):
    CATEGORY_CHOICES = (
        ('clothing', 'Clothing'),
        ('stationery', 'Stationery'),
        ('accessories', 'Accessories'),
        ('books', 'Books'),
        ('bundles', 'Bundles'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField()  # Price in KES
    image = models.URLField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    stock = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_merchandise')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Merchandise'
        verbose_name_plural = 'Merchandise Items'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def in_stock(self):
        return self.stock > 0


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    shipping_address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    merchandise = models.ForeignKey(Merchandise, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.PositiveIntegerField()  # Price at the time of order
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.quantity} x {self.merchandise.name}"
    
    @property
    def subtotal(self):
        return self.quantity * self.unit_price

