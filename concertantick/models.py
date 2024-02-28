from django.conf import settings
from django.db import models

from melodramatick.work.models import Work


class Concerto(Work):
    instrument = models.CharField(choices=settings.INSTRUMENT_CHOICES, max_length=10, blank=True)
