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
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from .models import AKA, Genre, SubGenre, Work
from melodramatick.forms import CsvImportForm
from melodramatick.composer.models import Composer, SiteComplete
from melodramatick.listen.forms import AlbumForm
from melodramatick.listen.models import Listen, Album
from melodramatick.performance.models import Performance


admin.site.register(Genre)


class ListenInline(admin.StackedInline):
    model = Listen
    extra = 0
    max_num = 1

    def has_add_permission(self, request, obj):
        return False


class AKAInline(admin.StackedInline):
    model = AKA
    extra = 0
    verbose_name = "title"
    verbose_name_plural = "also known as"


class AlbumInline(admin.TabularInline):
    model = Album
    extra = 0
    form = AlbumForm
    readonly_fields = ('uri', 'duration', 'image_url')
    exclude = ('id',)


@admin.register(SubGenre)
class SubGenreAdmin(admin.ModelAdmin):
    list_display = ("name", "genre")


class BaseWorkAdmin(PolymorphicChildModelAdmin):
    base_model = Work
    change_list_template = "admin/import_csv_changelist.html"
    exclude = ('site',)
    list_display = ("id", "title", "composer", "year", "sub_genre", "type")
    list_filter = (('composer', RelatedDropdownFilter), ('sub_genre__genre', RelatedDropdownFilter))
    actions = ['save_performance']
    inlines = [ListenInline, AKAInline, AlbumInline]

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
                    composer = Composer.all_sites.get(surname=row['composer'])
                    # TODO add current site to composer if it doesn't exist
                    row['composer'] = composer
                except ObjectDoesNotExist:
                    self.message_user(
                        request,
                        'Composer not recognised. Please add an entry for the composer whose work you wish to import.')
                    return redirect("..")
                try:
                    # TODO add site to creation?
                    Work.objects.get_or_create(**row)
                except IntegrityError:
                    pass
            # If CSV only contains work of single composer, assume it is full compilation of their work.
            if len(unique_composers) == 1:
                SiteComplete.objects.get_or_create(composer=composer, site=request.site, complete=True)
            self.message_user(request, "Your csv file has been imported.")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/upload_file_form.html", payload
        )

    def save_model(self, request, obj, form, change):
        """
        Add current site to saved model
        """
        obj.site = request.site
        super().save_model(request, obj, form, change)

    @admin.action(description='Add performance for each work')
    def save_performance(self, request, queryset):
        for work in queryset:
            p = Performance(user=request.user)
            p.save()
            p.work.add(work)
        self.message_user(request, "Your performances have been logged.")


@admin.register(Work)
class WorkParentAdmin(PolymorphicParentModelAdmin):
    base_model = Work
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ['title']

    def get_child_models(self):
        return (apps.get_model(settings.WORK_MODEL),)

    def get_search_results(self, request, queryset, search_term):
        """
        Filter autocomplete fields search results for current site.
        """
        return super().get_search_results(request, queryset.filter(site=request.site), search_term)
