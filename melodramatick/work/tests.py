from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from melodramatick.accounts.models import CustomUser
from melodramatick.composer.models import Composer, SiteComplete
from melodramatick.performance.models import Performance
from testtick.admin import TestitemAdmin
from testtick.models import Testitem

from .admin import AKAInline, ListenInline, WorkParentAdmin
from .models import Work


class WorkDetailViewTestCase(TestCase):
    fixtures = ['user.json', 'testtick_listen.json', 'testtick_work.json',
                'testtick_testitem.json', 'testtick_composer.json']

    def setUp(self):
        self.client.force_login(CustomUser.objects.get(id=2))

    @patch("melodramatick.work.views.render_tickbox", return_value=(True, "<img>fake</img>"))
    def test_get_context_data(self, rt):
        response = self.client.get("/works/230")
        self.assertIn("ticked", response.context_data)
        self.assertIn("tickbox", response.context_data)
        self.assertEqual(response.context_data['listen_count'], 3)
        response = self.client.get("/works/435")
        self.assertEqual(response.context_data['listen_count'], 0)


class WorkAdminTestCase(TestCase):
    fixtures = ['user.json', 'testtick_work.json', 'testtick_testitem.json', 'testtick_composer.json']

    def setUp(self):
        self.admin = TestitemAdmin(model=Testitem, admin_site=AdminSite())
        self.factory = RequestFactory()
        self.client.force_login(CustomUser.objects.get(id=1))
        self.request = self.client.get("/").wsgi_request
        self.request.user = CustomUser.objects.get(id=1)

    def get_admin_post_request(self, csv_file):
        request = self.factory.post("/admin/testtick/testitem/import-csv/", {"csv_file": csv_file})
        request.user = self.request.user
        request.site = self.request.site
        setattr(request, "session", self.client.session)
        setattr(request, "_messages", FallbackStorage(request))
        return request

    def test_inlines(self):
        self.assertFalse(ListenInline(Testitem, AdminSite()).has_add_permission(self.request, Testitem.objects.first()))
        self.assertEqual(AKAInline.verbose_name, "title")
        self.assertEqual(AKAInline.verbose_name_plural, "also known as")

    def test_get_urls_adds_import_csv_endpoint(self):
        self.assertEqual(self.admin.get_urls()[0].pattern._route, "import-csv/")

    def test_import_csv_get_renders_form(self):
        response = self.admin.import_csv(self.request)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)

    def test_import_csv_redirects_when_composer_is_unknown(self):
        csv_file = SimpleUploadedFile(
            "works.csv",
            b"composer,title,year\nUnknown,Missing Composer Work,2001\n",
        )
        request = self.get_admin_post_request(csv_file)

        response = self.admin.import_csv(request)

        self.assertEqual(response.url, "..")
        self.assertFalse(Testitem.objects.filter(title="Missing Composer Work").exists())
        self.assertIn("Composer not recognised", str(list(get_messages(request))[-1]))

    def test_import_csv_creates_work_and_site_complete_for_single_composer(self):
        csv_file = SimpleUploadedFile(
            "works.csv",
            b"composer,title,year\nAdam,Imported Template Work,2001\n",
        )
        request = self.get_admin_post_request(csv_file)

        response = self.admin.import_csv(request)

        self.assertEqual(response.url, "..")
        imported = Work.objects.get(title="Imported Template Work")
        self.assertEqual(imported.composer, Composer.objects.get(surname="Adam"))
        self.assertEqual(imported.site, self.request.site)
        self.assertTrue(
            SiteComplete.objects.filter(
                composer=Composer.objects.get(surname="Adam"),
                site=self.request.site,
                complete=True,
            ).exists()
        )

    def test_save_model_sets_current_site(self):
        obj = Testitem(
            composer=Composer.objects.get(surname="Adam"),
            title="Saved Through Admin",
            year=2002,
        )

        self.admin.save_model(self.request, obj, form=None, change=False)

        self.assertEqual(obj.site, self.request.site)
        self.assertTrue(Testitem.objects.filter(title="Saved Through Admin", site=self.request.site).exists())

    def test_save_performance_creates_performance_for_each_work(self):
        initial_count = Performance.objects.count()

        self.admin.save_performance(self.request, Testitem.objects.filter(pk__in=[230, 435]))

        self.assertEqual(Performance.objects.count(), initial_count + 2)
        self.assertEqual(
            sorted(performance.work.first().pk for performance in Performance.objects.order_by("-id")[:2]),
            [230, 435],
        )
        self.assertIn("performances have been logged", str(list(get_messages(self.request))[-1]))


class WorkParentAdminTestCase(TestCase):
    fixtures = ['user.json', 'testtick_work.json', 'testtick_testitem.json', 'testtick_composer.json']

    def setUp(self):
        self.admin = WorkParentAdmin(model=Work, admin_site=AdminSite())
        self.client.force_login(CustomUser.objects.get(id=1))
        self.request = self.client.get("/").wsgi_request
        self.request.user = CustomUser.objects.get(id=1)

    def test_get_child_models_uses_active_work_model(self):
        self.assertEqual(self.admin.get_child_models(), (Testitem,))

    def test_get_search_results_filters_by_current_site(self):
        queryset, use_distinct = self.admin.get_search_results(
            self.request,
            Work.objects.filter(pk=230),
            "",
        )

        self.assertFalse(use_distinct)
        self.assertQuerysetEqual(queryset, Work.objects.filter(pk=230), transform=lambda obj: obj)
