from django.shortcuts import redirect

from .models import Listen
from melodramatick.work.models import Work


def spotify_playback_view(request, **kwargs):
    work_id = kwargs.get('work')
    work = Work.objects.get(id=work_id)
    listen, _ = Listen.objects.get_or_create(user=request.user, work=work, site=request.site)
    listen.tally += 1
    listen.save()

    return redirect(request.META.get('HTTP_REFERER'))
