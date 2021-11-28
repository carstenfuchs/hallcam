#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from time import sleep
from picamera import PiCamera

import localconfig


class Scheduler:
    def is_due(self, dt0, dt1):
        """
        Returns the importance with which the Scheduler thinks that a picture
        should be taken for some time t in intervall dt0 < t <= dt1.
        """
        return 0


class SchedulerEvery5Minutes(Scheduler):
    def is_due(self, dt0, dt1):
        ts0 = dt0.timestamp()
        ts1 = dt1.timestamp()

        if (ts0 // 300) < (ts1 // 300):
            return 4

        return 0


class SchedulerEveryFullHour(Scheduler):
    def is_due(self, dt0, dt1):
        ts0 = dt0.timestamp()
        ts1 = dt1.timestamp()

        if (ts0 // 3600) < (ts1 // 3600):
            return 6

        return 0


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

    def take_action(self, now, importance):
        if (now - self.last_action_time).total_seconds() < 10.0:
            if importance <= self.last_action_impt:
                print("Skipping action, throttling.")
                return

        self.last_action_time = now
        self.last_action_impt = importance

        filename = f'{self.pictures_dir}/pic_{now.strftime("%Y%m%d_%H%M%S")}_{importance}.jpg'

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

schedulers = [
    SchedulerEvery5Minutes(),
    SchedulerEveryFullHour(),
  # SchedulerExposureMonitor(),
]

print("Entering main loop, press CTRL+C to exit.")
try:
    prev_dt = datetime.now()

    while True:
        curr_dt = datetime.now()

        importance = 0
        for sch in schedulers:
            importance = max(importance, sch.is_due(prev_dt, curr_dt))

        if importance > 0:
            cap_handler.take_action(curr_dt, importance)

        prev_dt = curr_dt
        sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")

camera.stop_preview()
