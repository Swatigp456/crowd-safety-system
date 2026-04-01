# monitoring/urls.py
from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/crowd-data/', views.get_crowd_data, name='crowd_data'),
    path('api/heatmap-data/', views.get_heatmap_data, name='heatmap_data'),
    path('api/safe-routes/', views.get_safe_routes, name='safe_routes'),
    path('api/update-crowd-data/', views.update_crowd_data, name='update_crowd_data'),
    path('api/user-location/', views.get_user_location, name='user_location'),
]