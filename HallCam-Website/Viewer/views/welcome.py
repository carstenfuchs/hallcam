from datetime import date
from django.db import transaction
from django.shortcuts import render


@transaction.non_atomic_requests
def view(request):
    heute = date.today()

    return render(request, "Viewer/welcome.html", {
        "heute": heute,
    })
