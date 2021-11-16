from django.db import models


class Camera(models.Model):
    name  = models.CharField(max_length=40)
    scene = models.CharField(max_length=80)
    notes = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return f"{self.name} ({self.scene})"


class Picture(models.Model):
    """A picture is a photo or thumbnail of a scene."""

    camera  = models.ForeignKey(Camera, models.PROTECT, help_text="The camera that has taken the picture.")
    picture = models.ImageField(upload_to="pictures/")
