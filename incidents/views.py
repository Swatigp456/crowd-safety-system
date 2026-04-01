# incidents/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import Incident, IncidentComment
from .validation_service import IncidentValidationService
from django.utils import timezone
import json
import os

@login_required
def index(request):
    """Display all incidents"""
    incidents = Incident.objects.all().order_by('-reported_at')
    paginator = Paginator(incidents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'incidents/index.html', {'incidents': page_obj})

@login_required
def report_incident(request):
    """Report a new incident with validation"""
    if request.method == 'POST':
        try:
            print("=== INCIDENT REPORT SUBMITTED ===")
            
            # Get data from POST
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            incident_type = request.POST.get('incident_type', 'other')
            location = request.POST.get('location', '')
            latitude = request.POST.get('latitude', 0)
            longitude = request.POST.get('longitude', 0)
            
            # Validate required fields
            if not title or not description:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': 'Title and description are required'}, status=400)
                else:
                    messages.error(request, 'Title and description are required')
                    return redirect('incidents:report')
            
            # Create incident object
            incident = Incident(
                title=title,
                description=description,
                incident_type=incident_type,
                location=location,
                latitude=latitude,
                longitude=longitude,
                reported_by=request.user
            )
            
            # Handle image upload
            if 'image' in request.FILES:
                incident.image = request.FILES['image']
                print("Image uploaded:", request.FILES['image'].name)
            
            # Handle video upload
            if 'video' in request.FILES:
                incident.video = request.FILES['video']
                print("Video uploaded:", request.FILES['video'].name)
            
            # Save to database first
            incident.save()
            print(f"Incident saved with ID: {incident.id}")
            
            # Run validation
            print("Running validation checks...")
            validator = IncidentValidationService(incident)
            validation_result = validator.validate()
            
            print(f"Validation result: Score={validation_result['score']}, Is Fraud={validation_result['is_fraud']}")
            
            # Return success response with validation info
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success', 
                    'incident_id': incident.id,
                    'message': 'Incident reported successfully!',
                    'validation': {
                        'score': validation_result['score'],
                        'is_fraud': validation_result['is_fraud'],
                        'status': validation_result['status']
                    }
                })
            else:
                if validation_result['is_fraud']:
                    messages.warning(request, f'Incident reported but marked as potentially false (Confidence: {validation_result["score"]}%)')
                else:
                    messages.success(request, f'Incident reported successfully! (Confidence: {validation_result["score"]}%)')
                return redirect('incidents:detail', incident_id=incident.id)
                
        except Exception as e:
            print(f"Error saving incident: {e}")
            import traceback
            traceback.print_exc()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error', 
                    'message': str(e)
                }, status=400)
            else:
                messages.error(request, f'Error: {str(e)}')
                return redirect('incidents:report')
    
    return render(request, 'incidents/report.html')

@login_required
def incident_detail(request, incident_id):
    """View incident details"""
    incident = get_object_or_404(Incident, id=incident_id)
    comments = incident.comments.all().order_by('-created_at')
    
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            IncidentComment.objects.create(
                incident=incident,
                user=request.user,
                comment=comment_text
            )
            messages.success(request, 'Comment added successfully!')
            return redirect('incidents:detail', incident_id=incident_id)
    
    return render(request, 'incidents/detail.html', {
        'incident': incident,
        'comments': comments
    })

@login_required
def update_incident_status(request, incident_id):
    """Update incident status (admin/security only)"""
    if request.method == 'POST' and request.user.role in ['admin', 'security']:
        incident = get_object_or_404(Incident, id=incident_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Incident.STATUS_CHOICES):
            incident.status = new_status
            if new_status == 'resolved':
                incident.resolved_at = timezone.now()
            incident.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            else:
                messages.success(request, 'Incident status updated!')
                return redirect('incidents:detail', incident_id=incident_id)
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def validate_incident(request, incident_id):
    """Manually validate or reject an incident (admin only)"""
    if request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        incident = get_object_or_404(Incident, id=incident_id)
        action = request.POST.get('action')
        
        if action == 'verify':
            incident.validation_status = 'verified'
            incident.is_fraud = False
            incident.confidence_score = 100
            incident.validated_by = request.user
            incident.validated_at = timezone.now()
            incident.validation_notes = f"Manually verified by {request.user.username}"
            incident.save()
            messages.success(request, f'Incident #{incident_id} marked as VERIFIED')
        elif action == 'reject':
            incident.validation_status = 'rejected'
            incident.is_fraud = True
            incident.confidence_score = 0
            incident.validated_by = request.user
            incident.validated_at = timezone.now()
            reason = request.POST.get('reason', 'Manually rejected by admin')
            incident.validation_notes = f"Rejected by {request.user.username}: {reason}"
            incident.fraud_reason = reason
            incident.save()
            messages.warning(request, f'Incident #{incident_id} marked as FALSE REPORT')
        elif action == 'revalidate':
            # Run validation again
            validator = IncidentValidationService(incident)
            result = validator.validate()
            incident.save()
            messages.info(request, f'Incident #{incident_id} revalidated. Score: {result["score"]}%')
        
        return redirect('incidents:detail', incident_id=incident_id)
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def api_get_incidents(request):
    """API endpoint to get incidents"""
    incidents = Incident.objects.all().order_by('-reported_at')
    
    incidents_data = []
    for incident in incidents:
        incidents_data.append({
            'id': incident.id,
            'title': incident.title,
            'description': incident.description[:100],
            'incident_type': incident.incident_type,
            'incident_type_display': incident.get_incident_type_display(),
            'status': incident.status,
            'status_display': incident.get_status_display(),
            'location': incident.location,
            'latitude': float(incident.latitude),
            'longitude': float(incident.longitude),
            'reported_by': incident.reported_by.username,
            'reported_at': incident.reported_at.strftime('%Y-%m-%d %H:%M:%S'),
            'has_image': bool(incident.image),
            'has_video': bool(incident.video),
            'validation_status': incident.validation_status,
            'confidence_score': incident.confidence_score,
            'is_fraud': incident.is_fraud
        })
    
    return JsonResponse({'incidents': incidents_data})