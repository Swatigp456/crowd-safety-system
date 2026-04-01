from django.contrib import admin
from .models import Alert, AlertRecipient, EmergencyPanic

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'alert_type', 'priority', 'created_at', 'is_active')
    list_filter = ('alert_type', 'priority', 'is_active')
    search_fields = ('title', 'message')

@admin.register(AlertRecipient)
class AlertRecipientAdmin(admin.ModelAdmin):
    list_display = ('alert', 'user', 'read_at')
    list_filter = ('sent_via_app',)

@admin.register(EmergencyPanic)
class EmergencyPanicAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_resolved')
    list_filter = ('is_resolved',)