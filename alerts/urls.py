# alerts/urls.py
from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('', views.index, name='index'),
    path('panic/', views.panic_button, name='panic'),
    path('send/', views.send_alert, name='send_alert'),
    path('get-alerts/', views.get_alerts, name='get_alerts'),
    path('mark-read/<int:alert_id>/', views.mark_alert_read, name='mark_read'),
    path('global/', views.get_global_alerts, name='global_alerts'),
    path('global/refresh/', views.refresh_global_alerts, name='refresh_global'),
]