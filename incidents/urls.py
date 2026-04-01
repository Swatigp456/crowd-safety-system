# incidents/urls.py
from django.urls import path
from . import views

app_name = 'incidents'

urlpatterns = [
    path('', views.index, name='index'),
    path('report/', views.report_incident, name='report'),
    path('<int:incident_id>/', views.incident_detail, name='detail'),
    path('<int:incident_id>/update-status/', views.update_incident_status, name='update_status'),
    path('<int:incident_id>/validate/', views.validate_incident, name='validate_incident'),
    path('api/get-incidents/', views.api_get_incidents, name='api_get_incidents'),
]