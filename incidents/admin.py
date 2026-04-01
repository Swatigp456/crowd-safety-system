from django.contrib import admin
from .models import Incident, IncidentComment

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'incident_type', 'status', 'location', 'reported_at')
    list_filter = ('incident_type', 'status', 'reported_at')
    search_fields = ('title', 'description', 'location')

@admin.register(IncidentComment)
class IncidentCommentAdmin(admin.ModelAdmin):
    list_display = ('incident', 'user', 'created_at')
    list_filter = ('created_at',)