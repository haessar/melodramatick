__all__ = ["Album", "Listen"]
from django.conf import settings
from django.core.cache import cache
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from melodramatick.utils.models import AbstractSingleSiteModel
from melodramatick.utils.spotify_api import get_album_duration, get_album_image, get_playlist_duration, get_playlist_image
from melodramatick.work.models import Work


class Listen(AbstractSingleSiteModel):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='listen')
    tally = models.PositiveSmallIntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['work', 'user'], name='unique_listen')
        ]
        verbose_name = "Listens"
        verbose_name_plural = "Listens"
        ordering = ['updated_at']

    def __str__(self):
        return self.user.username


@receiver([post_save, post_delete], sender=Listen, dispatch_uid="update_user_listen")
def clear_cache_listen(*args, **kwargs):
    cache.clear()


class Album(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='album')
    duration = models.IntegerField(default=0)
    id = models.CharField(primary_key=True, max_length=220,
                          validators=[RegexValidator(regex=r"^([a-zA-Z0-9]{22}[,]?)+$")])
    uri = models.CharField(max_length=220)
    image_url = models.URLField(null=True, blank=True)

    @property
    def image(self):
        if self.image_url:
            return self.image_url


@receiver(post_save, sender=Album)
def set_image_url(sender, instance, **kwargs):
    if not instance.image_url:
        if "album" in instance.uri:
            image_url = get_album_image(instance.uri)
        # else:
        #     image_url = get_playlist_image(instance.uri)
        if image_url:
            sender.objects.filter(pk=instance.pk).update(image_url=image_url)


@receiver(post_save, sender=Album)
def set_duration(sender, instance, **kwargs):
    if not instance.duration:
        if "album" in instance.uri:
            duration = get_album_duration(instance.uri)
        # else:
        #     duration = get_playlist_duration(instance.uri)
        if duration:
            sender.objects.filter(pk=instance.pk).update(duration=duration)
