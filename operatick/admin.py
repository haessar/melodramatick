from django.contrib import admin

from melodramatick.work.admin import BaseWorkAdmin
from .models import Opera


@admin.register(Opera)
class OperaAdmin(BaseWorkAdmin):
    pass
