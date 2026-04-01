# ai/urls.py
from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('', views.chat_page, name='chat_page'),
    path('api/chat/', views.chat_api, name='chat_api'),
] 
