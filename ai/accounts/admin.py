# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserLocation
from django.utils.html import format_html

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role_badge', 'phone_number', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('role', 'phone_number', 'address', 'profile_picture', 
                      'emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('wide',)
        }),
    )
    
    def role_badge(self, obj):
        colors = {
            'admin': 'danger',
            'security': 'warning',
            'user': 'info'
        }
        color = colors.get(obj.role, 'secondary')
        return format_html(
            '<span style="background: linear-gradient(135deg, var(--{}-color), var(--{}-dark)); padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: 600;">{}</span>',
            color, color, obj.get_role_display()
        )
    
    role_badge.short_description = 'Role'
    role_badge.allow_tags = True
    
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} users activated.')
    make_active.short_description = "Activate selected users"
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} users deactivated.')
    make_inactive.short_description = "Deactivate selected users"

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserLocation)