# api/urls.py
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Real-time alerts
    path('alerts/', views.RealTimeAlertAPI.as_view(), name='alerts'),
    path('alerts/<int:alert_id>/acknowledge/', views.AlertAcknowledgementAPI.as_view(), name='acknowledge_alert'),
    
    # Real-time crowd data
    path('crowd/', views.RealTimeCrowdAPI.as_view(), name='crowd_data'),
    
    # Emergency panic
    path('panic/', views.EmergencyPanicAPI.as_view(), name='panic'),
    # api/urls.py
    
]