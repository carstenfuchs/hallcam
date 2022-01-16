from django.urls import path
from Core.views import home, upload, viewer


app_name = 'core'

urlpatterns = [
    path('', home.homepage_view, name="home"),
    path('upload/', upload.upload_view, name="upload"),
    path('viewer/', viewer.viewer_view, name="viewer"),
]
