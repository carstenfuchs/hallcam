from datetime import date
from django.shortcuts import redirect, render
from django import forms


class UploadImageForm(forms.Form):
    title = forms.CharField(max_length=50)
    img = forms.ImageField()


def handle_uploaded_file(f):
    # `f` is of type `UploadedFile`.
    print(type(f))
    print(f)
    # with open('some/file/name.txt', 'wb+') as destination:
    #     for chunk in f.chunks():
    #         destination.write(chunk)


def upload_view(request):
    # The basics of this view are explained at
    # https://docs.djangoproject.com/en/3.2/topics/http/file-uploads/

    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)

        if form.is_valid():
            # example 1:
            handle_uploaded_file(request.FILES['img'])

            # example 2:
          # instance = ModelWithFileField(file_field=request.FILES['img'])
          # instance.save()

            # message.success("…")
            return redirect('core:upload')
    else:
        form = UploadImageForm()

    return render(request, 'Core/upload.html', {
        'heute': date.today(),
        'form': form,
    })
