from django.db import models
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
    """A picture is a photo or thumbnail of a scene."""

    EVENT_CHOICES = [
        ('scheduled', ''),
        ('manual', 'ssh or local terminal'),
        ('img analysis', ''),
        ('motion_detection', ''),
        ('other', 'other'),
    ]

    camera    = models.ForeignKey(Camera, models.PROTECT, help_text="The camera that has taken the picture.")
    picture   = models.ImageField(upload_to="pictures/")
    timestamp = models.DateTimeField(null=True, help_text="The time at which the camera took the picture.")  # TODO: Remove `null=True`
  # event     = models.CharField(max_length=12, choices=EVENT_CHOICES, help_text="The event that triggered the capture of this picture.")
  # quality   = Cam_original, cam_upload, thumbnail
