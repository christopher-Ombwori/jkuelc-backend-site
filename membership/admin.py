from django.contrib import admin
from .models import Member


class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_status', 'payment_status', 'membership_expiry', 'is_active')
    list_filter = ('membership_status', 'payment_status')
    search_fields = ('user__name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'membership_status', 'payment_status', 'membership_expiry')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


admin.site.register(Member, MemberAdmin)

