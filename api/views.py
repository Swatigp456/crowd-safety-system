from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from monitoring.models import CrowdData
from alerts.models import Alert
from incidents.models import Incident
from accounts.models import User
from django.utils import timezone
from datetime import timedelta

class CrowdDataAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        crowd_data = CrowdData.objects.filter(
            timestamp__gte=timezone.now() - timedelta(minutes=30)
        ).values('location_name', 'latitude', 'longitude', 'density', 'count', 'timestamp')
        
        return Response({
            'status': 'success',
            'data': list(crowd_data)
        })

class AlertsAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        alerts = Alert.objects.filter(is_active=True)[:50].values(
            'title', 'message', 'priority', 'alert_type', 'created_at'
        )
        
        return Response({
            'status': 'success',
            'data': list(alerts)
        })

class IncidentsAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        incidents = Incident.objects.all().order_by('-reported_at')[:50].values(
            'title', 'incident_type', 'status', 'location', 'reported_at'
        )
        
        return Response({
            'status': 'success',
            'data': list(incidents)
        })

class UsersAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Unauthorized'}, status=403)
        
        users = User.objects.all().values('username', 'email', 'role', 'is_active', 'date_joined')
        
        return Response({
            'status': 'success',
            'data': list(users)
        })

# WebSocket functionality removed - channels not installed
