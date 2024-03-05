import itertools

from django.db.models import Sum, Q
from django.db.models.functions import Coalesce


def user_listens_per_era(qs, user=None):
    if user:
        qs = qs.annotate(user_listens=Coalesce(Sum('listen__tally', filter=Q(listen__user=user)), 0))
    by_era = sorted([(w.era, w.user_listens) for w in qs.exclude(user_listens=0)], key=lambda x: x[0])
    return [(key, sum(num for _, num in value)) for key, value in itertools.groupby(by_era, lambda x: x[0])]
