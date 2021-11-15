from django.urls import path
from Core.views import upload


app_name = 'core'

urlpatterns = [
    path('upload/', upload.upload_view, name="upload"),
]
