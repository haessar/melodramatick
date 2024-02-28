from django.contrib import admin

from melodramatick.work.admin import BaseWorkAdmin
from .models import Concerto


@admin.register(Concerto)
class ConcertoAdmin(BaseWorkAdmin):
    base_model = Concerto
