__all__ = ["GENDER_CHOICES", "Composer", "Group", "Quote"]
from datetime import datetime

from django.db import models

from melodramatick.utils.models import AbstractManySitesModel, AbstractSingleSiteModel


GENDER_CHOICES = [("M", "Male"), ("F", "Female")]


class Composer(AbstractManySitesModel):
    surname = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    nationality = models.CharField(max_length=20)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, default="M")
    birth_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['surname', 'first_name'], name='unique_composer')
        ]
        ordering = ['surname']

    def __str__(self):
        return "{}, {}".format(self.surname, self.first_name)

    def full_name(self):
        return '{} {}'.format(self.first_name, self.surname)

    @property
    def anniversary(self):
        if self.birth_date:
            today = datetime.now()
            if self.birth_date.month == today.month and self.birth_date.day == today.day:
                return today.year - self.birth_date.year


class Group(models.Model):
    name = models.CharField(max_length=50)
    composer = models.ManyToManyField(Composer, related_name='group')

    def __str__(self):
        return self.name


class Quote(models.Model):
    id = models.IntegerField(primary_key=True)
    composer = models.ForeignKey(Composer, on_delete=models.CASCADE)
    quote = models.CharField(max_length=500)

    def __str__(self):
        return self.quote


class SiteComplete(AbstractSingleSiteModel):
    composer = models.ForeignKey(Composer, on_delete=models.CASCADE, related_name="sitecomplete")
    complete = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['composer', 'site'], name='unique_sitecomplete')
        ]
        verbose_name_plural = "Site complete"
