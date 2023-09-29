from django.conf import settings
import django_filters

from .models import GENDER_CHOICES, Composer, Group
from melodramatick.utils.filters import CustomEmptyLabelMixin


class ComposerFilter(CustomEmptyLabelMixin, django_filters.FilterSet):
    nationality = django_filters.AllValuesFilter()
    complete = django_filters.ChoiceFilter(choices=((True, "Yes"), (False, "No")), method="filter_complete")
    gender = django_filters.ChoiceFilter(choices=GENDER_CHOICES)
    group = django_filters.ModelChoiceFilter(
        queryset=Group.objects.filter(composer__sites__in=[settings.SITE_ID]).distinct(),
        lookup_expr='exact')

    class Meta:
        model = Composer
        fields = ['nationality', 'group']

    def filter_complete(self, queryset, name, value):
        return queryset.filter(sitecomplete__complete=True if value == "True" else False)
