from django.core.files.storage import default_storage
from django.db import models
from pathlib import Path
from PIL import Image

from Accounts.models import User


class Camera(models.Model):
    name  = models.CharField(max_length=40, unique=True)
    pwd   = models.CharField(max_length=80, verbose_name="password", help_text="The password that the camera must use in the picture upload form.")
    scene = models.CharField(max_length=80)
    notes = models.CharField(max_length=80, blank=True)
    users = models.ManyToManyField(User, blank=True, help_text="Who can see this camera's pictures?")

    def __str__(self):
        return f"{self.name} ({self.scene})"


class Picture(models.Model):
    """A picture is a photo of a scene along with related metadata."""

    PICTURES_SUBDIR = 'pictures'
    THUMBNAILS_SUBDIR = 'thumbs'
    VALID_SUFFIXES = ('.jpg', '.png', '.gif', '.jpeg')

    EVENT_CHOICES = [
        ('scheduled', ''),
        ('manual', 'ssh or local terminal'),
        ('img analysis', ''),
        ('motion_detection', ''),
        ('other', 'other'),
    ]

    camera    = models.ForeignKey(Camera, models.PROTECT, help_text="The camera that has taken the picture.")
    filename  = models.CharField(max_length=48, unique=True)
    timestamp = models.DateTimeField(help_text="The time at which the camera took the picture.")
  # event     = models.CharField(max_length=12, choices=EVENT_CHOICES, help_text="The event that triggered the capture of this picture.")
  # quality   = Cam_original, cam_upload, thumbnail
  # temperature, time-to-upload, …

    def get_image_url(self):
        return default_storage.base_url + f"{self.PICTURES_SUBDIR}/{self.filename}"

    def get_thumb_url(self):
        pic_path   = Path(default_storage.location, self.PICTURES_SUBDIR,   self.filename)
        thumb_path = Path(default_storage.location, self.THUMBNAILS_SUBDIR, self.filename).with_suffix('.jpg')

        # print("get_thumb_url()")
        # print(f"--> {pic_path = }")
        # print(f"--> {pic_path.exists() = }")
        # print(f"--> {thumb_path = }")
        # print(f"--> {thumb_path.exists() = }")

        # If the thumbnail image does not yet exist, create it now.
        if not thumb_path.exists():
            assert thumb_path.parent.exists()
            try:
                with Image.open(pic_path) as img:
                    if img.mode != 'RGB':
                        # Make sure that PNG images with a palette are converted to RGB.
                        img = img.convert('RGB')
                    img.thumbnail((400, 300), resample=Image.LANCZOS)
                    img.save(thumb_path, 'JPEG')
            except FileNotFoundError as e:
                print("Picture.get_thumb_url() --> ", e)

        return default_storage.base_url + str(thumb_path.relative_to(default_storage.location))
