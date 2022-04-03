from backports.zoneinfo import ZoneInfo
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django import forms

from Core.models import Camera, Picture


class UploadPictureForm(forms.Form):
    camera   = forms.ModelChoiceField(queryset=Camera.objects.all(), to_field_name="name")
    password = forms.CharField(max_length=40)
    pic_file = forms.ImageField()
  # sys_info = forms.CharField(max_length=250, required=False)

    def clean(self):
        cd = super().clean()

        # Setze hier gar nicht erst an, solange es noch Felder gibt, die in sich fehlerhaft sind.
        if self.errors:
            return

        if cd['password'] != cd['camera'].pwd:
            self.add_error('password', "The password is wrong.")
            return cd

        return cd


def save_to_disk(camera, uploaded_pic_file):
    """Saves the given `UploadedFile` to disk and returns its full path."""

    pic_path = Path(
        settings.MEDIA_ROOT,
        Picture.PICTURES_SUBDIR,
        f"camera-{camera.id}",
        uploaded_pic_file.name,
    )

    # If this is the first picture of a new camera, make sure that
    # the related subdirectory exists.
    pic_path.parent.mkdir(parents=True, exist_ok=True)

    with open(pic_path, 'wb') as dest_file:
        for chunk in uploaded_pic_file.chunks():
            dest_file.write(chunk)

    print(f"Picture saved to {pic_path} ({uploaded_pic_file.content_type}, {uploaded_pic_file.size} bytes, camera {camera.name})")
    return pic_path


@csrf_exempt
def upload_view(request):
    # The basics of this view are explained at
    # https://docs.djangoproject.com/en/4.0/topics/http/file-uploads/

    if request.method == 'POST':
        # The items in `request.FILES` are of type `UploadedFile`. For details,
        # see https://docs.djangoproject.com/en/4.0/ref/files/uploads/
        form = UploadPictureForm(request.POST, request.FILES)

        if form.is_valid():
            # The `ImageField` in the form normalizes to an `UploadedFile` object.
            # This is just the `UploadedFile` taken from request.FILES['pic_file'],
            # augmented with an additional `image` attribute as described at
            # https://docs.djangoproject.com/en/4.0/ref/forms/fields/#imagefield
            assert form.cleaned_data['pic_file'] == request.FILES['pic_file']

            pic_path = save_to_disk(form.cleaned_data['camera'], form.cleaned_data['pic_file'])

            try:
                dt = datetime.strptime(pic_path.name[4:17], "%Y%m%d_%H%M")
                dt = dt.replace(tzinfo=ZoneInfo('Europe/Berlin'))
            except ValueError:
                dt = timezone.now()

            # If a picture with the given filename already exists, the file on
            # disk is overwritten and the related `Picture` object is updated
            # rather than created (the `filename` must be unique).
            Picture.objects.update_or_create(
                filename=pic_path.name,
                defaults={
                    'camera': form.cleaned_data['camera'],
                    'timestamp': dt,
                }
            )

            return redirect('core:upload')
    else:
        form = UploadPictureForm()

    return render(request, 'Core/upload.html', {
        'title': "Upload image 😜",
        'form': form,
    })
