from django.views.generic import DetailView
from melodramatick.work.views import WorkTableView

from .filters import OperaFilter
from .models import Opera
from .tables import OperaTable


class OperaDetailView(DetailView):
    model = Opera


class OperaTableView(WorkTableView):
    model = Opera
    table_class = OperaTable
    filterset_class = OperaFilter
