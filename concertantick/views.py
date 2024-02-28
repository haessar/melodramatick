from melodramatick.work.views import WorkDetailView, WorkTableView

from .filters import ConcertoFilter
from .models import Concerto
from .tables import ConcertoTable


class ConcertoDetailView(WorkDetailView):
    model = Concerto


class ConcertoTableView(WorkTableView):
    model = Concerto
    table_class = ConcertoTable
    filterset_class = ConcertoFilter
