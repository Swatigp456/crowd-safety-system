# monitoring/admin.py
from django.contrib import admin
from .models import CrowdData, Camera, Zone
from django.utils.html import format_html

@admin.register(CrowdData)
class CrowdDataAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'density_badge', 'count', 'timestamp')
    list_filter = ('density', 'timestamp')
    search_fields = ('location_name',)
    date_hierarchy = 'timestamp'
    
    def density_badge(self, obj):
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger'
        }
        color = colors.get(obj.density, 'secondary')
        return format_html(
            '<span style="background: var(--{}-color); padding: 4px 12px; border-radius: 50px; font-size: 11px;">{}</span>',
            color, obj.get_density_display()
        )
    
    density_badge.short_description = 'Density'

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('name', 'camera_status', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'url')
    
    def camera_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #28a745;">● Active</span>')
        return format_html('<span style="color: #dc3545;">● Inactive</span>')
    
    camera_status.short_description = 'Status'

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'radius', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)