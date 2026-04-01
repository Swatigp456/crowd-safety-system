# incidents/models.py
from django.db import models
from accounts.models import User
from django.utils import timezone

class Incident(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected - False Report'),
    )
    
    TYPE_CHOICES = (
        ('accident', 'Accident'),
        ('medical', 'Medical Emergency'),
        ('security', 'Security Issue'),
        ('crowd', 'Crowd Management'),
        ('fire', 'Fire'),
        ('other', 'Other'),
    )
    
    VALIDATION_STATUS = (
        ('pending', 'Pending Review'),
        ('verified', 'Verified - Real Report'),
        ('rejected', 'Rejected - False Report'),
        ('under_review', 'Under Review'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    incident_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    location = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, default=0)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, default=0)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents')
    image = models.ImageField(upload_to='incidents/', blank=True, null=True)
    video = models.FileField(upload_to='incidents/videos/', blank=True, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    # Validation fields
    validation_status = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')
    confidence_score = models.IntegerField(default=0, help_text="0-100 confidence score")
    validation_notes = models.TextField(blank=True, null=True)
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validated_incidents')
    validated_at = models.DateTimeField(blank=True, null=True)
    is_fraud = models.BooleanField(default=False)
    fraud_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-reported_at']
    
    def __str__(self):
        return f"{self.title} - {self.status} - Confidence: {self.confidence_score}%"
    
    def get_validation_badge(self):
        if self.validation_status == 'verified':
            return '<span class="badge bg-success">✅ Verified</span>'
        elif self.validation_status == 'rejected':
            return '<span class="badge bg-danger">❌ Rejected - False</span>'
        elif self.validation_status == 'under_review':
            return '<span class="badge bg-warning">⏳ Under Review</span>'
        else:
            return '<span class="badge bg-secondary">🔄 Pending</span>'
    
    def get_validation_status_display(self):
        return dict(self.VALIDATION_STATUS).get(self.validation_status, 'Pending')

class IncidentComment(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.incident.title}"