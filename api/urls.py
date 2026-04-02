from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('crowd-data/', views.CrowdDataAPI.as_view(), name='crowd_data'),
    path('alerts/', views.AlertsAPI.as_view(), name='alerts'),
    path('incidents/', views.IncidentsAPI.as_view(), name='incidents'),
    path('users/', views.UsersAPI.as_view(), name='users'),
]
