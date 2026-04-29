from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from melodramatick.accounts.models import CustomUser
from melodramatick.performance.models import Performance
from .admin import ListAdmin, ListItemAdmin, ListItemInline
from .models import Award, AwardLevel, List, ListItem, Progress, update_user_award
from .views import TopListView


class TopListViewTestCase(TestCase):
    fixtures = ["testtick_composer.json", "testtick_top_list.json", "user.json", "testtick_work.json",
                "testtick_testitem.json"]

    def setUp(self):
        response = self.client.get("/")
        self.request = response.wsgi_request
        self.view = TopListView()
        self.view.setup(self.request)

    def test_get_table_data(self):
        table_data = self.view.get_table_data()
        self.assertListEqual(
            list(table_data.values('max_position', 'list_work_count').order_by('id')),
            [{'max_position': 2, 'list_work_count': 2},  # <List: Top test items - Example Dot Com>
             {'max_position': 1, 'list_work_count': 1}]  # <List: Another Test List - Example Dot Com>
        )


class TopListModelTestCase(TestCase):
    fixtures = ["testtick_composer.json", "testtick_top_list.json", "user.json", "testtick_work.json",
                "testtick_testitem.json"]

    def test_list_str_and_length(self):
        list_obj = List.objects.get(id=1)

        self.assertEqual(str(list_obj), "Top test items - Example Dot Com")
        self.assertEqual(list_obj.length, 2)

    def test_list_item_str(self):
        list_item = ListItem.objects.get(id=1)

        self.assertEqual(str(list_item), "Template Validation Work - Top test items - Example Dot Com")

    def test_award_level_str(self):
        self.assertEqual(str(AwardLevel.objects.get(rank=1)), "platinum")

    def test_award_html_icon(self):
        award = Award.objects.create(
            user=CustomUser.objects.get(id=1),
            list=List.objects.get(id=1),
            level=AwardLevel.objects.get(rank=2),
        )

        self.assertEqual(
            award.html_icon,
            '<i class="fa-solid fa-trophy fa-xl" style="color: #FFD700;" title="Gold"></i>',
        )

    def test_progress_as_percentage(self):
        progress = Progress(ratio=0.756)

        self.assertEqual(progress.as_percentage, 76)

    def test_ticks_to_next_award_for_platinum_progress(self):
        progress = Progress(list=List.objects.get(id=1), ratio=0.9)

        self.assertEqual(progress.ticks_to_next_award, (1, 1))

    def test_ticks_to_next_award_uses_tick_count_for_platinum_progress(self):
        list_obj = List.objects.get(id=1)
        works = list(ListItem.objects.filter(list=list_obj).values_list("item", flat=True))
        for position in range(3, 13):
            ListItem.objects.create(
                item_id=works[position % len(works)],
                list=list_obj,
                position=position,
            )
        progress = Progress(list=list_obj, ratio=11 / 12, count=11)

        self.assertEqual(progress.ticks_to_next_award, (1, 1))

    def test_ticks_to_next_award_for_gold_progress(self):
        progress = Progress(list=List.objects.get(id=1), ratio=0.75)

        self.assertEqual(progress.ticks_to_next_award, (1, 2))

    def test_ticks_to_next_award_for_silver_progress(self):
        progress = Progress(list=List.objects.get(id=1), ratio=0.5)

        self.assertEqual(progress.ticks_to_next_award, (1, 3))

    def test_ticks_to_next_award_for_bronze_progress(self):
        progress = Progress(list=List.objects.get(id=1), ratio=0.25)

        self.assertEqual(progress.ticks_to_next_award, (1, 4))

    def test_ticks_to_next_award_when_complete(self):
        progress = Progress(list=List.objects.get(id=1), ratio=1.0)

        self.assertEqual(progress.ticks_to_next_award, (0, 0))


class UpdateUserAwardSignalTestCase(TestCase):
    fixtures = ["user.json", "testtick_company.json", "testtick_composer.json", "testtick_performance.json",
                "testtick_testitem.json", "testtick_venue.json", "testtick_work.json"]

    @patch("melodramatick.tasks.update_user_award_shared_task.delay")
    def test_update_user_award_with_instance(self, delay):
        performance = Performance.objects.get(id=1)

        update_user_award(instance=performance)

        delay.assert_called_once_with(1, 1)

    @patch("melodramatick.tasks.update_user_award_shared_task.delay")
    def test_update_user_award_with_login_user(self, delay):
        user = CustomUser.objects.get(id=2)

        update_user_award(user=user)

        delay.assert_called_once_with(2, None)


