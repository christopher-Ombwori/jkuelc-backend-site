from django.contrib import admin
from .models import Payment, MembershipPayment, Notification, Feedback, MpesaTransaction


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_type', 'status', 'payment_method', 'created_at')
    list_filter = ('payment_type', 'status', 'payment_method')
    search_fields = ('user__name', 'user__email', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'amount', 'payment_type', 'status')}),
        ('Details', {'fields': ('payment_method', 'transaction_id', 'reference_id')}),
        ('Relationships', {'fields': ('order',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


class MembershipPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment', 'membership_period')
    search_fields = ('payment__user__name', 'payment__user__email')
    fieldsets = (
        (None, {'fields': ('payment', 'membership_period')}),
    )


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'content', 'user__name', 'user__email')
    fieldsets = (
        (None, {'fields': ('user', 'title', 'content')}),
        ('Classification', {'fields': ('type', 'is_read')}),
        ('References', {'fields': ('reference_id',)}),
        ('Timestamps', {'fields': ('created_at',)}),
    )


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('content', 'user__name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'content', 'type')}),
        ('References', {'fields': ('reference_id',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'amount', 'reference', 'status', 'mpesa_receipt_number', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('phone_number', 'reference', 'mpesa_receipt_number', 'merchant_request_id', 'checkout_request_id')
    readonly_fields = ('created_at', 'updated_at', 'raw_request', 'raw_response')
    fieldsets = (
        (None, {'fields': ('payment', 'phone_number', 'amount', 'reference', 'description')}),
        ('Transaction Details', {'fields': ('status', 'merchant_request_id', 'checkout_request_id', 'mpesa_receipt_number', 'transaction_date')}),
        ('Response', {'fields': ('result_code', 'result_description')}),
        ('Raw Data', {'fields': ('raw_request', 'raw_response'), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


admin.site.register(Payment, PaymentAdmin)
admin.site.register(MembershipPayment, MembershipPaymentAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(MpesaTransaction, MpesaTransactionAdmin)

