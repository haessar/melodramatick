from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from partial_date import PartialDateField


# This might be Operatick-specific (with Ensemble/Orchestra)
class Company(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'location'], name='unique_venue')
        ]
        ordering = ['location', 'name']

    def __str__(self):
        return '%s, %s' % (self.name, self.location)


class Performance(models.Model):
    work = models.ManyToManyField(settings.WORK_MODEL, related_name='performance')
    date = PartialDateField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    venue = models.ForeignKey(Venue, to_field="id", on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete=models.CASCADE)
    streamed = models.BooleanField(default=False)


@receiver([post_save, post_delete], sender=Performance, dispatch_uid="update_user_performance")
def clear_cache_performance(*args, **kwargs):
    cache.clear()
