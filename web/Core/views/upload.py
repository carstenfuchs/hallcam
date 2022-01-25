from backports.zoneinfo import ZoneInfo
from datetime import date, datetime

from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django import forms

from Core.models import Camera, Picture
from HallCam import localconfig


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


@csrf_exempt
def upload_view(request):
    # The basics of this view are explained at
    # https://docs.djangoproject.com/en/4.0/topics/http/file-uploads/

    if request.method == 'POST':
        form = UploadPictureForm(request.POST, request.FILES)

        if form.is_valid():
            # The values in `request.FILES` are of type `UploadedFile`.
            uploaded_pic_file = request.FILES['pic_file']

            # with open('some/file/name.txt', 'wb+') as destination:
            #     for chunk in request.FILES['pic_file'].chunks():
            #         destination.write(chunk)
            print(f"{uploaded_pic_file.name = }")
            print(f"{uploaded_pic_file.size = }")
            print(f"{uploaded_pic_file.content_type = }")
            print(f"{uploaded_pic_file.content_type_extra = }")

            try:
                dt = datetime.strptime(uploaded_pic_file.name[4:17], "%Y%m%d_%H%M")
                dt = dt.replace(tzinfo=ZoneInfo('Europe/Berlin'))
            except ValueError:
                dt = timezone.now()

            print(f"{dt = }")

            pic_obj = Picture(
                camera=Camera.objects.all()[0],
                picture=uploaded_pic_file,
                timestamp=dt,
            )
            pic_obj.save()

            # message.success("…")
            return redirect('core:upload')
    else:
        form = UploadPictureForm()

    return render(request, 'Core/upload.html', {
        'title': "Upload image 😜",
        'form': form,
    })
