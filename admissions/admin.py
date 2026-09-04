# Register your models here.

# admin.py
from django.contrib import admin
from .models import AdmissionApplication

@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    # Columns shown in the admin list view
    list_display = ('full_name', 'target_class', 'parent_name', 'phone', 'applied_at')
    
    # Filter sidebar options
    list_filter = ('target_class', 'applied_at')
    
    # Search box configuration
    search_fields = ('full_name', 'parent_name', 'email', 'phone')
    
    # Group fields into sections when viewing an individual application
    fieldsets = (
        ('Student Details', {
            'fields': ('full_name', 'date_of_birth', 'target_class', 'previous_school')
        }),
        ('Parent / Guardian Information', {
            'fields': ('parent_name', 'email', 'phone')
        }),
        ('System Info', {
            'fields': ('applied_at',),
            'classes': ('collapse',),
        }),
    )
    
    # applied_at is auto-generated, so it must be read-only in the detailed view
    readonly_fields = ('applied_at',)
    
    # Order by newest applications first
    ordering = ('-applied_at',)