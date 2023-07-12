from django.db.models import Count, Max
from django_tables2 import SingleTableView

from .models import List
from .tables import TopListTable


class TopListView(SingleTableView):
    model = List
    table_class = TopListTable
    template_name = 'top_list/index.html'

    def get_table_data(self):
        table_data = super().get_table_data()
        return table_data.annotate(
            max_position=Max("listitem__position"),
            list_work_count=Count("items")
        )
