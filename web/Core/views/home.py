from datetime import timedelta
from django.db import transaction
from django.shortcuts import render
from django.utils import timezone

from Accounts.models import User
from Core.models import Camera


def get_all_of_last_24_hours(cameras):
    now = timezone.now()
    cam_pics = []

    for cam in cameras:
        pics = cam.picture_set.filter(timestamp__gte=now - timedelta(days=1))
        cam_pics.append(
            {
                'camera': cam,
                'pictures': list(pics),   # this must be a list, or we can only iterate it once
            },
        )

    return cam_pics


@transaction.non_atomic_requests
def homepage_view(request):
    if request.user.is_authenticated:
        cameras = request.user.camera_set.all()
    else:
        try:
            public_user = User.objects.get(email="public_user@cafu.de", is_active=False)
            cameras = public_user.camera_set.all()
        except User.DoesNotExist:
            cameras = Camera.objects.none()

    context = {
        'title': 'Übersicht',
        'cam_pics': get_all_of_last_24_hours(cameras),
    }

    return render(request, "Core/home.html", context)
