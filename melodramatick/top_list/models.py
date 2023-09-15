__all__ = ["Award", "AwardLevel", "List", "ListItem", "Progress"]
import datetime
import math

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from django.utils.safestring import mark_safe

from melodramatick.performance.models import Performance
from melodramatick.utils.models import AbstractSingleSiteModel
from melodramatick.work.models import Work


class List(AbstractSingleSiteModel):
    items = models.ManyToManyField(Work, through='ListItem')
    name = models.CharField(max_length=100)
    publication = models.CharField(max_length=50)
    year = models.IntegerField(choices=settings.YEAR_CHOICES, default=datetime.datetime.now().year, blank=True, null=True)
    author = models.CharField(null=True, blank=True, max_length=50)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.publication)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'publication'], name='unique_list')
        ]
        ordering = ['-year']

    @property
    def length(self):
        return len(self.listitem_set.all())


class ListItem(models.Model):
    item = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='list_item')
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField(db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['item', 'list', 'position'], name='unique_list_item')
        ]
        ordering = ['position']

    def __str__(self):
        return "{} - {}".format(self.item, self.list)


class AwardLevel(models.Model):
    rank = models.SmallIntegerField(primary_key=True)
    level = models.CharField(max_length=10)
    color_hex = models.CharField(max_length=10)

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return self.level


class Award(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete=models.CASCADE, related_name="award")
    level = models.ForeignKey(AwardLevel, on_delete=models.CASCADE)

    class Meta:
        ordering = ['level']

    @property
    def html_icon(self):
        return mark_safe('<i class="fa-solid fa-trophy fa-xl" style="color: {};" title="{}"></i>'.format(
            self.level.color_hex,
            str(self.level).title()))


class Progress(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete=models.CASCADE, related_name="progress")
    ratio = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    count = models.IntegerField(default=0)

    @property
    def as_percentage(self):
        return round(self.ratio * 100)

    @property
    def ticks_to_next_award(self):
        """
        Returns a tuple of two integers:
            1. number of list ticks required til next award
            2. rank of the next award
        Will return (0, 0) if top award has already been achieved
        """
        if 0.9 <= self.ratio < 1.0:
            distance = 1.0 - self.ratio
            rank = 1
        elif 0.75 <= self.ratio < 0.9:
            distance = 0.9 - self.ratio
            rank = 2
        elif 0.5 <= self.ratio < 0.75:
            distance = 0.75 - self.ratio
            rank = 3
        elif self.ratio < 0.5:
            distance = 0.5 - self.ratio
            rank = 4
        else:
            return 0, 0
        return math.ceil(distance * self.list.length), rank


@receiver(user_logged_in)
@receiver(m2m_changed, sender=Performance.work.through)
@receiver(pre_delete, sender=Performance)
def update_user_award(**kwargs):
    from melodramatick.tasks import update_user_award_shared_task
    instance = kwargs.get("instance")
    if instance:
        user_id = instance.user.id
        instance_id = instance.id
    else:
        user_id = kwargs["user"].id
        instance_id = None
    update_user_award_shared_task.delay(user_id, instance_id)
