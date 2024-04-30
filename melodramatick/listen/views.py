from urllib.parse import urlparse

from django.conf import settings
from django.shortcuts import redirect

from .models import Listen
from melodramatick.work.models import Work


def spotify_playback_view(request, **kwargs):
    work_id = kwargs.get('work')
    work = Work.objects.get(id=work_id)
    listen, _ = Listen.objects.get_or_create(user=request.user, work=work, site=request.site)
    listen.tally += 1
    listen.save()

    referer_url = request.META.get('HTTP_REFERER')
    # Avoid feedback loop with login page redirects
    if referer_url and not urlparse(referer_url).path == settings.LOGIN_URL:
        return redirect(referer_url)
    else:
        return redirect('home')
