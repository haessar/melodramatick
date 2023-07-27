from django.contrib import admin
from django.contrib.sites.models import Site

from .models import Ballet
from .settings import SITE_ID
from melodramatick.work.admin import WorkAdmin


@admin.register(Ballet)
class BalletAdmin(WorkAdmin):
    exclude = ['site']

    def save_model(self, request, obj, form, change):
        obj.site = Site.objects.get(id=SITE_ID)
        super().save_model(request, obj, form, change)
