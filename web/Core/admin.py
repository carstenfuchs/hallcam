from django.contrib import admin
from Core.models import Camera, Picture


class CameraAdmin(admin.ModelAdmin):
    filter_horizontal = ['users']
    list_display = ('name', 'scene', 'notes', 'pwd')

admin.site.register(Camera, CameraAdmin)


class PictureAdmin(admin.ModelAdmin):
    list_display = ('camera', 'picture')

admin.site.register(Picture, PictureAdmin)
