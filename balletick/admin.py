from django.contrib import admin

from .models import Ballet
from melodramatick.work.admin import BaseWorkAdmin


@admin.register(Ballet)
class BalletAdmin(BaseWorkAdmin):
    pass
