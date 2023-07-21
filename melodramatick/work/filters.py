from dal import autocomplete
import django_filters
from django.conf import settings
from django.db.models import Q, F
from django.urls import reverse_lazy

from melodramatick.composer.models import Composer, Group
from melodramatick.top_list.models import List
from melodramatick.utils.filters import CustomEmptyLabelMixin
from melodramatick.utils.widgets import CustomRangeWidget
from .forms import WorkFilterFormHelper
from .models import Genre, Work


class EraChoiceFilter(django_filters.ChoiceFilter):
    def filter(self, qs, value):
        if value:
            start, end = value.split("-")
            return qs.filter(Q(year__gte=start) & Q(year__lte=end))
        return qs


class AllRangeFilter(django_filters.RangeFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        min_value = 0
        max_value = 360
        self.extra['widget'] = CustomRangeWidget(attrs={'data-range_min': min_value, 'data-range_max': max_value})


class WorkFilter(CustomEmptyLabelMixin, django_filters.FilterSet):
    composer = django_filters.ModelChoiceFilter(
        queryset=Composer.objects.all(),
        widget=autocomplete.ModelSelect2(
            url=reverse_lazy("composer:composer-autocomplete"),
            attrs={'data-theme': 'bootstrap-4'}))
    top_list = django_filters.ModelChoiceFilter(queryset=List.objects.all(), method='filter_top_list', label="Top List")
    duration_range = AllRangeFilter(method='filter_duration_range', label="Album duration")
    era = EraChoiceFilter(choices=settings.ERAS_MAP)
    genre = django_filters.ModelChoiceFilter(queryset=Genre.objects.all(), field_name='sub_genre__genre', lookup_expr='exact')
    composer_group = django_filters.ModelChoiceFilter(queryset=Group.objects.all(), field_name='composer__group',
                                                      lookup_expr='exact', label="Composer Group")

    class Meta:
        model = Work
        fields = ['composer', 'composer_group', 'top_list', 'duration_range', 'genre']
        form = WorkFilterFormHelper

    def filter_top_list(self, queryset, name, value):
        return queryset \
            .filter(list_item__list=value) \
            .annotate(list_rank=F('list_item__position'))

    def filter_duration_range(self, queryset, name, value):
        return queryset \
            .filter(album__duration__gte=value.start or 0, album__duration__lte=value.stop or 9999) \
            .annotate(duration=F('album__duration')) \
            .annotate(uri=F('album__uri'))
