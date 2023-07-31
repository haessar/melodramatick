__all__ = ["AKA", "Genre", "SubGenre", "Work"]
import datetime
import importlib
import random

from django.conf import settings
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from melodramatick.composer.models import Composer


class Genre(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class SubGenre(models.Model):
    name = models.CharField(max_length=50)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Work(models.Model):
    composer = models.ForeignKey(Composer, on_delete=models.PROTECT)
    title = models.CharField(max_length=100, db_index=True)
    year = models.IntegerField(choices=settings.YEAR_CHOICES, default=datetime.datetime.now().year)
    notes = models.TextField(null=True, blank=True)
    sub_genre = models.ForeignKey(SubGenre, on_delete=models.PROTECT, null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.PROTECT)
    objects = CurrentSiteManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['composer', 'title'], name='unique_work')
        ]
        ordering = ['title']
        # abstract = True

    def __str__(self):
        if len(Work.objects.filter(title=self.title)) > 1:
            return "{} ({})".format(self.title, self.composer.surname)
        return self.title

    @property
    def random_uri(self):
        albums = self.album.all()
        if albums:
            uris = [a.uri for a in albums]
            if len(uris) > 1:
                return uris[random.randint(0, len(uris)-1)]
            return uris[0]
        else:
            return None

    @property
    def era(self):
        for years, era in settings.ERAS_MAP:
            start, end = map(int, years.split("-"))
            if self.year in range(start, end + 1):
                return era

    @property
    def top_lists(self):
        return len(self.list_item.all())

    @property
    def type(self):
        app_label = settings.SITE_APP_MAP[self.site.id]
        app_settings = importlib.import_module('{}.settings'.format(app_label))
        return app_settings.WORK_MODEL_RELATED_NAME


@receiver([post_save, post_delete], sender=Work, dispatch_uid="update_work")
def clear_cache_work(*args, **kwargs):
    cache.clear()


class AKA(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="aka")
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title
