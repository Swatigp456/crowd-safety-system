# incidents/validation_service.py
import re
from datetime import datetime, timedelta
from django.utils import timezone
from accounts.models import User

class IncidentValidationService:
    """Service to validate incident reports and detect fraud"""
    
    def __init__(self, incident):
        self.incident = incident
        self.score = 100  # Start with 100, deduct for suspicious factors
        self.reasons = []
    
    def validate(self):
        """Run all validation checks"""
        self.check_description_quality()
        self.check_user_history()
        self.check_location_validity()
        self.check_media_quality()
        self.check_keywords()
        self.check_timing_pattern()
        self.check_similar_incidents()
        
        # Set confidence score
        self.incident.confidence_score = max(0, min(100, self.score))
        
        # Determine validation status
        if self.score >= 70:
            self.incident.validation_status = 'verified'
            self.incident.is_fraud = False
        elif self.score >= 40:
            self.incident.validation_status = 'under_review'
            self.incident.is_fraud = False
        else:
            self.incident.validation_status = 'rejected'
            self.incident.is_fraud = True
            self.incident.fraud_reason = '; '.join(self.reasons)
        
        self.incident.validation_notes = '; '.join(self.reasons)
        self.incident.save()
        
        return {
            'score': self.score,
            'is_fraud': self.incident.is_fraud,
            'status': self.incident.validation_status,
            'reasons': self.reasons
        }
    
    def check_description_quality(self):
        """Check if description is detailed enough"""
        desc = self.incident.description or ""
        words = len(desc.split())
        
        if words < 10:
            self.score -= 20
            self.reasons.append("Description too short (less than 10 words)")
        elif words < 20:
            self.score -= 10
            self.reasons.append("Description could be more detailed")
        
        # Check for gibberish
        if self.is_gibberish(desc):
            self.score -= 40
            self.reasons.append("Description appears to be gibberish/spam")
    
    def check_user_history(self):
        """Check user's reporting history"""
        user = self.incident.reported_by
        previous_reports = Incident.objects.filter(reported_by=user).exclude(id=self.incident.id)
        
        # Check if user has many rejected reports
        rejected_count = previous_reports.filter(is_fraud=True).count()
        if rejected_count > 3:
            self.score -= 30
            self.reasons.append(f"User has {rejected_count} previous false reports")
        elif rejected_count > 1:
            self.score -= 15
            self.reasons.append(f"User has {rejected_count} previous false reports")
        
        # Check if user is new (joined recently)
        days_since_join = (timezone.now() - user.date_joined).days
        if days_since_join < 1:
            self.score -= 20
            self.reasons.append("User account is very new - possible spam")
        elif days_since_join < 7:
            self.score -= 10
            self.reasons.append("User account is new")
        
        # Check reporting frequency
        reports_last_hour = previous_reports.filter(reported_at__gte=timezone.now() - timedelta(hours=1)).count()
        if reports_last_hour > 3:
            self.score -= 25
            self.reasons.append(f"User reported {reports_last_hour} incidents in last hour - suspicious")
    
    def check_location_validity(self):
        """Check if location coordinates are valid"""
        lat = float(self.incident.latitude) if self.incident.latitude else 0
        lng = float(self.incident.longitude) if self.incident.longitude else 0
        
        # Check if coordinates are default (0,0)
        if lat == 0 and lng == 0:
            self.score -= 15
            self.reasons.append("No location coordinates provided")
        
        # Check if coordinates are in ocean (simplified check)
        if lat == 0 or lng == 0:
            self.score -= 10
            self.reasons.append("Suspicious coordinates")
    
    def check_media_quality(self):
        """Check if media is provided and of good quality"""
        has_image = bool(self.incident.image)
        has_video = bool(self.incident.video)
        
        if not has_image and not has_video:
            self.score -= 10
            self.reasons.append("No photo or video evidence provided")
        
        if has_image:
            self.score += 10
            self.reasons.append("Photo evidence provided (+10)")
        
        if has_video:
            self.score += 15
            self.reasons.append("Video evidence provided (+15)")
    
    def check_keywords(self):
        """Check for suspicious keywords indicating false reports"""
        text = (self.incident.title + " " + self.incident.description).lower()
        
        suspicious_keywords = [
            'test', 'testing', 'fake', 'spam', 'joke', 'lol', 'haha',
            'just kidding', 'not real', 'ignore', 'delete', 'wrong',
            'accidentally', 'mistake', 'sorry', 'cancel'
        ]
        
        for keyword in suspicious_keywords:
            if keyword in text:
                self.score -= 15
                self.reasons.append(f"Suspicious keyword detected: '{keyword}'")
                break
        
        # Check for emergency keywords (adds confidence)
        emergency_keywords = ['fire', 'accident', 'emergency', 'help', 'injured', 'collision', 'smoke']
        for keyword in emergency_keywords:
            if keyword in text:
                self.score += 5
                self.reasons.append(f"Emergency keyword detected: '{keyword}' (+5)")
                break
    
    def check_timing_pattern(self):
        """Check if reporting time is unusual"""
        hour = self.incident.reported_at.hour
        
        # Late night reports (3-5 AM) might be suspicious
        if 3 <= hour <= 5:
            self.score -= 10
            self.reasons.append("Reported during unusual hours (3-5 AM)")
    
    def check_similar_incidents(self):
        """Check for similar incidents in same area recently"""
        from incidents.models import Incident as IncidentModel
        time_threshold = timezone.now() - timedelta(hours=24)
        similar_incidents = IncidentModel.objects.filter(
            location__icontains=self.incident.location[:20] if self.incident.location else '',
            reported_at__gte=time_threshold
        ).exclude(id=self.incident.id)
        
        if similar_incidents.count() > 5:
            self.score -= 15
            self.reasons.append(f"Multiple similar reports in same area ({similar_incidents.count()} in 24h)")
        elif similar_incidents.count() > 0:
            self.score += 5
            self.reasons.append(f"Similar incident reported recently - likely real (+5)")
    
    def is_gibberish(self, text):
        """Check if text appears to be gibberish or spam"""
        # Check for repetitive characters
        if re.search(r'(.)\1{5,}', text):
            return True
        
        # Check if mostly numbers or special characters
        alnum_count = sum(c.isalnum() for c in text)
        if len(text) > 0 and alnum_count / len(text) < 0.3:
            return True
        
        return False