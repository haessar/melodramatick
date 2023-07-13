import random

from django.db.models import Count, Q, Sum
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin


class WorkTableView(SingleTableMixin, FilterView):
    # model = Opera
    # table_class = OperaTable
    template_name = 'work/index.html'
    # filterset_class = OperaFilter

    def render_to_response(self, context, **kwargs):
        """
        Add a randomly chosen spotify_link from the filtered queryset to context
        """
        qs_with_links = self.object_list.exclude(album__id__isnull=True)
        if qs_with_links:
            random_pick = qs_with_links[random.randint(0, len(qs_with_links)-1)]
            try:
                album_id = random_pick.uri
            except AttributeError:
                album_id = random_pick.random_uri
            context['random_uri'] = album_id
            context['work_id'] = random_pick.id
        return super().render_to_response(context, **kwargs)

    def get_table_data(self):
        table_data = super().get_table_data()
        return table_data.annotate(
            user_listens=Sum("listen__tally", filter=Q(listen__user=self.request.user), distinct=True),
            user_performances=Count("performance", filter=Q(performance__user=self.request.user), distinct=True),
            total_lists=Count("list", distinct=True)
        )

    def get_table_kwargs(self):
        """
        Remove column from table if it is being filtered over.
        Handle ordering when particular filters are selected.
        """
        excluded = set()
        order_by = ('total_lists', 'year')
        excluded.update(('position', 'duration', 'uri'))
        for k, v in self.request.GET.items():
            if v:
                excluded.add(k)
                if k == 'top_list':
                    excluded.discard('position')
                    excluded.add('total_lists')
                    order_by = ('position',)
                elif 'duration_range' in k:
                    excluded.discard('duration')
                    excluded.discard('uri')
                    excluded.add("random_uri")
                    order_by = ('duration',)
        return {
            'exclude': excluded,
            'order_by': order_by
        }
