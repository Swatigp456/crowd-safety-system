# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from monitoring.models import CrowdData
from alerts.models import Alert, AlertRecipient, EmergencyPanic
from incidents.models import Incident
from accounts.models import User
from django.utils import timezone
from datetime import timedelta
import json
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# api/views.py



class RealTimeAlertAPI(APIView):
    """API for real-time alerts"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get recent alerts for current user"""
        try:
            # Get alerts for current user
            alerts = AlertRecipient.objects.filter(
                user=request.user,
                alert__is_active=True
            ).select_related('alert').order_by('-created_at')[:50]
            
            alerts_data = []
            for ar in alerts:
                alerts_data.append({
                    'id': ar.alert.id,
                    'title': ar.alert.title,
                    'message': ar.alert.message,
                    'type': ar.alert.alert_type,
                    'priority': ar.alert.priority,
                    'location': ar.alert.location,
                    'latitude': float(ar.alert.latitude) if ar.alert.latitude else None,
                    'longitude': float(ar.alert.longitude) if ar.alert.longitude else None,
                    'created_by': ar.alert.created_by.username if ar.alert.created_by else 'System',
                    'created_at': ar.alert.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'read': ar.read_at is not None,
                    'is_active': ar.alert.is_active
                })
            
            return Response({
                'status': 'success',
                'count': len(alerts_data),
                'alerts': alerts_data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    def post(self, request):
        """Create a new alert (Admin/Security only)"""
        if request.user.role not in ['admin', 'security']:
            return Response({
                'status': 'error',
                'message': 'Permission denied. Only admin and security can send alerts.'
            }, status=403)
        
        try:
            data = request.data
            
            # Create alert
            alert = Alert.objects.create(
                title=data.get('title'),
                message=data.get('message'),
                alert_type=data.get('alert_type', 'security'),
                priority=data.get('priority', 'medium'),
                location=data.get('location', ''),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                created_by=request.user
            )
            
            # Determine recipients
            if data.get('send_to_all', False):
                recipients = User.objects.filter(is_active=True)
            else:
                recipients = User.objects.filter(role__in=['security', 'admin'], is_active=True)
            
            # Send to recipients
            for recipient in recipients:
                AlertRecipient.objects.create(
                    alert=alert,
                    user=recipient,
                    sent_via_app=True
                )
            
            # Send WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'alerts',
                {
                    'type': 'alert_message',
                    'data': {
                        'id': alert.id,
                        'title': alert.title,
                        'message': alert.message,
                        'priority': alert.priority,
                        'location': alert.location,
                        'latitude': float(alert.latitude) if alert.latitude else None,
                        'longitude': float(alert.longitude) if alert.longitude else None,
                        'created_by': request.user.username,
                        'created_at': alert.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
            )
            
            return Response({
                'status': 'success',
                'alert_id': alert.id,
                'message': 'Alert sent successfully'
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)

class RealTimeCrowdAPI(APIView):
    """API for real-time crowd data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get real-time crowd data"""
        try:
            crowd_data = CrowdData.objects.filter(
                timestamp__gte=timezone.now() - timedelta(minutes=30)
            ).values('location_name', 'latitude', 'longitude', 'density', 'count', 'timestamp')
            
            data = []
            for item in crowd_data:
                data.append({
                    'location': item['location_name'],
                    'latitude': float(item['latitude']),
                    'longitude': float(item['longitude']),
                    'density': item['density'],
                    'count': item['count'],
                    'timestamp': item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return Response({
                'status': 'success',
                'count': len(data),
                'data': data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    def post(self, request):
        """Update crowd data (for AI detection)"""
        if request.user.role not in ['admin', 'security']:
            return Response({
                'status': 'error',
                'message': 'Permission denied'
            }, status=403)
        
        try:
            data = request.data
            
            crowd_data = CrowdData.objects.create(
                location_name=data.get('location_name'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                density=data.get('density', 'low'),
                count=data.get('count', 0)
            )
            
            # Send WebSocket update
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'crowd_data',
                {
                    'type': 'crowd_update',
                    'data': {
                        'id': crowd_data.id,
                        'location': crowd_data.location_name,
                        'latitude': float(crowd_data.latitude),
                        'longitude': float(crowd_data.longitude),
                        'density': crowd_data.density,
                        'count': crowd_data.count,
                        'timestamp': crowd_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
            )
            
            return Response({
                'status': 'success',
                'crowd_id': crowd_data.id
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)

class EmergencyPanicAPI(APIView):
    """API for emergency panic button"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Trigger emergency panic"""
        try:
            data = request.data
            
            # Create panic record
            panic = EmergencyPanic.objects.create(
                user=request.user,
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                message=data.get('message', 'Emergency!')
            )
            
            # Create emergency alert
            alert = Alert.objects.create(
                title=f"🚨 EMERGENCY - {request.user.username}",
                message=data.get('message', 'Emergency situation detected'),
                alert_type='emergency',
                priority='emergency',
                location=data.get('location', 'Unknown'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                created_by=request.user
            )
            
            # Notify all admins and security
            recipients = User.objects.filter(role__in=['admin', 'security'], is_active=True)
            
            for recipient in recipients:
                AlertRecipient.objects.create(
                    alert=alert,
                    user=recipient,
                    sent_via_app=True
                )
            
            # Send WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'alerts',
                {
                    'type': 'alert_message',
                    'data': {
                        'id': alert.id,
                        'title': alert.title,
                        'message': alert.message,
                        'priority': 'emergency',
                        'location': alert.location,
                        'latitude': float(alert.latitude) if alert.latitude else None,
                        'longitude': float(alert.longitude) if alert.longitude else None,
                        'created_by': request.user.username,
                        'created_at': alert.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'is_panic': True
                    }
                }
            )
            
            return Response({
                'status': 'success',
                'panic_id': panic.id,
                'alert_id': alert.id,
                'message': 'Emergency alert sent! Help is on the way.'
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)

class AlertAcknowledgementAPI(APIView):
    """API to acknowledge alerts"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, alert_id):
        """Mark alert as read"""
        try:
            alert_recipient = AlertRecipient.objects.filter(
                alert_id=alert_id,
                user=request.user
            ).first()
            
            if alert_recipient and not alert_recipient.read_at:
                alert_recipient.read_at = timezone.now()
                alert_recipient.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Alert acknowledged'
                })
            else:
                return Response({
                    'status': 'info',
                    'message': 'Alert already acknowledged'
                })
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)