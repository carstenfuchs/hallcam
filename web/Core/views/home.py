from datetime import date
from django.db import transaction
from django.shortcuts import render

from Accounts.models import User
from Core.models import Camera


@transaction.non_atomic_requests
def homepage_view(request):
    heute = date.today()

    if request.user.is_authenticated:
        cameras = request.user.camera_set.all()
    else:
        try:
            public_user = User.objects.get(email="public_user@cafu.de", is_active=False)
            cameras = public_user.camera_set.all()
        except User.DoesNotExist:
            cameras = Camera.objects.none()

    cam_pics = []
    for cam in cameras:
        pics = reversed(cam.picture_set.all().order_by('-id')[:30])
        cam_pics.append(
            {
                'camera': cam,
                'pictures': list(pics),   # this must be a list, or we can only iterate it once
            },
        )

    return render(request, "Core/home.html", {
        'title': 'Übersicht',
        'heute': heute,
        'cam_pics': cam_pics,
    })
