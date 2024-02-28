import django_tables2 as tables
from melodramatick.work.tables import WorkTable

from .models import Concerto

ConcertoTable = tables.table_factory(Concerto, table=WorkTable, fields=["position", "title", "composer", "instrument"])
