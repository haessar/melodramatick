import django_tables2 as tables
from melodramatick.work.tables import WorkTable

from .models import Opera

OperaTable = tables.table_factory(Opera, table=WorkTable, fields=["position", "title", "composer", "language"])
