import csv
import io

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.shortcuts import redirect, render
from django.urls import path
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from .models import AKA, Genre, SubGenre
from melodramatick.forms import CsvImportForm
from melodramatick.composer.models import Composer
from melodramatick.listen.forms import AlbumForm
from melodramatick.listen.models import Listen, Album
from melodramatick.performance.models import Performance

admin.site.register(Genre)


class ListenInline(admin.StackedInline):
    model = Listen
    extra = 1
    max_num = 1


class AKAInline(admin.StackedInline):
    model = AKA
    extra = 0
    verbose_name = "title"
    verbose_name_plural = "also known as"


class AlbumInline(admin.TabularInline):
    model = Album
    extra = 0
    form = AlbumForm


@admin.register(SubGenre)
class SubGenreAdmin(admin.ModelAdmin):
    list_display = ("name", "genre")


# @admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    change_list_template = "admin/import_csv_changelist.html"
    list_display = ("id", "title", "composer", "year", "sub_genre")
    list_filter = (('composer', RelatedDropdownFilter), ('sub_genre__genre', RelatedDropdownFilter))
    actions = ['save_performance']
    # inlines = [ListenInline, AKAInline, AlbumInline]

    def get_urls(self):
        urls = super().get_urls()
        return [path('import-csv/', self.import_csv), ] + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            rows = csv.DictReader(io_string)
            unique_composers = set()
            for row in rows:
                unique_composers.add(row['composer'])
                try:
                    composer = Composer.objects.get(surname=row['composer'])
                    row['composer'] = composer
                except ObjectDoesNotExist:
                    self.message_user(
                        request,
                        'Composer not recognised. Please add an entry for the composer whose operas you wish to import.')
                    return redirect("..")
                try:
                    apps.get_model(settings.WORK_MODEL).objects.get_or_create(**row)
                except IntegrityError:
                    pass
            # If CSV only contains work of single composer, assume it is full compilation of their work.
            if len(unique_composers) == 1:
                composer.complete = True
                composer.save()
            self.message_user(request, "Your csv file has been imported.")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/upload_file_form.html", payload
        )

    @admin.action(description='Add performance for each work')
    def save_performance(self, request, queryset):
        for work in queryset:
            p = Performance(user=request.user)
            p.save()
            p.work.add(work)
        self.message_user(request, "Your performances have been logged.")
