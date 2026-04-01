# alerts/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Alert, AlertRecipient, EmergencyPanic
from accounts.models import User
import json
import requests
import logging

logger = logging.getLogger(__name__)

def is_admin_or_security(user):
    return user.is_authenticated and user.role in ['admin', 'security']

@login_required
def index(request):
    alerts = Alert.objects.filter(is_active=True)[:50]
    return render(request, 'alerts/index.html', {'alerts': alerts})

@login_required
def panic_button(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            panic = EmergencyPanic.objects.create(
                user=request.user,
                latitude=data.get('latitude', 0),
                longitude=data.get('longitude', 0),
                message=data.get('message', 'Emergency!')
            )
            
            alert = Alert.objects.create(
                title=f"🚨 EMERGENCY - {request.user.username}",
                message=data.get('message', 'Emergency situation detected'),
                alert_type='emergency',
                priority='emergency',
                location=data.get('location', 'Unknown'),
                latitude=data.get('latitude', 0),
                longitude=data.get('longitude', 0),
                created_by=request.user,
                source='Panic Button'
            )
            
            recipients = User.objects.filter(role__in=['admin', 'security'], is_active=True)
            for recipient in recipients:
                AlertRecipient.objects.create(alert=alert, user=recipient, sent_via_app=True)
            
            return JsonResponse({'status': 'success', 'alert_id': alert.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

@login_required
@user_passes_test(is_admin_or_security)
def send_alert(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            alert = Alert.objects.create(
                title=data.get('title'),
                message=data.get('message'),
                alert_type=data.get('alert_type', 'security'),
                priority=data.get('priority', 'medium'),
                location=data.get('location', ''),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                created_by=request.user,
                source='Manual'
            )
            
            if data.get('send_to_all', False):
                recipients = User.objects.filter(is_active=True)
            else:
                recipients = User.objects.filter(role__in=['security', 'admin'], is_active=True)
            
            for recipient in recipients:
                AlertRecipient.objects.create(alert=alert, user=recipient, sent_via_app=True)
            
            alert.sent_to_all = True
            alert.save()
            
            return JsonResponse({'status': 'success', 'alert_id': alert.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

@login_required
def get_alerts(request):
    try:
        alerts = AlertRecipient.objects.filter(
            user=request.user, alert__is_active=True
        ).select_related('alert').order_by('-created_at')[:50]
        
        alerts_data = []
        for ar in alerts:
            alerts_data.append({
                'id': ar.alert.id,
                'title': ar.alert.title,
                'message': ar.alert.message,
                'priority': ar.alert.priority,
                'location': ar.alert.location,
                'latitude': float(ar.alert.latitude) if ar.alert.latitude else None,
                'longitude': float(ar.alert.longitude) if ar.alert.longitude else None,
                'source': ar.alert.source or 'System',
                'created_at': ar.alert.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'read': ar.read_at is not None
            })
        return JsonResponse({'status': 'success', 'alerts': alerts_data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def mark_alert_read(request, alert_id):
    try:
        ar = AlertRecipient.objects.filter(alert_id=alert_id, user=request.user).first()
        if ar and not ar.read_at:
            ar.read_at = timezone.now()
            ar.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'info', 'message': 'Already read'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def get_global_alerts(request):
    """Fetch global alerts without view on map feature"""
    try:
        alerts = []
        
        # Fetch earthquake data from USGS
        response = requests.get('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson', timeout=10)
        if response.status_code == 200:
            data = response.json()
            for feature in data.get('features', [])[:10]:
                props = feature['properties']
                mag = props.get('mag', 0)
                place = props.get('place', 'Unknown location')
                time_ms = props.get('time', 0)
                
                if mag >= 2.5:
                    if mag >= 6.0:
                        priority = 'emergency'
                    elif mag >= 5.0:
                        priority = 'high'
                    elif mag >= 4.0:
                        priority = 'medium'
                    else:
                        priority = 'low'
                    
                    alerts.append({
                        'title': f"🌍 Earthquake: M{mag} - {place}",
                        'message': f"Magnitude {mag} earthquake detected at {place}. Time: {__import__('datetime').datetime.fromtimestamp(time_ms/1000).strftime('%Y-%m-%d %H:%M:%S')} UTC.",
                        'priority': priority,
                        'location': place,
                        'source': 'USGS',
                        'magnitude': mag
                    })
        
        return JsonResponse({'status': 'success', 'alerts': alerts, 'count': len(alerts)})
        
    except Exception as e:
        logger.error(f"Error fetching global alerts: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@csrf_exempt
def refresh_global_alerts(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'message': 'Alerts refreshed'})
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)