from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.test import TestCase

from .admin import ComposerAdmin
from .filters import ComposerFilter
from .models import Composer
from .views import ComposerAutocomplete, ComposerListView
from melodramatick.accounts.models import CustomUser


class ComposerModelTestCase(TestCase):
    fixtures = ["composer.json", "sites.json"]

    def setUp(self):
        self.composer = Composer.all_sites.get(surname="Adam")

    def test_str(self):
        self.assertEqual(str(self.composer), "Adam, Adolphe")

    def test_full_name(self):
        self.assertEqual(self.composer.full_name(), "Adolphe Adam")

    def test_unique_constraint(self):
        with self.assertRaisesMessage(IntegrityError, "UNIQUE"):
            # Shared surname and first_name, despite different nationality and complete values to those in db.
            Composer.all_sites.create(surname="Adam", first_name="Adolphe", nationality="Swiss", complete=True)


class ComposerAdminTestCase(TestCase):
    fixtures = ["composer.json", "sites.json"]

    def setUp(self):
        self.composer_admin = ComposerAdmin(model=Composer, admin_site=AdminSite())

    def test_get_queryset(self):
        request = self.client.get("/").wsgi_request
        qs = self.composer_admin.get_queryset(request)
        # All composers should be visible on composer admin, regardless of site
        self.assertQuerysetEqual(qs, Composer.all_sites.all())

    def test_import_csv(self):
        endpoint = "/admin/composer/composer/import-csv/"
        csv_str = b"surname,first_name,nationality,gender\nBerg,Alban,Austrian,M"

        csv_file = SimpleUploadedFile("composers.csv", csv_str)
        num_before = len(Composer.all_sites.all())
        response = self.client.post(endpoint, {"csv_file": csv_file})
        # Should add one composer to database, accessible from "all_sites" manager
        # but not "objects" manager (i.e. it's not yet been assigned a site)
        self.assertEqual(num_before + 1, len(Composer.all_sites.all()))
        # POST request should redirect to previous page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, "..")

        csv_str = b"INCORRECT_FIELD,first_name,nationality,gender\nBerg,Alban,Austrian,M"
        csv_file = SimpleUploadedFile("composers.csv", csv_str)
        response = self.client.post(endpoint, {"csv_file": csv_file})
        # Submission of faulty file will not add anything to database...
        self.assertEqual(num_before + 1, len(Composer.all_sites.all()))
        # ...but result in redirect to current page with error message
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, endpoint)
        self.assertIn("Cannot resolve keyword 'INCORRECT_FIELD' into field",
                      str(list(get_messages(response.wsgi_request))[-1]))

        response = self.client.get(endpoint)
        # GET request should return upload file form HTML
        self.assertIsInstance(response, HttpResponse)


class ComposerFilterTestCase(TestCase):
    fixtures = ["composer.json", "sites.json"]

    def setUp(self):
        self.filter = ComposerFilter()

    def test_group_filter(self):
        # TODO Requires group.json fixture
        pass


class ComposerAutocompleteTestCase(TestCase):
    fixtures = ["composer.json", "sites.json", "user.json"]

    def setUp(self):
        response = self.client.get("/")
        self.request = response.wsgi_request
        self.view = ComposerAutocomplete()
        self.view.setup(self.request)

    def test_get_queryset(self):
        # Return empty queryset when user is not authenticated
        self.assertQuerysetEqual(self.view.get_queryset(), [])
        # Return all composers when no query string given
        self.request.user = CustomUser.objects.get(id=1)
        self.view.q = ""
        qs = self.view.get_queryset()
        if self.request.site.id == 1:
            self.assertEquals(len(qs), 2)
        elif self.request.site.id == 2:
            self.assertEquals(len(qs), 1)
        self.view.q = "b"
        qs = self.view.get_queryset()
        if self.request.site.id == 1:
            # Return <QuerySet [<Composer: Beethoven, Ludwig van>]> when q is starting letter
            self.assertQuerysetEqual(qs, Composer.objects.filter(surname="Beethoven"))
        elif self.request.site.id == 2:
            # Return empty queryset when no composer on site contains q as starting letter
            self.assertQuerysetEqual(qs, [])


class ComposerListViewTestCase(TestCase):
    fixtures = ["composer.json", "sites.json", "work.json"]

    def setUp(self):
        response = self.client.get("/")
        self.request = response.wsgi_request
        self.view = ComposerListView()
        self.view.setup(self.request)

    def test_get_table_data(self):
        table_data = self.view.get_table_data()
        # Assertion - <Composer: Adam, Adolphe> has two works overall: one on each site.
        if self.request.site.id == 1:
            self.assertListEqual(
                list(table_data.values('total_works', 'total_top_lists').order_by('id')),
                [{'total_works': 1, 'total_top_lists': 0},  # <Composer: Adam, Adolphe>
                 {'total_works': 1, 'total_top_lists': 0}]  # <Composer: Beethoven, Ludwig van>
            )
        elif self.request.site.id == 2:
            self.assertQuerysetEqual(
                table_data.values('total_works', 'total_top_lists'),
                values=[{'total_works': 1, 'total_top_lists': 0}]  # <Composer: Adam, Adolphe>
            )
        # TODO - Add assertion for top_lists_to_works annotation

    def test_get_table_kwargs(self):
        table_kwargs = self.view.get_table_kwargs()
        self.assertIsInstance(table_kwargs, dict)
        self.assertIn('order_by', table_kwargs)
