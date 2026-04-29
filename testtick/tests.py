from django.apps import apps
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.staticfiles import finders
from django.test import RequestFactory, TestCase
from django.urls import reverse

from melodramatick.accounts.models import CustomUser
from melodramatick.composer.models import Composer
from melodramatick.work.models import Work

from .models import Testitem
from .views import TestitemDetailView, TestitemTableView


class TesttickSmokeTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_testtick_settings_wire_the_generated_app(self):
        self.assertTrue(apps.is_installed("testtick"))
        self.assertEqual(settings.WORK_MODEL, "testtick.Testitem")
        self.assertEqual(settings.SITE, "Testtick")
        self.assertTrue(issubclass(Testitem, Work))
        self.assertEqual(reverse("work:index"), "/works/")
        self.assertEqual(reverse("work:graphs"), "/works/graphs/")

    def test_shared_static_assets_are_available(self):
        self.assertIsNotNone(finders.find("images/banner.png"))
        self.assertIsNotNone(finders.find("images/favicon.ico"))

    def test_work_routes_render_with_minimal_testitem(self):
        site = Site.objects.get(id=settings.SITE_ID)
        composer = Composer.all_sites.create(
            first_name="Test",
            surname="Composer",
            nationality="Test",
        )
        composer.sites.add(site)
        testitem = Testitem.objects.create(
            composer=composer,
            title="Template Validation Work",
            year=2000,
            site=site,
        )
        user = CustomUser.objects.create_user(username="tester", password="password")
        index_request = self.factory.get(reverse("work:index"))
        index_request.user = user
        index_request.site = site
        detail_request = self.factory.get(reverse("work:work-detail", args=[testitem.pk]))
        detail_request.user = user
        detail_request.site = site

        index_response = TestitemTableView.as_view()(index_request)
        detail_response = TestitemDetailView.as_view()(detail_request, pk=testitem.pk)
        index_response.render()
        detail_response.render()

        self.assertEqual(index_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(b"Template Validation Work", index_response.content)
        self.assertIn(b"Template Validation Work", detail_response.content)
