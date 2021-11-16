from datetime import date
from django.shortcuts import redirect, render
from django import forms

from Core.models import Camera, Picture


class UploadPictureForm(forms.Form):
    title = forms.CharField(required=False, max_length=120)
    pic_file = forms.ImageField()


def upload_view(request):
    # The basics of this view are explained at
    # https://docs.djangoproject.com/en/3.2/topics/http/file-uploads/

    if request.method == 'POST':
        form = UploadPictureForm(request.POST, request.FILES)

        if form.is_valid():
            # The values in `request.FILES` are of type `UploadedFile`.

            # with open('some/file/name.txt', 'wb+') as destination:
            #     for chunk in request.FILES['pic_file'].chunks():
            #         destination.write(chunk)

            pic_obj = Picture(camera=Camera.objects.all()[0], picture=request.FILES['pic_file'])
            pic_obj.save()

            # message.success("…")
            return redirect('core:upload')
    else:
        form = UploadPictureForm()

    return render(request, 'Core/upload.html', {
        'heute': date.today(),
        'form': form,
    })
