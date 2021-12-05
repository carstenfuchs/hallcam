from datetime import datetime
from picamera import PiCamera
from common import get_pic_stem_from_data


class Camera:
    """This is a wrapper around the `PiCamera`."""

    # The maximum resolution is 2592×1944 for still photos, 1920×1080 for video recording.
    # We also need to set the frame rate to 15 to enable this maximum resolution.
    # The minimum resolution is 64×64.
    CAMERA_MIN_RESOLUTION = (64, 64)
    CAMERA_LOW_RESOLUTION = (640, 480)
    CAMERA_MED_RESOLUTION = (1600, 900)
    CAMERA_MAX_RESOLUTION = (2592, 1944)

    def __init__(self):
        self.pi_cam = PiCamera()
        self.pi_cam.rotation = 180

        self.pi_cam.resolution = self.CAMERA_MED_RESOLUTION
        self.pi_cam.framerate = 15

        # self.pi_cam.annotate_background = Color('blue')
        # self.pi_cam.annotate_foreground = Color('yellow')
        # self.pi_cam.annotate_text = "Hallo!  :-)"
        # self.pi_cam.annotate_text_size = 20  # 6 … 160, default is 32.

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
        self.pi_cam.annotate_text = now.strftime('%Y-%m-%d %H:%M:%S')
        self.pi_cam.capture(filename)
        return filename
