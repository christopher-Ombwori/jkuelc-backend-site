from django.contrib import admin
from .models import Merchandise, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


class MerchandiseAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'stock', 'in_stock', 'featured', 'rating')
    list_filter = ('category', 'featured', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('name', 'description', 'price', 'image')}),
        ('Classification', {'fields': ('category', 'featured', 'rating')}),
        ('Inventory', {'fields': ('stock',)}),
        ('Administration', {'fields': ('created_by',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'total_amount', 'status')}),
        ('Shipping', {'fields': ('shipping_address',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    inlines = [OrderItemInline]


admin.site.register(Merchandise, MerchandiseAdmin)
admin.site.register(Order, OrderAdmin)

