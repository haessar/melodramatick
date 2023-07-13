from django.apps import apps
from django.conf import settings
from django.shortcuts import redirect

from .models import Listen


def spotify_playback_view(request, **kwargs):
    work_id = kwargs.get('work')
    work = apps.get_model(settings.WORK_MODEL).objects.get(id=work_id)
    listen, _ = Listen.objects.get_or_create(user=request.user, work=work)
    listen.tally += 1
    listen.save()

    return redirect(request.META.get('HTTP_REFERER'))
