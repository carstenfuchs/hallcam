#!/usr/bin/env python3
import os
from time import sleep
from picamera import PiCamera


PICTURES_DIR = '/var/HallCam/pictures/'

if not os.access(PICTURES_DIR, os.W_OK):
    print(f"Cannot access {PICTURES_DIR}.")
else:
    print(f"Access to {PICTURES_DIR} is good.")


camera = PiCamera()
camera.rotation = 180

# The maximum resolution is 2592×1944 for still photos, and 1920×1080 for video recording.
# We also need to set the frame rate to 15 to enable this maximum resolution.
# The minimum resolution is 64×64.
CAMERA_MIN_RESOLUTION = (64, 64)
CAMERA_MAX_RESOLUTION = (2592, 1944)

# camera.resolution = CAMERA_MAX_RESOLUTION
# camera.framerate = 15

# camera.annotate_background = Color('blue')
# camera.annotate_foreground = Color('yellow')
camera.annotate_text = "Hallo!  :-)"
camera.annotate_text_size = 20  # 6 … 160, default is 32.

camera.start_preview()

for i in range(5):
    sleep(5)
    filename = f'{PICTURES_DIR}/image_{i:03d}.jpg'
    camera.capture(filename)
    print(f"Captured {filename}")

camera.stop_preview()
