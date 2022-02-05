from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from Core.libs.pictures import sync_pictures


@staff_member_required
def view(request):
    return render(
        request,
        'Core/stats.html',
        {
            'title': "Statistics 📈",
            'stats': sync_pictures(hot_run=False, verbosity=0),
        },
    )
