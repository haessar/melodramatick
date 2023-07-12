import datetime
import random

from django.apps import apps
from django.conf import settings
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
    title = models.CharField(max_length=100)
    # language = models.CharField(choices=settings.LANGUAGE_CHOICES, max_length=2, blank=True)
    year = models.IntegerField(choices=settings.YEAR_CHOICES, default=datetime.datetime.now().year)
    notes = models.TextField(null=True, blank=True)
    sub_genre = models.ForeignKey(SubGenre, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['composer', 'title'], name='unique_work')
        ]
        ordering = ['title']
        abstract = True

    def __str__(self):
        if len(apps.get_model(settings.WORK_MODEL).objects.filter(title=self.title)) > 1:
            return "{} ({})".format(self.title, self.composer.surname)
        return self.title

    @property
    def random_uri(self):
        playlists = self.playlist.all()
        if playlists:
            uris = [p.uri for p in playlists]
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
        return len(self.list_work.all())

    # @property
    # def language_verbose(self):
    #     return [v for (c, v) in settings.LANGUAGE_CHOICES if c == self.language][0]


@receiver([post_save, post_delete], sender=Work, dispatch_uid="update_work")
def clear_cache_work(*args, **kwargs):
    cache.clear()


class AKA(models.Model):
    work = models.ForeignKey(settings.WORK_MODEL, on_delete=models.CASCADE, related_name="aka")
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title
