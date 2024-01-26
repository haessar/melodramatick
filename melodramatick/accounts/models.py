__all__ = ["CustomUser"]
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    spotify_player = models.CharField(choices=[("web", "Web player"), ("app", "Desktop app")], default="app", null=True,
                                      max_length=3)

    def __str__(self):
        return self.username
