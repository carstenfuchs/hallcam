#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from time import sleep
from picamera import PiCamera

import localconfig


class CaptureHandler:

    def __init__(self, pictures_dir, upload_url):
        self.pictures_dir = pictures_dir
        self.upload_url = upload_url
        self.last_action_time = datetime(2000, 1, 1)
        self.last_action_impt = 0

    def upload_picture(self, filename):
        if not self.upload_url:
            return

        with open("/sys/class/thermal/thermal_zone0/temp") as temp_file:
            # https://www.elektronik-kompendium.de/sites/raspberry-pi/1911241.htm
            # https://raspberrypi.stackexchange.com/questions/41784/temperature-differences-between-cpu-gpu
            cpu_temp = temp_file.readline().strip()

        with open(filename, 'rb') as pic_file:
            try:
                r = requests.post(
                    self.upload_url,
                    data={
                        'camera': localconfig.CAMERA_NAME,
                        'password': localconfig.CAMERA_UPLOAD_PASSWORD,
                        'cpu_temp': cpu_temp,
                    },
                    files={'pic_file': pic_file},
                    allow_redirects=False,
                    timeout=10.0,
                )
                print(f"Uploaded picture to {self.upload_url}")
                if r.status_code != 302:
                    print(f"Unexpected response: Expected status_code 302, got status_code {r.status_code}.")
                    print(r)
                    print(r.text)
            except requests.exceptions.Timeout as e:
                print(f"Requests raised a timeout exception: {e}")
            except requests.exceptions.RequestException as e:
                print(f"Requests raised an exception: {e}")

    def take_action(self, importance):
        now = datetime.now()
        filename = f'{self.pictures_dir}/pic_{now.strftime("%Y%m%d_%H%M%S")}.jpg'

        if (now - self.last_action_time).total_seconds() < 10.0:
            if importance <= self.last_action_impt:
                print("Skipping action, throttling.")
                return

        self.last_action_time = now
        self.last_action_impt = importance

        print(f"Capturing picture, saving to {filename} ...")
        camera.capture(filename)

        print(f"Uploading {filename} ...")
        self.upload_picture(filename)


PICTURES_DIR = '/var/HallCam/pictures/'

if not os.access(PICTURES_DIR, os.W_OK):
    print(f"Cannot access {PICTURES_DIR}.")
else:
    print(f"Access to {PICTURES_DIR} is good.")

print(f"localconfig.UPLOAD_URL = {localconfig.UPLOAD_URL}")
print("")


camera = PiCamera()
camera.rotation = 180

# The maximum resolution is 2592×1944 for still photos, 1920×1080 for video recording.
# We also need to set the frame rate to 15 to enable this maximum resolution.
# The minimum resolution is 64×64.
CAMERA_MIN_RESOLUTION = (64, 64)
CAMERA_LOW_RESOLUTION = (640, 480)
CAMERA_MED_RESOLUTION = (1600, 900)
CAMERA_MAX_RESOLUTION = (2592, 1944)

camera.resolution = CAMERA_LOW_RESOLUTION
camera.framerate = 15

# camera.annotate_background = Color('blue')
# camera.annotate_foreground = Color('yellow')
# camera.annotate_text = "Hallo!  :-)"
# camera.annotate_text_size = 20  # 6 … 160, default is 32.

cap_handler = CaptureHandler(PICTURES_DIR, localconfig.UPLOAD_URL)
camera.start_preview()
sleep(2)

print("Entering main loop, press CTRL+C to exit.")
try:
    while True:
        cap_handler.take_action(5)
        sleep(15 * 60)
except KeyboardInterrupt:
    print("\nExiting...")

camera.stop_preview()
