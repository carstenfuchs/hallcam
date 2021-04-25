from django.urls import path
from .views import welcome


app_name = 'viewer'

urlpatterns = [
    path('', welcome.view, name='welcome'),
]
