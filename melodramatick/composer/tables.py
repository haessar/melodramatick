from django.urls import reverse
from django.utils.html import format_html
import django_tables2 as tables

from .models import Composer, SiteComplete


class ComposerTable(tables.Table):
    first_name = tables.Column(accessor="first_name", verbose_name="First name(s)")
    total_works = tables.Column(accessor="total_works", orderable=True, order_by="-total_works")
    total_top_lists = tables.Column(accessor="total_top_lists", orderable=True, order_by="-total_top_lists",
                                    verbose_name="Aggregate Top Lists count")
    impact = tables.Column(accessor="top_lists_to_works", verbose_name="Impact Factor", order_by="-top_lists_to_works",
                           attrs={"help_text": "Ratio of aggregated top list counts to total number of works composed."})
    complete = tables.BooleanColumn(accessor="sitecomplete", verbose_name="Complete",
                                    attrs={"help_text": "All available operas for this composer are in the database."})

    class Meta:
        model = Composer
        template_name = "composer/table.html"
        sequence = ['first_name', 'surname', 'complete']
        exclude = ['id', 'group']

    def render_total_works(self, record):
        return format_html('<a href={}?composer={}>{}</a>', reverse('work:index'), record.id, record.total_works)

    def render_surname(self, record):
        return format_html('<p class="font-weight-bold">{}</p>', record.surname)

    def render_impact(self, record):
        return round(record.top_lists_to_works, 2)

    def render_complete(self, value, record, column, bound_column):
        """
        Compensate for failure of accessor to correctly access fields from many-to-one relationships
        i.e. "sitecomplete__complete"
        """
        try:
            value = value.get(site=self.request.site).complete
        except SiteComplete.DoesNotExist:
            value = False
        return column.render(value, record, bound_column)
