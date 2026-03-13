from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('gemini/', views.gemini_chat, name='gemini_chat'),
    path('health/', views.health_check, name='health_check'),
]

