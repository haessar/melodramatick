import django_tables2 as tables
from melodramatick.work.tables import WorkTable

from .models import Ballet

BalletTable = tables.table_factory(Ballet, table=WorkTable, fields=["position", "title", "composer", "choreographer"])
