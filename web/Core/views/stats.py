from io import StringIO
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from Core.libs.pictures import cleanup_pictures, sync_pictures


@staff_member_required
def view(request):

    with StringIO() as buffer:
        cleanup_pictures(hot_run=False, out=buffer)
        cleanup_report = buffer.getvalue()

    return render(
        request,
        'Core/stats.html',
        {
            'title': "Statistics 📈",
            'stats': sync_pictures(hot_run=False, verbosity=0),
            'cleanup_report': cleanup_report,
        },
    )
