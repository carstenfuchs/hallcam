import requests, socket
from io import BytesIO
from pathlib import Path

from common import create_simple_image


class UploadManager:
    """This class manages uploads."""

    def __init__(self, upload_url, upload_pwd):
        self.UPLOAD_URL = upload_url
        self.UPLOAD_PWD = upload_pwd
        self.num_upload_fails = 0

    def open_pic(self, filename):
        if self.num_upload_fails >= 3:
            msg = f"{self.num_upload_fails} prior uploads failed.\nDummy images are sent until the next successful upload."
            print(msg)

            pic_name = Path(filename).stem + ".png"
            pic_file = BytesIO()
            create_simple_image(
                # This image is sent because x prior upload attempts have failed.
                # The true image is safely kept on the camera's disk space,
                # but in order increase the chance of a successful transmission,
                # this image, that requires a much smaller transfer volume,
                # has been substituted for the next upload attempt.
                # If the upload of this image is successful, the normal uploading
                # is resumed.
                msg,
                text_color=(255, 255, 255),
                background_color=(255, 60, 30),
            ).save(pic_file, format="png")
            pic_file.seek(0)

            return pic_name, pic_file

        # This is the normal case.
        pic_name = Path(filename).name
        pic_file = open(filename, 'rb')

        return pic_name, pic_file

    def upload(self, filename):
        if not self.UPLOAD_URL:
            return

        print(f"Uploading {filename} ...")

        with open("/sys/class/thermal/thermal_zone0/temp") as temp_file:
            # https://www.elektronik-kompendium.de/sites/raspberry-pi/1911241.htm
            # https://raspberrypi.stackexchange.com/questions/41784/temperature-differences-between-cpu-gpu
            cpu_temp = temp_file.readline().strip()

        try:
            pic_name, pic_file = self.open_pic(filename)

            with pic_file:
                r = requests.post(
                    self.UPLOAD_URL,
                    data={
                        'camera': socket.gethostname(),
                        'password': self.UPLOAD_PWD,
                        'cpu_temp': cpu_temp,
                    },
                    files={
                        'pic_file': (pic_name, pic_file),
                    },
                    allow_redirects=False,
                    timeout=30.0,
                )

            print(f"Uploaded picture to {self.UPLOAD_URL} in {r.elapsed.total_seconds()} s.")
            self.num_upload_fails = 0

            if r.status_code != 302:
                print(f"Unexpected response: Expected status_code 302, got status_code {r.status_code}.")
                print(r)
                for line in r.text.splitlines():
                    if any(keyword in line for keyword in ('error', 'invalid')):
                        print(line[:240])
        except FileNotFoundError as e:
            print(f"--> FileNotFoundError: {e}")
        except requests.exceptions.Timeout as e:
            print(f"--> Requests raised a timeout exception: {e}")
            self.num_upload_fails += 1
        except requests.exceptions.RequestException as e:
            print(f"--> Requests raised an exception: {e}")
            self.num_upload_fails += 1
