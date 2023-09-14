from django.conf import settings
from django.db import models

from melodramatick.work.models import Work


class Opera(Work):
    language = models.CharField(choices=settings.LANGUAGE_CHOICES, max_length=2, blank=True)

    @property
    def language_verbose(self):
        return [v for (c, v) in settings.LANGUAGE_CHOICES if c == self.language][0]
