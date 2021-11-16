from django.contrib import admin
from Core.models import Camera, Picture


class CameraAdmin(admin.ModelAdmin):
    list_display = ('name', 'scene', 'notes')

admin.site.register(Camera, CameraAdmin)


class PictureAdmin(admin.ModelAdmin):
    list_display = ('camera', 'picture')

admin.site.register(Picture, PictureAdmin)
