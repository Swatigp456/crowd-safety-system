# ml/urls.py
from django.urls import path
from . import views

app_name = 'ml'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('train-crowd/', views.train_crowd_model, name='train_crowd'),
    path('train-incident/', views.train_incident_model, name='train_incident'),
    path('train-anomaly/', views.train_anomaly_model, name='train_anomaly'),
    path('predict-crowd/', views.predict_crowd, name='predict_crowd'),
    path('classify-incident/', views.classify_incident, name='classify_incident'),
    path('detect-anomaly/', views.detect_anomaly, name='detect_anomaly'),
    path('model-status/', views.get_model_status, name='model_status'),
]