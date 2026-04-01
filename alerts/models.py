# alerts/models.py
from django.db import models
from accounts.models import User
from django.utils import timezone

class Alert(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency'),
    )
    
    TYPE_CHOICES = (
        ('crowd', 'Crowd Alert'),
        ('emergency', 'Emergency'),
        ('security', 'Security Alert'),
        ('weather', 'Weather Alert'),
        ('natural_disaster', 'Natural Disaster'),
        ('news', 'Breaking News'),
        ('system', 'System Alert'),
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='security')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    location = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_alerts')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    sent_to_all = models.BooleanField(default=False)
    source = models.CharField(max_length=100, blank=True, null=True)
    external_id = models.CharField(max_length=200, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source', 'external_id']),
            models.Index(fields=['priority', 'created_at']),
            models.Index(fields=['alert_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.priority}"
    
    def get_priority_color(self):
        colors = {
            'low': 'info',
            'medium': 'warning',
            'high': 'orange',
            'emergency': 'danger'
        }
        return colors.get(self.priority, 'secondary')
    
    def get_priority_icon(self):
        icons = {
            'low': 'fa-info-circle',
            'medium': 'fa-exclamation-triangle',
            'high': 'fa-exclamation-circle',
            'emergency': 'fa-skull-crosswalk'
        }
        return icons.get(self.priority, 'fa-bell')

class AlertRecipient(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_via_sms = models.BooleanField(default=False)
    sent_via_email = models.BooleanField(default=False)
    sent_via_app = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['alert', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.alert.title}"
    
    def mark_as_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save()

class EmergencyPanic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    message = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Panic from {self.user.username} at {self.created_at}"
    
    def resolve(self):
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save()