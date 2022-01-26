#!/usr/bin/env python3
import os
import shutil, socket, sys
from datetime import datetime, timedelta
from time import sleep
from pathlib import Path

import localconfig
from camera import get_camera
from common import fmt_bytes, get_data_from_pic_stem, get_score
from upman import UploadManager


class Task:
    def is_due(self, dt0, dt1):
        """
        Returns the importance with which the Task thinks that a picture
        should be taken in the intervall dt0 < t <= dt1.
        """
        return 0


class TaskEvery5Minutes(Task):
    def is_due(self, dt0, dt1):
        ts0 = dt0.timestamp()
        ts1 = dt1.timestamp()

        if (ts0 // 300) < (ts1 // 300):
            return 4

        return 0


class TaskEveryFullHour(Task):
    def is_due(self, dt0, dt1):
        ts0 = dt0.timestamp()
        ts1 = dt1.timestamp()

        if (ts0 // 3600) < (ts1 // 3600):
            return 6

        return 0


def gather_pictures(clean_dir, now):
    pics = []

    for pic_path in Path(clean_dir).iterdir():
        pics.append(
            (
                pic_path,
                pic_path.stat().st_size,
                get_score(*get_data_from_pic_stem(pic_path.stem), now),
            )
        )

    # Sort the pictures by score.
    pics.sort(key=lambda pic: -pic[2])
    return pics


class TaskCleanupDisk(Task):
    def __init__(self, clean_dir):
        self.clean_dir = clean_dir
        self.next_clean_dt = datetime(2000, 1, 1)

    def clean(self, now):
        print("Cleaning up disk space ...")
        GiB = pow(1024, 3)
        MIN_PICS_TOTAL =  1*GiB
        MAX_PICS_TOTAL = 20*GiB
        MIN_DISK_FREE  =  2*GiB

        disk_total, disk_used, disk_free = shutil.disk_usage("/")
        # print(f"disk_total {fmt_bytes(disk_total):>10}")
        # print(f"disk_used  {fmt_bytes(disk_used):>10}")
        # print(f"disk_free  {fmt_bytes(disk_free):>10} ({fmt_bytes(MIN_DISK_FREE)})")
        btd_disk = max(MIN_DISK_FREE - disk_free, 0)
        print(f"free disk space: {fmt_bytes(disk_free)}, want at least: {fmt_bytes(MIN_DISK_FREE)} --> delete {fmt_bytes(btd_disk)}")

        pics = gather_pictures(self.clean_dir, now)
        pics_total_bytes = sum(pic[1] for pic in pics)
        btd_pics = max(pics_total_bytes - MAX_PICS_TOTAL, 0)
        print(f"{len(pics)} pictures of size: {fmt_bytes(pics_total_bytes)}, want at most: {fmt_bytes(MAX_PICS_TOTAL)} --> delete {fmt_bytes(btd_pics)}")

        pic_bytes_to_delete = max(btd_disk, btd_pics)
        print(f"--> deleting {fmt_bytes(pic_bytes_to_delete)} ...")

        while pics and pic_bytes_to_delete > 0 and pics_total_bytes > MIN_PICS_TOTAL:
            pic = pics.pop()
            print(f"  deleting {pic[0]},{pic[1]:>8} bytes, score {pic[2]}")
            pic[0].unlink()
          # pic[0].unlink(missing_ok=True)  # Python 3.8+
            pic_bytes_to_delete -= pic[1]
            pics_total_bytes -= pic[1]

        print(f"{len(pics)} pictures of size: {fmt_bytes(pics_total_bytes)} left")
        if pic_bytes_to_delete > 0:
            print(f"{fmt_bytes(pic_bytes_to_delete)} not deleted, MIN_PICS_TOTAL is {fmt_bytes(MIN_PICS_TOTAL)}")

    def is_due(self, dt0, dt1):
        if dt0 < self.next_clean_dt <= dt1:
            print("Running TaskCleanupDisk!", dt0, dt1)
            self.clean(dt1)

        if self.next_clean_dt <= dt1:
            self.next_clean_dt = datetime(dt1.year, dt1.month, dt1.day, 3, 33, 33)
            if self.next_clean_dt <= dt1:
                self.next_clean_dt += timedelta(days=1)
            print("Next disk cleanup is scheduled for", self.next_clean_dt)

        return 0


def run_camera():
    access_ok = os.access(localconfig.PICTURES_DIR, os.W_OK)
    camera = get_camera()
    upman = UploadManager(localconfig.UPLOAD_URL, localconfig.UPLOAD_PASSWORD)

    print(f"host        {socket.gethostname()}")
    print(f"camera      {camera.__class__}")
    print(f"save to     {localconfig.PICTURES_DIR} (access {'OK' if access_ok else 'FAILED'})")
    print(f"upload to   {localconfig.UPLOAD_URL}")

    camera.start_preview()

    tasks = [
        TaskEvery5Minutes(),
        TaskEveryFullHour(),
      # TaskExposureMonitor(),
        TaskCleanupDisk(localconfig.PICTURES_DIR),
    ]

    print("\nEntering main loop, press CTRL+C to exit.")
    try:
        prev_dt = datetime.now()

        while True:
            curr_dt = datetime.now()

            importance = 0
            for task in tasks:
                importance = max(importance, task.is_due(prev_dt, curr_dt))

            if importance > 0:
                filename = camera.capture_picture(curr_dt, importance, localconfig.PICTURES_DIR)
                upman.upload(filename)

            prev_dt = curr_dt
            sleep(1)

    except KeyboardInterrupt:
        print("\nExiting ...")

    camera.stop_preview()


if __name__ == "__main__":
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        # The null byte (\0) means the socket is created in the abstract
        # namespace instead of being created on the file system itself.
        # https://stackoverflow.com/questions/788411/check-to-see-if-python-script-is-running
        lock_socket.bind('\0' + 'HallCam')
    except socket.error:
        print("HallCam is already running.")
        sys.exit()

    # We got the lock.
    run_camera()
