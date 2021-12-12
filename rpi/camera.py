from datetime import datetime
from picamera import PiCamera, Color
from common import get_pic_stem_from_data


class Camera:
    """This is a wrapper around the `PiCamera`."""

    # The maximum resolution is 3280×2464 for still photos, 1920×1080 for video recording.
    # We also need to set the frame rate to at most 15 to enable this maximum resolution.
    # The minimum resolution is 64×64.
    # https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
    CAMERA_MIN_RESOLUTION = (64, 64)
    CAMERA_LOW_RESOLUTION = (640, 480)
    CAMERA_MED_RESOLUTION = (1640, 1232)
  # CAMERA_MAX_RESOLUTION = (2592, 1944)    # camera v1
    CAMERA_MAX_RESOLUTION = (3280, 2464)    # camera v2

    def __init__(self):
        self.pi_cam = PiCamera()
        self.pi_cam.rotation = 180

        self.pi_cam.resolution = self.CAMERA_MED_RESOLUTION
        self.pi_cam.framerate = 5

        self.pi_cam.annotate_background = Color('#777')
        # self.pi_cam.annotate_foreground = Color('yellow')
        # self.pi_cam.annotate_text = "Hallo!  :-)"
        self.pi_cam.annotate_text_size = 18  # 6 … 160, default is 32.

        self.last_action_time = datetime(2000, 1, 1)
        self.last_action_impt = 0

    def capture_picture(self, now, importance, pictures_dir):
        if (now - self.last_action_time).total_seconds() < 10.0:
            if importance <= self.last_action_impt:
                print("Skipping action, throttling.")
                return

        self.last_action_time = now
        self.last_action_impt = importance

        filename = f'{pictures_dir}/{get_pic_stem_from_data(now, importance)}.jpg'

        print(f"Capturing picture, saving to {filename} ...")
        self.pi_cam.annotate_text = now.strftime(' %Y-%m-%d %H:%M:%S ')
        self.pi_cam.capture(filename)
        return filename
