# monitoring/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CrowdData
from datetime import datetime, timedelta
import json
import requests
from django.db.models import Q

@login_required
def index(request):
    return render(request, 'monitoring/index.html')

@login_required
def get_user_location(request):
    """Get user's actual location"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = data.get('latitude')
            lng = data.get('longitude')
            if lat and lng:
                return JsonResponse({
                    'status': 'success',
                    'location': {
                        'latitude': lat,
                        'longitude': lng,
                        'source': 'GPS',
                        'accuracy': 'High (GPS)'
                    }
                })
        except:
            pass
    
    # Get location from IP
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({
                'status': 'success',
                'location': {
                    'latitude': data.get('latitude', 28.6139),
                    'longitude': data.get('longitude', 77.2090),
                    'city': data.get('city', 'Delhi'),
                    'source': 'IP',
                    'accuracy': 'Approximate'
                }
            })
    except:
        pass
    
    return JsonResponse({
        'status': 'success',
        'location': {
            'latitude': 28.6139,
            'longitude': 77.2090,
            'city': 'Delhi',
            'source': 'Default',
            'accuracy': 'Default'
        }
    })

@login_required
def get_crowd_data(request):
    """Get real-time crowd data"""
    # Get data from last 30 minutes
    time_threshold = datetime.now() - timedelta(minutes=30)
    crowd_data = CrowdData.objects.filter(
        timestamp__gte=time_threshold
    ).order_by('-timestamp')[:50]  # Get latest 50 points
    
    data = []
    for item in crowd_data:
        data.append({
            'id': item.id,
            'lat': float(item.latitude),
            'lng': float(item.longitude),
            'density': item.density,
            'count': item.count,
            'location': item.location_name,
            'timestamp': item.timestamp.strftime('%H:%M:%S')
        })
    
    # If no data, return sample data
    if not data:
        data = get_sample_crowd_data()
    
    return JsonResponse({
        'status': 'success',
        'count': len(data),
        'data': data
    })

def get_sample_crowd_data():
    """Return sample crowd data if database is empty"""
    return [
        {'lat': 28.6139, 'lng': 77.2090, 'density': 'high', 'count': 847, 'location': 'Connaught Place'},
        {'lat': 28.6328, 'lng': 77.2180, 'density': 'medium', 'count': 423, 'location': 'Rajiv Chowk'},
        {'lat': 28.5900, 'lng': 77.2200, 'density': 'low', 'count': 156, 'location': 'Lodhi Garden'},
        {'lat': 28.6200, 'lng': 77.2000, 'density': 'high', 'count': 654, 'location': 'Market Area'},
        {'lat': 28.6000, 'lng': 77.2300, 'density': 'medium', 'count': 345, 'location': 'Business District'},
        {'lat': 28.6400, 'lng': 77.2100, 'density': 'high', 'count': 512, 'location': 'India Gate'},
        {'lat': 28.5800, 'lng': 77.1900, 'density': 'low', 'count': 89, 'location': 'Residential Area'},
    ]

@login_required
def get_heatmap_data(request):
    """Get data for heatmap visualization"""
    time_threshold = datetime.now() - timedelta(minutes=30)
    crowd_data = CrowdData.objects.filter(timestamp__gte=time_threshold)
    
    heatmap_data = []
    for item in crowd_data:
        weight = 1
        if item.density == 'medium':
            weight = 2
        elif item.density == 'high':
            weight = 3
        
        heatmap_data.append([
            float(item.latitude),
            float(item.longitude),
            weight
        ])
    
    if not heatmap_data:
        heatmap_data = [
            [28.6139, 77.2090, 3],
            [28.6328, 77.2180, 2],
            [28.5900, 77.2200, 1],
            [28.6200, 77.2000, 3],
            [28.6000, 77.2300, 2],
        ]
    
    return JsonResponse({'heatmap_data': heatmap_data})

@login_required
def get_safe_routes(request):
    """Get safe routes based on user location"""
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    
    if not user_lat or not user_lng:
        return JsonResponse({'safe_routes': []})
    
    try:
        user_lat = float(user_lat)
        user_lng = float(user_lng)
    except:
        return JsonResponse({'safe_routes': []})
    
    # Find safe zones (low density areas within 2km)
    safe_zones = CrowdData.objects.filter(
        density='low',
        timestamp__gte=datetime.now() - timedelta(minutes=30)
    )
    
    routes = []
    for zone in safe_zones:
        # Calculate distance
        distance = calculate_distance(
            user_lat, user_lng,
            float(zone.latitude), float(zone.longitude)
        )
        
        # Only show zones within 2km
        if distance < 2000:
            routes.append({
                'latitude': float(zone.latitude),
                'longitude': float(zone.longitude),
                'location': zone.location_name,
                'distance': round(distance),
                'people_count': zone.count,
                'safety_score': calculate_safety_score(zone.density, zone.count)
            })
    
    # Sort by distance
    routes.sort(key=lambda x: x['distance'])
    
    # If no safe zones found, return sample
    if not routes:
        routes = [
            {
                'latitude': 28.5900,
                'longitude': 77.2200,
                'location': 'Lodhi Garden (Safe Zone)',
                'distance': 1200,
                'people_count': 156,
                'safety_score': 95
            },
            {
                'latitude': 28.5800,
                'longitude': 77.1900,
                'location': 'South Extension (Low Crowd)',
                'distance': 1800,
                'people_count': 89,
                'safety_score': 92
            }
        ]
    
    return JsonResponse({'safe_routes': routes[:5]})  # Return top 5 safe routes

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters"""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def calculate_safety_score(density, count):
    """Calculate safety score based on crowd density"""
    if density == 'low':
        return 95
    elif density == 'medium':
        return 70
    else:
        return 40