class ListAdminTestCase(TestCase):
    fixtures = ["testtick_composer.json", "testtick_top_list.json", "user.json", "testtick_work.json",
                "testtick_testitem.json"]

    def setUp(self):
        self.admin = ListAdmin(model=List, admin_site=AdminSite())
        self.factory = RequestFactory()
        self.client.force_login(CustomUser.objects.get(id=1))
        self.request = self.client.get("/").wsgi_request
        self.request.user = CustomUser.objects.get(id=1)

    def get_admin_post_request(self, txt_file):
        request = self.factory.post("/admin/top_list/list/import-txt/", {"txt_file": txt_file})
        request.user = self.request.user
        request.site = self.request.site
        setattr(request, "session", self.client.session)
        setattr(request, "_messages", FallbackStorage(request))
        return request

    def test_list_item_inline_uses_item_autocomplete(self):
        self.assertEqual(ListItemInline.autocomplete_fields, ["item"])

    def test_get_urls_adds_import_txt_endpoint(self):
        self.assertEqual(self.admin.get_urls()[0].pattern._route, "import-txt/")

    def test_parse_filename(self):
        txt_file = SimpleUploadedFile("top_template_works-example_publication.txt", b"")

        self.assertEqual(
            self.admin.parse_filename(txt_file),
            ("Top Template Works", "Example Publication"),
        )

    def test_save_model_sets_current_site(self):
        obj = List(name="Admin Saved List", publication="Test Publisher", year=2024)

        self.admin.save_model(self.request, obj, form=None, change=False)

        self.assertEqual(obj.site, self.request.site)
        self.assertTrue(List.objects.filter(name="Admin Saved List", site=self.request.site).exists())

    def test_import_txt_get_renders_form_with_docs(self):
        response = self.admin.import_txt(self.request)

        self.assertIsInstance(response, HttpResponse)
        self.assertContains(response, "Body should contain comma-separated list")

    def test_import_txt_rejects_bad_filename(self):
        txt_file = SimpleUploadedFile("bad_filename.txt", b"Template Validation Work")
        request = self.get_admin_post_request(txt_file)

        response = self.admin.import_txt(request)

        self.assertEqual(response.url, "..")
        self.assertIn("correct format", str(list(get_messages(request))[-1]))

    def test_import_txt_rejects_unknown_work(self):
        txt_file = SimpleUploadedFile("top_items-example.txt", b"Not A Real Work")
        request = self.get_admin_post_request(txt_file)

        response = self.admin.import_txt(request)

        self.assertEqual(response.url, "..")
        self.assertFalse(List.objects.filter(name="Top Items", publication="Example").exists())
        self.assertIn("not recognised", str(list(get_messages(request))[-1]))

    def test_import_txt_creates_list_items(self):
        txt_file = SimpleUploadedFile(
            "top_items-example.txt",
            b"Template Validation Work,Secondary Template Work",
        )
        request = self.get_admin_post_request(txt_file)

        response = self.admin.import_txt(request)

        imported = List.objects.get(name="Top Items", publication="Example")
        self.assertEqual(response.url, "..")
        self.assertEqual(imported.site, self.request.site)
        self.assertQuerysetEqual(
            imported.listitem_set.order_by("position").values_list("item_id", "position"),
            [(230, 1), (435, 2)],
            transform=tuple,
        )
        self.assertIn("txt file has been imported", str(list(get_messages(request))[-1]))


class ListItemAdminTestCase(TestCase):
    fixtures = ["testtick_composer.json", "testtick_top_list.json", "user.json", "testtick_work.json",
                "testtick_testitem.json"]

    def setUp(self):
        self.admin = ListItemAdmin(model=ListItem, admin_site=AdminSite())
        self.factory = RequestFactory()

    def test_response_add_redirects_to_incremented_addanother_url(self):
        request = self.factory.post("/", {"_addanother": "1", "list": "1", "position": "2"})

        response = self.admin.response_add(request, ListItem.objects.get(id=1))

        self.assertEqual(
            response.url,
            "{}?list=1&position=3".format(reverse("admin:top_list_listitem_add")),
        )

    def test_response_add_redirects_to_changelist_without_addanother(self):
        request = self.factory.post("/", {"list": "1", "position": "2"})

        response = self.admin.response_add(request, ListItem.objects.get(id=1))

        self.assertEqual(response.url, reverse("admin:top_list_listitem_changelist"))
