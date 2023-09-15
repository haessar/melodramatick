from celery import shared_task
from notifications.signals import notify

from melodramatick.accounts.models import CustomUser
from melodramatick.performance.models import Performance
from melodramatick.top_list.models import Award, AwardLevel, List, Progress
from melodramatick.work.models import Work


@shared_task
def update_user_award_shared_task(user_id, performance_id=None):
    user = CustomUser.objects.get(id=user_id)
    performance = Performance.objects.get(id=performance_id) if performance_id else None
    for l in List.objects.filter(items__in=performance.work.all() if performance  # noqa: E741
                                 else Work.objects.all()).distinct():
        ticked = set()
        for li in l.listitem_set.all():
            if Performance.objects.filter(user=user, work=li.item, streamed=False):
                ticked.add(li.position)
        ratio = len(ticked) / l.length
        progress, _ = Progress.objects.get_or_create(user=user, list=l)
        progress.ratio = ratio
        progress.count = len(ticked)
        progress.save()
        if ratio >= 0.5:
            try:
                award = Award.objects.get(user=user, list=l)
            except Award.DoesNotExist:
                award = Award.objects.create(user=user, list=l, level=AwardLevel.objects.get(rank=4))
                new_award = True
            else:
                new_award = False
            if ratio == 1.0:
                award.level = AwardLevel.objects.get(rank=1)
            elif ratio >= 0.9:
                award.level = AwardLevel.objects.get(rank=2)
            elif ratio >= 0.75:
                award.level = AwardLevel.objects.get(rank=3)
            if new_award:
                notify.send(user, recipient=user, verb="achieved an award", target=award.level, action_object=award,
                            description="for {}".format(l))
            award.save()
