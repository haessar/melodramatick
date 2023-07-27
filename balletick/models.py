from django.db import models

from melodramatick.work.models import Work


class Ballet(Work):
    choreographer = models.CharField(max_length=50, blank=True, null=True)
