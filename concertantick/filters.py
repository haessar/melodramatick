from django.conf import settings
import django_filters

from .models import Concerto
from melodramatick.work.filters import WorkFilter


class ConcertoFilter(WorkFilter):
    instrument = django_filters.ChoiceFilter(choices=settings.INSTRUMENT_CHOICES)

    class Meta(WorkFilter.Meta):
        model = Concerto
