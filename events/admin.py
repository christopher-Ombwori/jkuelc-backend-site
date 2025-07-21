from django.contrib import admin
from django import forms
from .models import Event, EventRegistration


class EventAdminForm(forms.ModelForm):
    reminder_1 = forms.CharField(max_length=200, required=False, label="Reminder 1")
    reminder_2 = forms.CharField(max_length=200, required=False, label="Reminder 2")
    reminder_3 = forms.CharField(max_length=200, required=False, label="Reminder 3")
    reminder_4 = forms.CharField(max_length=200, required=False, label="Reminder 4")
    reminder_5 = forms.CharField(max_length=200, required=False, label="Reminder 5")

    class Meta:
        model = Event
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.important_reminders:
            reminders = self.instance.important_reminders
            for i, reminder in enumerate(reminders[:5], 1):
                self.fields[f'reminder_{i}'].initial = reminder

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Collect non-empty reminders
        reminders = []
        for i in range(1, 6):
            reminder = self.cleaned_data.get(f'reminder_{i}')
            if reminder and reminder.strip():
                reminders.append(reminder.strip())
        
        instance.important_reminders = reminders
        return super().save(commit)


class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = ('title', 'date', 'location', 'status', 'is_featured', 'is_registration_open', 'attendees')
    list_filter = ('status', 'is_featured', 'is_registration_open')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'description', 'date', 'time', 'location', 'image')}),
        ('Settings', {'fields': ('status', 'is_featured', 'is_registration_open', 'attendees')}),
        ('Important Reminders', {
            'fields': ('reminder_1', 'reminder_2', 'reminder_3', 'reminder_4', 'reminder_5'),
            'description': 'Add important reminders for attendees (e.g., what to bring, dress code, etc.). Leave empty fields blank.'
        }),
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

