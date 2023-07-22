from django.shortcuts import redirect

from melodramatick.work.models import Work
from .models import Performance


def tick_view(request, **kwargs):
    work_id = kwargs.get('work')
    work = Work.objects.get(id=work_id)
    performances = Performance.objects.filter(user=request.user, work=work)
    if not performances:
        performance = Performance.objects.create(user=request.user, site=request.site)
        performance.work.add(work)
    else:
        for p in performances:
            p.delete()

    return redirect(request.META.get('HTTP_REFERER'))
