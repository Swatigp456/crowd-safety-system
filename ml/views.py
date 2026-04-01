# ml/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import CrowdMLService
from monitoring.models import CrowdData
from incidents.models import Incident
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

ml_service = CrowdMLService()

@login_required
def dashboard(request):
    """ML Dashboard"""
    return render(request, 'ml/dashboard.html', {'now': datetime.now()})

@login_required
def train_crowd_model(request):
    """Train crowd prediction model"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    
    # Get historical crowd data
    crowd_data = CrowdData.objects.all().order_by('timestamp')[:1000]
    
    if crowd_data.count() < 10:
        return JsonResponse({
            'status': 'error', 
            'message': f'Need at least 10 crowd data points. Currently have {crowd_data.count()}'
        }, status=400)
    
    # Prepare training data
    historical = []
    for data in crowd_data:
        historical.append({
            'hour': data.timestamp.hour,
            'day_of_week': data.timestamp.weekday(),
            'location': data.location_name,
            'crowd_level': 0 if data.density == 'low' else (1 if data.density == 'medium' else 2),
            'previous_crowd': data.count
        })
    
    result = ml_service.train_crowd_predictor(historical)
    return JsonResponse(result)

@login_required
def train_incident_model(request):
    """Train incident classification model"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    
    # Get historical incident data
    incidents = Incident.objects.all().order_by('reported_at')[:500]
    
    if incidents.count() < 5:
        return JsonResponse({
            'status': 'error', 
            'message': f'Need at least 5 incidents. Currently have {incidents.count()}'
        }, status=400)
    
    # Prepare training data
    historical = []
    for incident in incidents:
        historical.append({
            'title': incident.title,
            'description': incident.description,
            'incident_type': incident.incident_type,
            'hour': incident.reported_at.hour
        })
    
    result = ml_service.train_incident_classifier(historical)
    return JsonResponse(result)

@login_required
def train_anomaly_model(request):
    """Train anomaly detection model"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    
    # Get normal crowd data (low to medium density)
    normal_data = CrowdData.objects.filter(
        density__in=['low', 'medium']
    ).order_by('timestamp')[:500]
    
    if normal_data.count() < 5:
        return JsonResponse({
            'status': 'error', 
            'message': f'Need at least 5 normal data points. Currently have {normal_data.count()}'
        }, status=400)
    
    # Prepare training data
    training_data = []
    for data in normal_data:
        training_data.append({
            'crowd_count': data.count,
            'hour': data.timestamp.hour,
            'day_of_week': data.timestamp.weekday()
        })
    
    result = ml_service.train_anomaly_detector(training_data)
    return JsonResponse(result)

@login_required
def predict_crowd(request):
    """Predict crowd density for a location"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        hour = data.get('hour', datetime.now().hour)
        day_of_week = data.get('day_of_week', datetime.now().weekday())
        location = data.get('location', 'Unknown')
        previous_crowd = data.get('previous_crowd', 0)
        
        result = ml_service.predict_crowd_density(hour, day_of_week, location, previous_crowd)
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@csrf_exempt
def classify_incident(request):
    """Classify an incident from description"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        title = data.get('title', '')
        description = data.get('description', '')
        hour = data.get('hour', datetime.now().hour)
        
        result = ml_service.classify_incident(title, description, hour)
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def detect_anomaly(request):
    """Detect anomaly in crowd data"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        crowd_count = data.get('crowd_count', 0)
        hour = data.get('hour', datetime.now().hour)
        day_of_week = data.get('day_of_week', datetime.now().weekday())
        
        result = ml_service.detect_anomaly(crowd_count, hour, day_of_week)
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def get_model_status(request):
    """Get status of ML models"""
    models_status = {
        'crowd_predictor': ml_service.crowd_predictor is not None,
        'incident_classifier': ml_service.incident_classifier is not None,
        'anomaly_detector': ml_service.anomaly_detector is not None,
        'total_data_points': CrowdData.objects.count(),
        'total_incidents': Incident.objects.count()
    }
    
    return JsonResponse({'status': 'success', 'models': models_status})