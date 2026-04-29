import django_tables2 as tables
from melodramatick.work.tables import WorkTable

from .models import Testitem


TestitemTable = tables.table_factory(Testitem, table=WorkTable, fields=["position", "title", "composer"])
