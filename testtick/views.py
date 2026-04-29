from melodramatick.work.views import WorkDetailView, WorkTableView

from .filters import TestitemFilter
from .models import Testitem
from .tables import TestitemTable


class TestitemDetailView(WorkDetailView):
    model = Testitem


class TestitemTableView(WorkTableView):
    model = Testitem
    table_class = TestitemTable
    filterset_class = TestitemFilter
