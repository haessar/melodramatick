import csv
import io

from django.contrib import admin
from django.db.utils import IntegrityError
from django.shortcuts import redirect, render
from django.urls import path

from .models import Composer, Group, Quote
from melodramatick.forms import CsvImportForm


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(composer__sites__in=[request.site])


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("quote", "composer")


@admin.register(Composer)
class ComposerAdmin(admin.ModelAdmin):
    change_list_template = "admin/import_csv_changelist.html"

    def get_queryset(self, request):
        return Composer.all_sites.all()

    def get_urls(self):
        urls = super().get_urls()
        return [path('import-csv/', self.import_csv), ] + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            rows = csv.DictReader(io_string)
            for row in rows:
                try:
                    Composer.all_sites.get_or_create(**dict(row, **{"complete": False}))
                except IntegrityError:
                    pass
            self.message_user(request, "Your csv file has been imported.")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/upload_file_form.html", payload
        )
