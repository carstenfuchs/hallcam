from backports.zoneinfo import ZoneInfo
from datetime import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from Core.models import Camera, Picture


# https://stackoverflow.com/questions/4283933/what-is-the-clean-way-to-unittest-filefield-in-django
# https://stackoverflow.com/questions/25792696/automatically-delete-media-root-between-tests
# https://swapps.com/blog/testing-files-with-pythondjango/
# not very helpful: https://www.caktusgroup.com/blog/2013/06/26/media-root-and-django-tests/


class Test_Picture(TestCase):
    """
    Tests the properties of the `Picture` model.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cam = Camera.objects.create(name="camera-1")
        cls.dt = datetime(2022, 1, 1, tzinfo=ZoneInfo('Europe/Berlin'))

    def test_saves_filelike_object(self):
        """
        Makes sure that the `Picture` class properly saves a file-like object.
        This is what happens in our "upload" view.
        """

        # The implementation of `SimpleUploadedFile` can be seen at:
        # https://github.com/django/django/blob/master/django/core/files/uploadedfile.py
        suf = SimpleUploadedFile('testcase_pic_1.jpg.txt', b'This is a testcase picture.')

        pic_obj = Picture(
            camera=self.cam,
            picture=suf,
            timestamp=self.dt,
        )

        # print(f"{pic_obj.picture.name = }")
        # print(f"{pic_obj.picture.path = }")
        # print(f"{pic_obj.picture.url = }")

        # The picture has not yet been saved: The filename has not yet been
        # updated and neither the database nor the storage have been touched.
        self.assertEqual(Picture.objects.count(), 0)
        self.assertEqual(pic_obj.picture.__class__.__name__, "ImageFieldFile")
        self.assertEqual(pic_obj.picture.name, "testcase_pic_1.jpg.txt")
        self.assertEqual(pic_obj.picture.path, "/var/www/HallCam-media/testcase_pic_1.jpg.txt")
        self.assertEqual(pic_obj.picture.url, "/media/testcase_pic_1.jpg.txt")

        pic_obj.save()

        # Now the picture has been saved: The filename has been updated to, for
        # example, "pictures/testcase_pic_1.jpg_MchJtRN.txt", the data has been
        # written to the storage under this name and the `Picture` object has
        # has been created in the database.
        self.assertEqual(Picture.objects.count(), 1)
        self.assertEqual(pic_obj.picture.__class__.__name__, "ImageFieldFile")
        self.assertTrue(pic_obj.picture.name.startswith("pictures/testcase_pic_1.jpg_"))
        self.assertTrue(pic_obj.picture.path.startswith("/var/www/HallCam-media/pictures/testcase_pic_1.jpg_"))
        self.assertTrue(pic_obj.picture.url.startswith("/media/pictures/testcase_pic_1.jpg_"))

    def test_preexisting_file(self):
        """
        Tests/documents how things work out if a string (file name) rather than
        a file-like object is given.
        """

        pic_obj = Picture(
            camera=self.cam,
            picture="some_file.jpg",
            timestamp=self.dt,
        )

        self.assertEqual(Picture.objects.count(), 0)
        self.assertEqual(pic_obj.picture.__class__.__name__, "ImageFieldFile")
        self.assertEqual(pic_obj.picture.name, "some_file.jpg")
        self.assertEqual(pic_obj.picture.path, "/var/www/HallCam-media/some_file.jpg")
        self.assertEqual(pic_obj.picture.url, "/media/some_file.jpg")

        pic_obj.save()

        # The database instance has been created, but nothing else has changed
        # and the storage has not been touched.
        self.assertEqual(Picture.objects.count(), 1)
        self.assertEqual(pic_obj.picture.__class__.__name__, "ImageFieldFile")
        self.assertEqual(pic_obj.picture.name, "some_file.jpg")
        self.assertEqual(pic_obj.picture.path, "/var/www/HallCam-media/some_file.jpg")
        self.assertEqual(pic_obj.picture.url, "/media/some_file.jpg")
