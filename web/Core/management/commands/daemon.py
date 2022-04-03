import socket
from time import sleep
from backports.zoneinfo import ZoneInfo

from dateutil import parser, tz
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.utils import timezone
import requests

from Core.libs.pictures import cleanup_pictures, get_pic_stem_from_data
from Core.models import Camera, Picture
from Core.views.upload import save_to_disk


class Task:
    """This class models a task that is periodically run by the daemon."""

    def is_due(self, dt0, dt1):
        """Returns whether the task is due to be run."""
        return False

    def run_action(self):
        """Called whenever the task is due, this method implements the action."""
        pass


class TaskPickupExternalImage(Task):

    def __init__(self):
        # `latest_dt` is the timestamp of the most recently downloaded image.
        self.latest_dt = timezone.now()

    def is_due(self, dt0, dt1):
        """Every 5 minutes, offset by 1 minute."""
        ts0 = dt0.timestamp()
        ts1 = dt1.timestamp()
        ofs = 60

        return ((ts0 - ofs) // 300) < ((ts1 - ofs) // 300)

    def run_action(self):
        for cam in Camera.objects.filter(pwd__startswith="pick up "):
            url = cam.pwd[8:]

            if not url.lower().endswith(".jpg"):
                print(f"Warning: URL {url} does not end with .jpg")

            # TODO: First use HTTP HEAD for checking the `last-modified` header,
            #       only then load the contents with HTTP GET?
            # TODO: Use PIL to verify that the image is valid?
            try:
                r = requests.get(url, timeout=20.0)
            except requests.exceptions.Timeout as e:
                print(str(e))
                return

            try:
                # About converting from GMT to local time, see:
                # https://stackoverflow.com/questions/4563272/how-to-convert-a-utc-datetime-to-a-local-datetime-using-only-standard-library
                lm = r.headers.get('last-modified', '')
                dt = parser.parse(lm).astimezone(ZoneInfo('localtime'))
            except parser.ParserError as e:
                print(str(e))
                return

            # print(f"{self.latest_dt = }, {lm = }, {dt = }")
            if dt <= self.latest_dt:
                return

            self.latest_dt = dt

            path_name = get_pic_stem_from_data(dt, 6 if dt.minute <= 2 else 4) + ".jpg"
            suf = SimpleUploadedFile(path_name, r.content, content_type="image/jpeg")
            save_to_disk(cam, suf)

            # If a picture with the given filename already exists, the file on disk is
            # overwritten and the related `Picture` object is updated rather than created
            # (the `filename` must be unique).
            Picture.objects.update_or_create(
                filename=path_name,
                defaults={
                    'camera': cam,
                    'timestamp': dt,
                }
            )


class TaskCleanupDisk(Task):

    def is_due(self, dt0, dt1):
        """Only on Monday mornings at 3:00 o'clock."""
        if dt1.isoweekday() != 1:
            return False

        # Note that this is oversimplified: If `dt0` and `dt1` were spaced very
        # far apart, we might miss due dates.
        return dt0.hour < 3 <= dt1.hour

    def run_action(self):
        cleanup_pictures(hot_run=True)


class Command(BaseCommand):
    help = "Run as a system service, this command performs recurrent tasks."

    def handle(self, *args, **options):
        lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

        try:
            # The null byte (\0) means the socket is created in the abstract
            # namespace instead of being created on the file system itself.
            # https://stackoverflow.com/questions/788411/check-to-see-if-python-script-is-running
            lock_socket.bind('\0' + 'HallCam_website')
        except socket.error:
            print("The HallCam website daemon is already running.")
            return

        # We got the lock.
        tasks = [
            TaskPickupExternalImage(),
            TaskCleanupDisk(),
        ]

        try:
            prev_dt = timezone.now()

            while True:
                curr_dt = timezone.now()

                for task in tasks:
                    if task.is_due(prev_dt, curr_dt):
                        print(f"Running {task.__class__.__name__} at {curr_dt}.")
                        task.run_action()

                prev_dt = curr_dt
                sleep(1)

        except KeyboardInterrupt:
            print("Exiting ...")
