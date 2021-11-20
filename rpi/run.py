#!/usr/bin/env python3
import os
import requests
from time import sleep
from picamera import PiCamera

import localconfig


PICTURES_DIR = '/var/HallCam/pictures/'

if not os.access(PICTURES_DIR, os.W_OK):
    print(f"Cannot access {PICTURES_DIR}.")
else:
    print(f"Access to {PICTURES_DIR} is good.")

print(f"localconfig.UPLOAD_URL = {localconfig.UPLOAD_URL}")
print("")


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

    if localconfig.UPLOAD_URL:
        with open(filename, 'rb') as pic_file:
            try:
                r = requests.post(
                    localconfig.UPLOAD_URL,
                    files={'pic_file': pic_file},
                    allow_redirects=False,
                    timeout=10.0,
                )
                print(f"Uploaded picture to {localconfig.UPLOAD_URL}")
                if r.status_code != 302:
                    print(f"Unexpected response: Expected status_code 302, got status_code {r.status_code}.")
                    print(r)
                    print(r.text)
            except requests.exceptions.Timeout as e:
                print(f"Requests raised a timeout exception: {e}")
            except requests.exceptions.RequestException as e:
                print(f"Requests raised an exception: {e}")

camera.stop_preview()
