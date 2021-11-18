from django.urls import path
from Core.views import upload, viewer


app_name = 'core'

urlpatterns = [
    path('upload/', upload.upload_view, name="upload"),
    path('viewer/', viewer.viewer_view, name="viewer"),
]
