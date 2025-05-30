from django.contrib import admin
from .models import Event, EventRegistration


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'status', 'is_featured', 'is_registration_open', 'attendees')
    list_filter = ('status', 'is_featured', 'is_registration_open')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'description', 'date', 'time', 'location', 'image')}),
        ('Settings', {'fields': ('status', 'is_featured', 'is_registration_open', 'attendees')}),
        ('Administration', {'fields': ('created_by',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'registration_date', 'attended')
    list_filter = ('attended', 'registration_date')
    search_fields = ('event__title', 'user__name', 'user__email')
    fieldsets = (
        (None, {'fields': ('event', 'user', 'attended')}),
        ('Dates', {'fields': ('registration_date',)}),
    )


admin.site.register(Event, EventAdmin)
admin.site.register(EventRegistration, EventRegistrationAdmin)

