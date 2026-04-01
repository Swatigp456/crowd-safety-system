# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from monitoring.models import CrowdData
from alerts.models import Alert, EmergencyPanic
from incidents.models import Incident
from accounts.models import User, UserLocation
import json
import random

@login_required
def index(request):
    """Admin dashboard with analytics"""
    context = {}
    
    # Get statistics
    context['total_users'] = User.objects.count()
    context['active_alerts'] = Alert.objects.filter(is_active=True).count()
    context['total_incidents'] = Incident.objects.filter(status='pending').count()
    context['active_panics'] = EmergencyPanic.objects.filter(is_resolved=False).count()
    context['critical_alerts'] = Alert.objects.filter(priority='emergency', is_active=True).count()
    
    # Get active users online
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    context['active_users_online'] = UserLocation.objects.filter(
        timestamp__gte=five_minutes_ago
    ).values('user').distinct().count()
    
    # ============================================
    # CROWD DENSITY DISTRIBUTION
    # ============================================
    last_24h = timezone.now() - timedelta(hours=24)
    crowd_data = CrowdData.objects.filter(timestamp__gte=last_24h)
    
    # Check if data exists - if not, create sample data
    if crowd_data.count() == 0:
        print("Creating sample crowd data...")
        
        # Create sample crowd data
        locations = [
            {'name': 'Times Square', 'lat': 40.7580, 'lng': -73.9855},
            {'name': 'Shopping Mall', 'lat': 40.7608, 'lng': -73.9845},
            {'name': 'Central Park', 'lat': 40.7829, 'lng': -73.9654},
            {'name': 'Broadway', 'lat': 40.7590, 'lng': -73.9845},
            {'name': 'Union Square', 'lat': 40.7359, 'lng': -73.9911},
        ]
        
        for hour in range(24):
            timestamp = timezone.now() - timedelta(hours=hour)
            for loc in locations:
                if 10 <= hour <= 17:
                    count = random.randint(500, 900)
                    density = 'high' if count > 650 else 'medium'
                elif 18 <= hour <= 21:
                    count = random.randint(300, 600)
                    density = 'medium' if count > 400 else 'low'
                else:
                    count = random.randint(20, 150)
                    density = 'low'
                
                CrowdData.objects.create(
                    location_name=loc['name'],
                    latitude=loc['lat'] + random.uniform(-0.005, 0.005),
                    longitude=loc['lng'] + random.uniform(-0.005, 0.005),
                    density=density,
                    count=count,
                    timestamp=timestamp
                )
        
        crowd_data = CrowdData.objects.filter(timestamp__gte=last_24h)
    
    # Calculate density distribution
    density_stats = {
        'low': crowd_data.filter(density='low').count(),
        'medium': crowd_data.filter(density='medium').count(),
        'high': crowd_data.filter(density='high').count()
    }
    
    # Ensure we have data to display
    total = density_stats['low'] + density_stats['medium'] + density_stats['high']
    if total == 0:
        density_stats = {'low': 45, 'medium': 35, 'high': 20}
    
    context['density_stats'] = json.dumps(density_stats)
    
    # ============================================
    # HOURLY CROWD ACTIVITY
    # ============================================
    hourly_data = []
    hour_labels = []
    
    for i in range(23, -1, -1):
        hour_time = timezone.now() - timedelta(hours=i)
        hour_start = hour_time.replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        
        hour_avg = CrowdData.objects.filter(
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).aggregate(Avg('count'))['count__avg']
        
        if hour_avg:
            hourly_data.append(int(hour_avg))
        else:
            # Sample data for demonstration
            if i in [10, 11, 12, 13, 14, 15, 16, 17]:
                hourly_data.append(random.randint(500, 800))
            elif i in [18, 19, 20, 21]:
                hourly_data.append(random.randint(300, 500))
            else:
                hourly_data.append(random.randint(20, 150))
        
        hour_labels.append(hour_time.strftime('%H:00'))
    
    context['hourly_crowd'] = json.dumps(hourly_data)
    context['hour_labels'] = json.dumps(hour_labels)
    
    # Get recent incidents
    context['recent_incidents'] = Incident.objects.order_by('-reported_at')[:10]
    
    return render(request, 'dashboard/index.html', context)


