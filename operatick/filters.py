from django.conf import settings
import django_filters
from melodramatick.work.filters import WorkFilter


class OperaFilter(WorkFilter):
    language = django_filters.ChoiceFilter(choices=settings.LANGUAGE_CHOICES)

    class Meta(WorkFilter.Meta):
        fields = ['composer', 'composer_group', 'language', 'top_list', 'duration_range', 'genre']
