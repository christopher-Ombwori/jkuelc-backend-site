from django.contrib import admin
from .models import Blog


class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'date', 'featured')
    list_filter = ('status', 'category', 'featured')
    search_fields = ('title', 'content', 'author__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'excerpt', 'content', 'author', 'image')}),
        ('Classification', {'fields': ('category', 'featured')}),
        ('Publication', {'fields': ('date', 'status', 'rejection_reason')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


admin.site.register(Blog, BlogAdmin)