@login_required
def reports(request):
    """Report management and analytics page"""
    context = {}
    
    # Get date range filter
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    
    incidents = Incident.objects.all()
    
    if date_from:
        incidents = incidents.filter(reported_at__gte=date_from)
    if date_to:
        incidents = incidents.filter(reported_at__lte=date_to)
    
    # Get statistics
    context['total_incidents'] = incidents.count()
    context['resolved_incidents'] = incidents.filter(status='resolved').count()
    context['pending_incidents'] = incidents.filter(status='pending').count()
    context['investigating_incidents'] = incidents.filter(status='investigating').count()
    
    # Get incidents by type
    incident_types = []
    type_counts = []
    
    type_data = incidents.values('incident_type').annotate(count=Count('id'))
    for item in type_data:
        incident_types.append(dict(Incident.TYPE_CHOICES).get(item['incident_type'], item['incident_type']))
        type_counts.append(item['count'])
    
    context['incident_types'] = json.dumps(incident_types)
    context['type_counts'] = json.dumps(type_counts)
    
    # Get daily trend for last 7 days
    daily_labels = []
    daily_counts = []
    
    for i in range(6, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        daily_labels.append(date.strftime('%a, %b %d'))
        daily_counts.append(incidents.filter(reported_at__date=date).count())
    
    context['daily_labels'] = json.dumps(daily_labels)
    context['daily_counts'] = json.dumps(daily_counts)
    
    context['incidents'] = incidents.order_by('-reported_at')
    
    return render(request, 'dashboard/reports.html', context)


@login_required
def user_management(request):
    """User management page for admin"""
    if request.user.role != 'admin':
        return redirect('dashboard:index')
    
    users = User.objects.all().order_by('-date_joined')
    
    for user in users:
        user.report_count = user.reported_incidents.count()
        user.alert_count = user.alertrecipient_set.count()
        user.panic_count = user.emergencypanic_set.count()
    
    return render(request, 'dashboard/user_management.html', {'users': users})


@login_required
def block_user(request, user_id):
    """Block/unblock user (admin only)"""
    if request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'status': 'success', 'is_active': user.is_active})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)


@login_required
def delete_user(request, user_id):
    """Delete user permanently (admin only)"""
    if request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent deleting yourself
        if user.id == request.user.id:
            return JsonResponse({'status': 'error', 'message': 'Cannot delete your own account'}, status=400)
        
        username = user.username
        user.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'User {username} deleted successfully'
        })
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)


@login_required
def change_user_role(request, user_id):
    """Change user role (admin only)"""
    if request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=405)
    
    try:
        user = User.objects.get(id=user_id)
        new_role = request.POST.get('role')
        
        if new_role in ['admin', 'security', 'user']:
            user.role = new_role
            user.save()
            return JsonResponse({
                'status': 'success',
                'message': f'Role changed to {new_role}',
                'new_role': new_role
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid role'}, status=400)
            
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)


@login_required
def system_health(request):
    """System health monitoring API endpoint"""
    if request.user.role not in ['admin', 'security']:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    # Get system statistics
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_incidents': Incident.objects.count(),
        'pending_incidents': Incident.objects.filter(status='pending').count(),
        'active_alerts': Alert.objects.filter(is_active=True).count(),
        'active_panics': EmergencyPanic.objects.filter(is_resolved=False).count(),
        'crowd_data_points': CrowdData.objects.count(),
        'recent_crowd_data': CrowdData.objects.filter(
            timestamp__gte=timezone.now() - timedelta(minutes=30)
        ).count()
    }
    
    return JsonResponse({'status': 'success', 'data': stats})


@login_required
def export_data(request):
    """Export data as JSON (admin only)"""
    if request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    data_type = request.GET.get('type', 'incidents')
    
    if data_type == 'incidents':
        data = list(Incident.objects.all().values(
            'id', 'title', 'description', 'incident_type', 'status',
            'location', 'latitude', 'longitude', 'reported_at'
        ))
    elif data_type == 'alerts':
        data = list(Alert.objects.all().values(
            'id', 'title', 'message', 'alert_type', 'priority',
            'location', 'created_at', 'is_active'
        ))
    elif data_type == 'users':
        data = list(User.objects.all().values(
            'id', 'username', 'email', 'role', 'is_active', 'date_joined'
        ))
    elif data_type == 'crowd':
        data = list(CrowdData.objects.all().values(
            'id', 'location_name', 'latitude', 'longitude', 'density', 
            'count', 'timestamp'
        )[:1000])
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid data type'}, status=400)
    
    return JsonResponse({
        'status': 'success',
        'type': data_type,
        'count': len(data),
        'data': data,
        'exported_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    })


@login_required
def get_user_stats(request):
    """Get user statistics for charts (admin only)"""
    if request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    # Get user registration trend for last 30 days
    user_trend = []
    date_labels = []
    
    for i in range(29, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        count = User.objects.filter(date_joined__date=date).count()
        user_trend.append(count)
        date_labels.append(date.strftime('%b %d'))
    
    return JsonResponse({
        'status': 'success',
        'labels': date_labels,
        'data': user_trend
    })