from django.contrib import admin

from melodramatick.work.admin import BaseWorkAdmin
from .models import Testitem


@admin.register(Testitem)
class TestitemAdmin(BaseWorkAdmin):
    base_model = Testitem
