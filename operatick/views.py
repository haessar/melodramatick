from melodramatick.work.views import WorkDetailView, WorkTableView

from .filters import OperaFilter
from .models import Opera
from .tables import OperaTable


class OperaDetailView(WorkDetailView):
    model = Opera


class OperaTableView(WorkTableView):
    model = Opera
    table_class = OperaTable
    filterset_class = OperaFilter
