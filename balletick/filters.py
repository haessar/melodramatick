from melodramatick.work.filters import WorkFilter
# from melodramatick.work.forms import WorkFilterFormHelper

from .models import Ballet


class BalletFilter(WorkFilter):

    class Meta(WorkFilter.Meta):
        model = Ballet
        # fields = ['composer', 'composer_group', 'top_list', 'duration_range', 'genre']
        # form = WorkFilterFormHelper
