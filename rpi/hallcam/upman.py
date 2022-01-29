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
        if self.num_upload_fails >= 5:
            print(f"{self.num_upload_fails} prior uploads failed --> sending only a lightweight debug image.")

            pic_name = Path(filename).stem + ".png"
            pic_file = BytesIO()
            create_simple_image(
                "There seems to be a problem with the network connection:\n"
                f"{self.num_upload_fails} attempts to upload pictures from the camera to the webserver\n"
                "have failed. All pictures are safely kept on the camera's disk\n"
                "space, but upload attempts are now started with images like\n"
                "this to facilitate troubleshooting.\n"
                "Normal uploads are resumed as soon as the next upload succeeded.\n",
                text_color=(255, 255, 255),
              # background_color=(255, 60, 30),  # dark orange
                background_color=(30, 60, 255),
            ).save(pic_file, format="png", optimize=True)
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

            if r.status_code == 302:
                self.num_upload_fails = 0
            else:
                print(f"Unexpected response: Expected status_code 302, got {r.status_code}.")
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
