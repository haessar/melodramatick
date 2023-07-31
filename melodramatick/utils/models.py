from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models


class AbstractSingleSiteModel(models.Model):
    site = models.ForeignKey(Site, on_delete=models.PROTECT)
    objects = CurrentSiteManager()
    all_sites = models.Manager()

    class Meta:
        abstract = True


class AbstractManySitesModel(models.Model):
    sites = models.ManyToManyField(Site)
    objects = CurrentSiteManager()
    all_sites = models.Manager()

    class Meta:
        abstract = True
