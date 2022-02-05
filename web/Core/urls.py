from django.urls import path
from Core.views import home, upload


app_name = 'core'

urlpatterns = [
    path('', home.homepage_view, name="home"),
    path('upload/', upload.upload_view, name="upload"),
]
