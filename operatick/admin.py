from django.contrib import admin
from django.contrib.sites.models import Site

from melodramatick.work.admin import WorkAdmin
from .models import Opera
from .settings import SITE_ID


@admin.register(Opera)
class OperaAdmin(WorkAdmin):
    exclude = ['site']

    def save_model(self, request, obj, form, change):
        obj.site = Site.objects.get(id=SITE_ID)
        super().save_model(request, obj, form, change)
