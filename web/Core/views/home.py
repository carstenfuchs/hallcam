from datetime import date
from django.db import transaction
from django.shortcuts import render


@transaction.non_atomic_requests
def homepage_view(request):
    heute = date.today()

    return render(request, "Core/home.html", {
        'title': 'Hallo!',
        'heute': heute,
    })
