from melodramatick.work.filters import WorkFilter

from .models import Testitem


class TestitemFilter(WorkFilter):

    class Meta(WorkFilter.Meta):
        model = Testitem
