from django.db import models


class Camera(models.Model):
    name  = models.CharField(max_length=40, unique=True)
    scene = models.CharField(max_length=80)
    notes = models.CharField(max_length=80, blank=True)

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
  # timestamp = models.DateTimeField(help_text="The time at which the camera took the picture.")
  # event     = models.CharField(max_length=12, choices=EVENT_CHOICES, help_text="The event that triggered the capture of this picture.")
  # quality   = Cam_original, cam_upload, thumbnail
