# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('reports/', views.reports, name='reports'),
    path('users/', views.user_management, name='user_management'),
    path('block-user/<int:user_id>/', views.block_user, name='block_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-role/<int:user_id>/', views.change_user_role, name='change_role'),
    path('system-health/', views.system_health, name='system_health'),
    path('export-data/', views.export_data, name='export_data'),
    path('user-stats/', views.get_user_stats, name='user_stats'),
]