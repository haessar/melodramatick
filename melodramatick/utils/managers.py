from django.conf import settings
from polymorphic.managers import PolymorphicManager


class CurrentSitePolymorphicManager(PolymorphicManager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(site=settings.SITE_ID)
