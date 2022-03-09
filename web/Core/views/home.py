from datetime import timedelta
from django.db import transaction
from django.shortcuts import render
from django.utils import timezone

from Accounts.models import User
from Core.models import Camera


def get_latest_and_24(cameras):
    """Returns the latest picture and those of the last 24 hours at the full hour."""
    collages = []
    now = timezone.now()

    # The latest full hour is `floor(now)` (with regards to hours),
    # the first full hour is 23 hours before that.
    latest_fh = now.replace(minute=0, second=0, microsecond=0)
    first_fh = latest_fh - timedelta(hours=23)

    for cam in cameras:
        pics = list(cam.picture_set.filter(timestamp__gte=first_fh-timedelta(minutes=30)))
        series = [None] * 24

        for pic in pics:
            delta = (pic.timestamp - first_fh).total_seconds() / 3600.0
            index = round(delta)

            if not (0 <= index < 24):
                continue

            if series[index] is None:
                series[index] = pic
                continue

            old_delta = (series[index].timestamp - first_fh).total_seconds() / 3600.0
            assert round(old_delta) == index

            if abs(index - delta) < abs(index - old_delta):
                series[index] = pic

        collage = {
            'camera': cam,
          # 'latest': cam.picture_set.all().order_by('timestamp')[0],
            'latest': pics[-1] if pics else None,
            'series': series,
        }
        collages.append(collage)

    return collages


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

    layout = request.GET.get('layout')
    context = {}

    if layout == 'all-of-24h':
        context['title'] = "Details"
        context['subtitle'] = "Alle Bilder der letzten 24 Stunden"
        context['cam_pics'] = get_all_of_last_24_hours(cameras)
    else:
        context['title'] = "Übersicht"
        context['subtitle'] = "Das aktuelle Bild und die letzten 24 Stunden"
        context['collages'] = get_latest_and_24(cameras)

    return render(request, "Core/home.html", context)