@login_required
@csrf_exempt
def update_crowd_data(request):
    """Update crowd data from AI detection"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            CrowdData.objects.create(
                location_name=data.get('location_name', 'Detected Area'),
                latitude=data.get('latitude', 0),
                longitude=data.get('longitude', 0),
                density=data.get('density', 'medium'),
                count=data.get('count', 100),
                timestamp=datetime.now()
            )
            return JsonResponse({'status': 'success', 'message': 'Data updated'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'POST only'})
# monitoring/views.py - Add this to your existing index view

@login_required
def index(request):
    """Live monitoring with map - supports lat/lng parameters"""
    
    # Get coordinates from URL parameters
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    zoom = request.GET.get('zoom', 15)
    location_name = request.GET.get('location', '')
    
    context = {
        'initial_lat': lat,
        'initial_lng': lng,
        'initial_zoom': zoom,
        'location_name': location_name
    }
    
    return render(request, 'monitoring/index.html', context)
# Add this to your existing monitoring/views.py

@login_required
def index(request):
    """Live monitoring with map - supports lat/lng parameters"""
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    zoom = request.GET.get('zoom', 15)
    location_name = request.GET.get('location', '')
    
    context = {
        'initial_lat': lat,
        'initial_lng': lng,
        'initial_zoom': zoom,
        'location_name': location_name
    }
    return render(request, 'monitoring/index.html', context)
# monitoring/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CrowdData
from datetime import datetime, timedelta
import json
import requests
import random

@login_required
def index(request):
    """Live monitoring with map - supports alert location parameters"""
    
    # Get coordinates from URL parameters (for alert location)
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    zoom = request.GET.get('zoom', 14)
    location_name = request.GET.get('location', '')
    show_alert = request.GET.get('showAlert', 'false')
    
    context = {
        'alert_lat': lat,
        'alert_lng': lng,
        'alert_zoom': zoom,
        'alert_location': location_name,
        'show_alert': show_alert == 'true'
    }
    
    return render(request, 'monitoring/index.html', context)

# ... rest of your existing views (get_crowd_data, get_heatmap_data, etc.)
# monitoring/views.py - Add this function if not exists
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CrowdData
from datetime import datetime, timedelta
import json
import random

@login_required
def index(request):
    """Live monitoring with map - supports alert location parameters"""
    # Get coordinates from URL parameters
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    zoom = request.GET.get('zoom', 15)
    location_name = request.GET.get('location', '')
    
    context = {
        'alert_lat': lat,
        'alert_lng': lng,
        'alert_zoom': zoom,
        'alert_location': location_name,
        'show_alert': lat and lng
    }
    return render(request, 'monitoring/index.html', context)

# Keep your other views (get_crowd_data, get_heatmap_data, etc.)