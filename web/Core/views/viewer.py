from django.shortcuts import render
from pathlib import Path

from Core.models import Picture


def viewer_view(request):
    all_pics = Picture.objects.all()
    missing_paths = []

    for pic in all_pics:
        p = pic.picture.path
        if not Path(p).is_file():
            missing_paths.append(p)
            pic.delete()

    if missing_paths:
        all_pics = Picture.objects.all()

    return render(request, 'Core/viewer.html', {
        'pics': all_pics,
        'missing_paths': missing_paths,
    })
