import csv
import importlib
import io
import operator

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.filters import RelatedFieldListFilter
from django.contrib.admin.utils import quote
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch, path, reverse
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from .models import AKA, Genre, SubGenre, Work
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


class BaseWorkAdmin(admin.ModelAdmin):
    change_list_template = "admin/import_csv_changelist.html"
    exclude = ('site',)
    list_display = ("id", "title", "composer", "year", "sub_genre", "type")
    list_filter = (('composer', RelatedDropdownFilter), ('sub_genre__genre', RelatedDropdownFilter))
    actions = ['save_performance']
    inlines = [ListenInline, AKAInline, AlbumInline]
    search_fields = ['title']

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
                composer.complete = True
                composer.save()
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


class ChildChangeList(ChangeList):
    def url_for_result(self, result):
        """
        Override Changelist.url_for_result method so that the linked change form will be site-specific.
        e.g. In the Work admin, a Ballet object will redirect to admin:balletick_ballet_change
        rather than the default admin:work_work_change.
        """
        pk = getattr(result, self.pk_attname)
        if result.site.id == settings.SITE_ID:
            app_label = settings.SITE_APP_MAP[result.site.id]
            app_settings = importlib.import_module('{}.settings'.format(app_label))
            return reverse('admin:%s_%s_change' % (app_label,
                                                   app_settings.WORK_MODEL_RELATED_NAME),
                           args=(quote(pk),),
                           current_app=self.model_admin.admin_site.name)
        raise NoReverseMatch


class AllSitesRelatedDropdownFilter(RelatedDropdownFilter):
    def field_choices(self, field, request, model_admin):
        """
        Field.get_choices has a hard-coded reference to _default_manager, which is usually set to
        CurrentSiteManager. This method overrides that to allow the all_sites manager to be used
        instead.
        """
        ordering = self.field_admin_ordering(field, request, model_admin)
        choice_func = operator.attrgetter(
            field.remote_field.get_related_field().attname
            if hasattr(field.remote_field, 'get_related_field')
            else 'pk'
        )
        qs = field.remote_field.model.all_sites.complex_filter(field.get_limit_choices_to())
        if ordering:
            qs = qs.order_by(*ordering)
        return [(choice_func(x), str(x)) for x in qs]


@admin.register(Work)
class AllWorksAdmin(BaseWorkAdmin):
    exclude = ()
    list_display = ("id", "title", "composer", "year", "sub_genre", "site", "type")
    list_filter = (
        ('composer', AllSitesRelatedDropdownFilter),
        ('site', RelatedFieldListFilter))

    def get_changelist(self, request, **kwargs):
        return ChildChangeList

    def get_queryset(self, request):
        return Work.all_sites.all()

    def save_model(self, request, obj, form, change):
        """
        Use save_model method from admin.ModelAdmin
        """
        super(BaseWorkAdmin, self).save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "composer":
            kwargs["queryset"] = Composer.all_sites.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return False
