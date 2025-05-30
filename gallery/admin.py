from django.contrib import admin
from .models import Gallery


class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'uploaded_by__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'description', 'image', 'category')}),
        ('Relationships', {'fields': ('event', 'drive_link')}),
        ('Administration', {'fields': ('uploaded_by',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


admin.site.register(Gallery, GalleryAdmin)

