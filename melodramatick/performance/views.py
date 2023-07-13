from django.apps import apps
from django.conf import settings
from django.shortcuts import redirect

from .models import Performance


def tick_view(request, **kwargs):
    work_id = kwargs.get('work')
    work = apps.get_model(settings.WORK_MODEL).objects.get(id=work_id)
    performances = Performance.objects.filter(user=request.user, work=work)
    if not performances:
        performance = Performance.objects.create(user=request.user)
        performance.work.add(work)
    else:
        for p in performances:
            p.delete()

    return redirect(request.META.get('HTTP_REFERER'))
