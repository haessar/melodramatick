import random

from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import DetailView, ListView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from . import plots
from .models import Work
from melodramatick.listen.models import Listen
from melodramatick.utils.rendering import render_tickbox


class WorkTableView(SingleTableMixin, FilterView):
    model = Work
    # table_class = OperaTable
    template_name = 'work/index.html'
    # filterset_class = OperaFilter

    def render_to_response(self, context, **kwargs):
        """
        Add a randomly chosen album uri from the filtered queryset to context
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


@method_decorator([vary_on_cookie, cache_page(60 * 60)], name='dispatch')
class WorkGraphsView(ListView):
    template_name = 'work/work_graphs.html'
    model = Work

    def get_context_data(self, **kwargs):
        qs = self.object_list.annotate(
                user_listens=Coalesce(Sum('listen__tally', filter=Q(listen__user=self.request.user)), 0),
                user_perfs=Count('performance', filter=Q(performance__user=self.request.user) & Q(performance__streamed=False))
            )
        top = plots.plot_works_by_decade(qs, figsize=(12, 6))
        middle_left = plots.plot_works_per_composer(qs, figsize=(4, 6))
        middle_centre = plots.plot_perfs_per_composer(qs, figsize=(4, 6))
        middle_right = plots.plot_listens_per_composer(qs, figsize=(4, 6))
        bottom_left = plots.plot_works_per_era(qs, figsize=(3, 6))
        bottom_centre = plots.plot_perfs_per_era(qs, figsize=(3, 6))
        bottom_right = plots.plot_listens_per_era(qs, figsize=(3, 6))
        duration_hist = plots.plot_duration_hist(qs, figsize=(12, 6))
        top_lists_bar = plots.plot_top_lists_by_decade(qs, figsize=(12, 6))
        context = {
            'top': top,
            'middle_left': middle_left,
            'middle_centre': middle_centre,
            'middle_right': middle_right,
            'bottom_left': bottom_left,
            'bottom_centre': bottom_centre,
            'bottom_right': bottom_right,
            'duration_hist': duration_hist,
            'top_lists_bar': top_lists_bar,
            'work_count': self.object_list.count(),
            'user_performance_count': qs.aggregate(Sum('user_perfs'))['user_perfs__sum'],
            'user_listen_count': qs.aggregate(Sum('user_listens'))['user_listens__sum'],
        }
        return context


class WorkDetailView(DetailView):
    model = Work

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ticked"], context["tickbox"] = render_tickbox(self.request.user, self.object, scale=2)
        try:
            context["listen_count"] = self.object.listen.get(user=self.request.user.id).tally
        except Listen.DoesNotExist:
            context["listen_count"] = 0
        return context
