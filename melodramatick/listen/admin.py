from django.contrib import admin

from .models import Listen


@admin.register(Listen)
class ListenAdmin(admin.ModelAdmin):
    exclude = ['site']
