import os

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse

from melodramatick.forms import TxtImportForm
from melodramatick.work.models import Work
from .models import List, ListItem


class ListItemInline(admin.TabularInline):
    model = ListItem
    extra = 0


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    change_list_template = "admin/import_txt_changelist.html"
    list_display = ("id", "name", "publication")
    inlines = [ListItemInline]
    exclude = ['site']
    list_select_related = True

    def save_model(self, request, obj, form, change):
        obj.site = request.site
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        return [path('import-txt/', self.import_txt), ] + urls

    @staticmethod
    def parse_filename(file):
        """Extract list name and publication name from file in format "<list_name>-<pub_name>.<ext>"
        e.g. "top_100_operas-best_publication.txt" yields "Top 100 Operas", "Best Publication"
        """
        filename = os.path.splitext(file.name)[0].replace('_', ' ')
        list_name, pub_name = filename.title().split('-')
        return list_name.strip(), pub_name.strip()

    def import_txt(self, request):
        """Body should contain comma-separated list of work titles that match those in db.
        e.g. "Aida,La finta semplice,Rigoletto"
        """
        if request.method == "POST":
            txt_file = request.FILES["txt_file"]
            try:
                list_name, pub_name = self.parse_filename(txt_file)
            except ValueError:
                self.message_user(request, "Ensure filename {} is in correct format".format(txt_file.name))
                return redirect("..")
            list = List.objects.create(name=list_name, publication=pub_name)
            decoded_file = txt_file.read().decode('utf-8')
            titles = decoded_file.split(',')
            for idx, title in enumerate(titles, 1):
                try:
                    work = Work.objects.get(title=title)
                    ListItem.objects.create(list=list, item=work, position=idx)
                except ObjectDoesNotExist:
                    self.message_user(request,
                                      "Work '{}' not recognised. Please ensure title matches that in database.".format(title))
                    return redirect("..")
            self.message_user(request, "Your txt file has been imported.")
            return redirect("..")
        form = TxtImportForm()
        payload = {"form": form, "docs": '\n'.join((self.parse_filename.__doc__, self.import_txt.__doc__))}
        return render(
            request, "admin/upload_file_form.html", payload
        )


@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "list")

    def response_add(self, request, obj, post_url_continue=None):
        """
        Keep the list and increment position for when adding further list items (for convenience)
        """
        if '_addanother' in request.POST:
            url = reverse("admin:top_list_listitem_add")
            list_id = request.POST['list']
            last_pos = request.POST['position']
            qs = '?list={}&position={}'.format(list_id, int(last_pos) + 1)
            return HttpResponseRedirect(''.join((url, qs)))
        else:
            return HttpResponseRedirect(reverse("admin:top_list_listitem_changelist"))
