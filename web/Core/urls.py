from django.urls import path
from Core.views import home, stats, upload


app_name = 'core'

urlpatterns = [
    path('', home.homepage_view, name="home"),
    path('statistics/', stats.view, name="stats"),
    path('upload/', upload.upload_view, name="upload"),
]
