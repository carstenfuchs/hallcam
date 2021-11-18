from django.shortcuts import render

from Core.models import Picture


def viewer_view(request):
    all_pics = Picture.objects.all()

    return render(request, 'Core/viewer.html', {
        'pics': all_pics,
    })
