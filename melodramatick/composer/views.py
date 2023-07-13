from dal import autocomplete
from django.db.models import Count, F, FloatField, IntegerField, Case, When
from django.db.models.functions import Cast
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .filters import ComposerFilter
from .models import Composer
from .tables import ComposerTable


class ComposerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Composer.objects.none()
        qs = Composer.objects.all()
        if self.q:
            qs = qs.filter(surname__istartswith=self.q)
        return qs


class ComposerListView(SingleTableMixin, FilterView):
    model = Composer
    table_class = ComposerTable
    template_name = 'composer/index.html'
    filterset_class = ComposerFilter

    def get_table_data(self):
        table_data = super().get_table_data()
        return (
            table_data
            .annotate(
                total_works=Count("work", distinct=True),
                total_top_lists=Count("work__list_item", distinct=True)
            ).annotate(
                top_lists_to_works=Cast(F("total_top_lists"), IntegerField()) / Cast(F("total_works"), FloatField()),
            )
            # ).annotate(
            #     impact=Case(
            #         When(total_operas__lt=F("top_lists_to_operas"), then=F("total_operas")),
            #         default=F("top_lists_to_operas"),
            #         output_field=FloatField()
            #     )
            # )
        )

    def get_table_kwargs(self):
        return {
            'order_by': ('total_top_lists',)
        }
