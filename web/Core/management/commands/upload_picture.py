import argparse
from backports.zoneinfo import ZoneInfo
from datetime import date, datetime, timedelta
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from Core.models import Camera, Picture
from Core.views.upload import save_to_disk


# von https://stackoverflow.com/questions/25470844/specify-format-for-input-arguments-argparse-python
def valid_time(s):
    try:
        return datetime.strptime(s, "%H:%M").time()
    except ValueError:
        msg = "Kein gültige Zeitangabe: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


class Command(BaseCommand):
    help = "Uploads a picture, just as a camera does."

    def add_arguments(self, parser):
        parser.add_argument("camera", help="The name of the camera to upload the picture for.")
        parser.add_argument("time", type=valid_time, help="The time at which the picture was taken.")
        parser.add_argument("filename", help="The name of the picture file to upload.")
        #parser.add_argument("--hot-run", action="store_true", help="Actually update the database and delete files!")

    def handle(self, *args, **options):
        print("")
        try:
            cam = Camera.objects.get(name=options['camera'])
            print(cam)
        except:
            print("A camera with this name does not exist.")
            return

        dt = datetime.combine(date.today(), options['time'], tzinfo=ZoneInfo('Europe/Berlin'))
        if dt > timezone.now():
            dt -= timedelta(days=1)
        print(dt)

        path = Path(options['filename'])
        print(path, path.name)

        with open(path, 'rb') as source_file:
            suf = SimpleUploadedFile(path.name, source_file.read(), content_type="image/jpeg")
            save_to_disk(cam, suf)

        # If a picture with the given filename already exists, the file on
        # disk is overwritten and the related `Picture` object is updated
        # rather than created (the `filename` must be unique).
        Picture.objects.update_or_create(
            filename=path.name,
            defaults={
                'camera': cam,
                'timestamp': dt,
            }
        )
