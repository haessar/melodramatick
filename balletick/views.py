from django.views.generic import DetailView
from melodramatick.work.views import WorkTableView

from .filters import BalletFilter
from .models import Ballet
from .tables import BalletTable


class BalletDetailView(DetailView):
    model = Ballet


class BalletTableView(WorkTableView):
    model = Ballet
    table_class = BalletTable
    filterset_class = BalletFilter
