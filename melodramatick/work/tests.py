from unittest.mock import patch

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Count, Exists, OuterRef, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from melodramatick.accounts.models import CustomUser
from melodramatick.composer.models import Composer, Group, SiteComplete
from melodramatick.listen.models import Listen
from melodramatick.performance.models import Performance
from testtick.admin import TestitemAdmin
from testtick.filters import TestitemFilter
from testtick.models import Testitem
from testtick.views import TestitemTableView

from .admin import AKAInline, ListenInline, WorkParentAdmin
from .filters import AllRangeFilter, EraChoiceFilter, GenreChoiceFilter
from .models import Genre, SubGenre, Work
from . import plots as work_plots
from .views import WorkGraphsView


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


class WorkTableViewTestCase(TestCase):
    fixtures = [
        'user.json',
        'testtick_album.json',
        'testtick_company.json',
        'testtick_composer.json',
        'testtick_listen.json',
        'testtick_performance.json',
        'testtick_testitem.json',
        'testtick_top_list.json',
        'testtick_venue.json',
        'testtick_work.json',
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.get(id=1)
        self.client.force_login(self.user)

    @patch("melodramatick.work.views.random.randint", return_value=0)
    def test_render_to_response_adds_random_playback_context(self, randint):
        response = self.client.get("/works/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["random_uri"], "spotify:album:1234567890abcdefGHIJKL")
        self.assertEqual(response.context_data["work_id"], 230)

    def test_get_table_data_adds_user_annotations(self):
        request = self.factory.get("/works/")
        request.user = self.user
        view = TestitemTableView()
        view.setup(request)
        view.object_list = Testitem.objects.all()

        data = {
            item["id"]: item
            for item in view.get_table_data().values(
                "id",
                "user_listens",
                "user_performances",
                "total_lists",
            )
        }

        self.assertEqual(data[230]["user_listens"], 1)
        self.assertEqual(data[230]["user_performances"], 2)
        self.assertEqual(data[230]["total_lists"], 2)
        self.assertEqual(data[435]["user_listens"], 2)
        self.assertEqual(data[435]["user_performances"], 2)
        self.assertEqual(data[435]["total_lists"], 1)
        self.assertIsNone(data[722]["user_listens"])
        self.assertEqual(data[722]["user_performances"], 0)
        self.assertEqual(data[722]["total_lists"], 0)

    def get_table_kwargs_for_querystring(self, path):
        request = self.factory.get(path)
        request.user = self.user
        view = TestitemTableView()
        view.setup(request)
        return view.get_table_kwargs()

    def test_get_table_kwargs_defaults(self):
        kwargs = self.get_table_kwargs_for_querystring("/works/")

        self.assertEqual(kwargs["order_by"], ("total_lists", "year"))
        self.assertEqual(kwargs["exclude"], {"position", "duration", "uri"})

    def test_get_table_kwargs_for_top_list_filter(self):
        kwargs = self.get_table_kwargs_for_querystring("/works/?top_list=1")

        self.assertEqual(kwargs["order_by"], ("position",))
        self.assertIn("top_list", kwargs["exclude"])
        self.assertIn("total_lists", kwargs["exclude"])
        self.assertNotIn("position", kwargs["exclude"])

    def test_get_table_kwargs_for_duration_filter(self):
        kwargs = self.get_table_kwargs_for_querystring("/works/?duration_range_min=100")

        self.assertEqual(kwargs["order_by"], ("duration",))
        self.assertIn("duration_range_min", kwargs["exclude"])
        self.assertIn("random_uri", kwargs["exclude"])
        self.assertNotIn("duration", kwargs["exclude"])
        self.assertNotIn("uri", kwargs["exclude"])


class WorkFilterTestCase(TestCase):
    fixtures = [
        'testtick_album.json',
        'testtick_composer.json',
        'testtick_testitem.json',
        'testtick_top_list.json',
        'testtick_work.json',
    ]

    def ids_for_filter(self, data):
        filterset = TestitemFilter(data=data, queryset=Testitem.objects.all())

        self.assertTrue(filterset.is_valid(), filterset.form.errors)
        return list(filterset.qs.order_by("id").values_list("id", flat=True))

    def test_filter_without_data_returns_all_works(self):
        self.assertEqual(self.ids_for_filter({}), [230, 435, 722])

    def test_era_choice_filter_returns_unfiltered_queryset_without_value(self):
        filter_obj = EraChoiceFilter()
        queryset = Testitem.objects.all()

        self.assertEqual(
            list(filter_obj.filter(queryset, "").order_by("id").values_list("id", flat=True)),
            [230, 435, 722],
        )

    def test_era_choice_filter_filters_inclusive_year_range(self):
        filter_obj = EraChoiceFilter()

        self.assertEqual(
            list(filter_obj.filter(Testitem.objects.all(), "1750-1809").order_by("id").values_list("id", flat=True)),
            [230],
        )

    def test_all_range_filter_uses_custom_range_widget_bounds(self):
        filter_obj = AllRangeFilter()

        self.assertEqual(filter_obj.extra["widget"].attrs["data-range_min"], 0)
        self.assertEqual(filter_obj.extra["widget"].attrs["data-range_max"], 360)

    def test_genre_choice_filter_choices_include_genres_and_used_orphan_subgenres(self):
        site = Site.objects.get(pk=settings.SITE_ID)
        genre = Genre.objects.create(name="Fixture Genre", site=site)
        child_sub_genre = SubGenre.objects.create(name="Child Subgenre", genre=genre, site=site)
        orphan_sub_genre = SubGenre.objects.create(name="Orphan Subgenre", site=site)
        Work.objects.filter(pk=230).update(sub_genre=child_sub_genre)
        Work.objects.filter(pk=435).update(sub_genre=orphan_sub_genre)
        filter_obj = GenreChoiceFilter()

        self.assertEqual(
            filter_obj.get_choices(),
            [(genre, "Fixture Genre"), (orphan_sub_genre, "> Orphan Subgenre")],
        )
        self.assertEqual(
            list(filter_obj.field.choices),
            [("", "---------"), (genre, "Fixture Genre"), (orphan_sub_genre, "> Orphan Subgenre")],
        )

    def test_filter_by_composer(self):
        self.assertEqual(self.ids_for_filter({"composer": 1}), [435, 722])

    def test_filter_by_composer_group(self):
        group = Group.objects.create(name="Adam Group")
        group.composer.add(Composer.objects.get(pk=1))

        self.assertEqual(self.ids_for_filter({"composer_group": group.pk}), [435, 722])

    def test_filter_by_era(self):
        self.assertEqual(self.ids_for_filter({"era": "1810-1839"}), [435])

    def test_filter_by_top_list_adds_list_rank_annotation(self):
        filterset = TestitemFilter(data={"top_list": 1}, queryset=Testitem.objects.all())

        self.assertTrue(filterset.is_valid(), filterset.form.errors)
        self.assertEqual(
            list(filterset.qs.order_by("list_rank").values_list("id", "list_rank")),
            [(230, 1), (435, 2)],
        )

    def test_filter_by_duration_range_adds_album_annotations(self):
        filterset = TestitemFilter(
            data={"duration_range_min": 100, "duration_range_max": 200},
            queryset=Testitem.objects.all(),
        )

        self.assertTrue(filterset.is_valid(), filterset.form.errors)
        self.assertEqual(
            list(filterset.qs.values_list("id", "duration", "uri")),
            [(230, 148, "spotify:album:1234567890abcdefGHIJKL")],
        )

    def test_filter_by_genre(self):
        site = Site.objects.get(pk=settings.SITE_ID)
        genre = Genre.objects.create(name="Fixture Genre", site=site)
        sub_genre = SubGenre.objects.create(name="Fixture Subgenre", genre=genre, site=site)
        Work.objects.filter(pk=230).update(sub_genre=sub_genre)

        self.assertEqual(self.ids_for_filter({"genre": "Fixture Genre"}), [230])

    def test_filter_by_orphan_subgenre(self):
        site = Site.objects.get(pk=settings.SITE_ID)
        sub_genre = SubGenre.objects.create(name="Orphan Subgenre", site=site)
        Work.objects.filter(pk=435).update(sub_genre=sub_genre)

        self.assertEqual(self.ids_for_filter({"genre": "Orphan Subgenre"}), [435])


class WorkGraphsViewTestCase(TestCase):
    fixtures = [
        'user.json',
        'testtick_company.json',
        'testtick_composer.json',
        'testtick_listen.json',
        'testtick_performance.json',
        'testtick_testitem.json',
        'testtick_venue.json',
        'testtick_work.json',
    ]

    def setUp(self):
        self.request = RequestFactory().get("/works/graphs/")
        self.request.user = CustomUser.objects.get(id=1)
        self.request.site = Site.objects.get(pk=settings.SITE_ID)
        streamed_tick = Performance.objects.create(user=self.request.user, site=self.request.site, streamed=True)
        streamed_tick.work.add(Work.objects.get(id=722))
        same_composer_performance = Performance.objects.create(user=self.request.user, site=self.request.site, streamed=False)
        same_composer_performance.work.add(Work.objects.get(id=435), Work.objects.get(id=722))

    @patch("melodramatick.work.views.plots.plot_top_lists_by_decade", return_value="top_lists_bar")
    @patch("melodramatick.work.views.plots.plot_duration_hist", return_value="duration_hist")
    @patch("melodramatick.work.views.plots.plot_listens_per_era", return_value="bottom_far_right")
    @patch("melodramatick.work.views.plots.plot_user_performances_per_era", return_value="bottom_right")
    @patch("melodramatick.work.views.plots.plot_perfs_per_era", return_value="bottom_centre")
    @patch("melodramatick.work.views.plots.plot_works_per_era", return_value="bottom_left")
    @patch("melodramatick.work.views.plots.plot_listens_per_composer", return_value="middle_far_right")
    @patch("melodramatick.work.views.plots.plot_user_performances_per_composer", return_value="middle_right")
    @patch("melodramatick.work.views.plots.plot_perfs_per_composer", return_value="middle_centre")
    @patch("melodramatick.work.views.plots.plot_works_per_composer", return_value="middle_left")
    @patch("melodramatick.work.views.plots.plot_works_by_decade", return_value="top")
    def test_get_context_data(self, *plot_mocks):
        view = WorkGraphsView()
        view.setup(self.request)
        view.object_list = Testitem.objects.all()

        context = view.get_context_data()
        decade_qs = plot_mocks[0].call_args.args[0]
        tick_composer_qs = plot_mocks[2].call_args.args[0]
        performance_composer_qs = plot_mocks[3].call_args.args[0]
        listen_composer_qs = plot_mocks[4].call_args.args[0]
        tick_era_qs = plot_mocks[6].call_args.args[0]
        performance_era_qs = plot_mocks[7].call_args.args[0]
        listen_era_qs = plot_mocks[8].call_args.args[0]
        decade_counts = {}
        for item in decade_qs.order_by("id").values("year", "user_listened", "user_ticks"):
            decade = int(item["year"] / 10) * 10
            decade_counts.setdefault(decade, {"works": 0, "listened": 0, "ticked": 0})
            decade_counts[decade]["works"] += 1
            decade_counts[decade]["listened"] += int(item["user_listened"])
            decade_counts[decade]["ticked"] += int(item["user_ticks"])

        self.assertEqual(context["top"], "top")
        self.assertEqual(context["middle_left"], "middle_left")
        self.assertEqual(context["middle_centre"], "middle_centre")
        self.assertEqual(context["middle_right"], "middle_right")
        self.assertEqual(context["middle_far_right"], "middle_far_right")
        self.assertEqual(context["bottom_left"], "bottom_left")
        self.assertEqual(context["bottom_centre"], "bottom_centre")
        self.assertEqual(context["bottom_right"], "bottom_right")
        self.assertEqual(context["bottom_far_right"], "bottom_far_right")
        self.assertEqual(context["duration_hist"], "duration_hist")
        self.assertEqual(context["top_lists_bar"], "top_lists_bar")
        self.assertEqual(context["work_count"], 3)
        self.assertEqual(context["user_performance_count"], 3)
        self.assertEqual(context["user_ticked_work_count"], 3)
        self.assertEqual(context["user_ticked_work_percentage"], 100)
        self.assertEqual(context["user_listened_work_count"], 2)
        self.assertEqual(
            decade_counts,
            {
                1800: {"works": 1, "listened": 1, "ticked": 1},
                1830: {"works": 1, "listened": 1, "ticked": 1},
                1840: {"works": 1, "listened": 0, "ticked": 1},
            },
        )
        self.assertEqual(
            list(tick_composer_qs.order_by("id").values_list("id", "user_ticks")),
            [(230, True), (435, True), (722, True)],
        )
        self.assertEqual(
            list(performance_composer_qs.order_by("id").values_list("id", "user_perfs")),
            [(230, 2), (435, 2), (722, 1)],
        )
        self.assertEqual(
            list(listen_composer_qs.order_by("id").values_list("id", "user_listens")),
            [(230, 1), (435, 2), (722, 0)],
        )
        self.assertEqual(plot_mocks[3].call_args.kwargs["user"], self.request.user)
        self.assertEqual(plot_mocks[4].call_args.kwargs["user"], self.request.user)
        self.assertEqual(
            list(tick_era_qs.order_by("id").values_list("id", "user_ticks")),
            [(230, True), (435, True), (722, True)],
        )
        self.assertEqual(
            list(performance_era_qs.order_by("id").values_list("id", "user_perfs")),
            [(230, 2), (435, 2), (722, 1)],
        )
        self.assertEqual(
            list(listen_era_qs.order_by("id").values_list("id", "user_listens")),
            [(230, 1), (435, 2), (722, 0)],
        )


class WorkGraphsPlotTestCase(TestCase):
    fixtures = [
        'user.json',
        'testtick_company.json',
        'testtick_composer.json',
        'testtick_listen.json',
        'testtick_performance.json',
        'testtick_testitem.json',
        'testtick_venue.json',
        'testtick_work.json',
    ]

    def setUp(self):
        self.user = CustomUser.objects.get(id=1)
        site = Site.objects.get(pk=settings.SITE_ID)
        streamed_tick = Performance.objects.create(user=self.user, site=site, streamed=True)
        streamed_tick.work.add(Work.objects.get(id=722))
        same_composer_performance = Performance.objects.create(user=self.user, site=site, streamed=False)
        same_composer_performance.work.add(Work.objects.get(id=435), Work.objects.get(id=722))
        self.qs = Testitem.objects.annotate(
            user_listens=Coalesce(Sum('listen__tally', filter=Q(listen__user=self.user), distinct=True), 0),
            user_ticks=Exists(
                Performance.objects.filter(
                    work=OuterRef('pk'),
                    user=self.user,
                    site_id=settings.SITE_ID,
                )
            ),
            user_perfs=Count(
                'performance',
                filter=Q(performance__user=self.user) & Q(performance__streamed=False),
                distinct=True,
            ),
        )

    @patch("melodramatick.work.plots.sns.barplot")
    def test_plot_perfs_per_composer_aggregates_user_ticks(self, barplot):
        work_plots.plot_perfs_per_composer(self.qs, figsize=(4, 6))

        self.assertEqual(barplot.call_args.kwargs["x"], ["Adam", "Beethoven"])
        self.assertEqual(barplot.call_args.kwargs["y"], [2, 1])

    @patch("melodramatick.work.plots.sns.barplot")
    def test_plot_listens_per_composer_aggregates_listen_tallies(self, barplot):
        Listen.objects.create(
            work=Work.objects.get(id=722),
            tally=2,
            user=self.user,
            site=Site.objects.get(pk=settings.SITE_ID),
        )

        work_plots.plot_listens_per_composer(self.qs, user=self.user, figsize=(4, 6))

        self.assertEqual(barplot.call_args.kwargs["x"], ["Adam", "Beethoven"])
        self.assertEqual(barplot.call_args.kwargs["y"], [4, 1])

    @patch("melodramatick.work.plots.sns.barplot")
    def test_plot_user_performances_per_composer_aggregates_live_performances(self, barplot):
        work_plots.plot_user_performances_per_composer(self.qs, user=self.user, figsize=(4, 6))

        self.assertEqual(barplot.call_args.kwargs["x"], ["Adam", "Beethoven"])
        self.assertEqual(barplot.call_args.kwargs["y"], [2, 2])

    @patch("matplotlib.axes.Axes.pie", autospec=True)
    def test_plot_perfs_per_era_uses_user_ticks(self, pie):
        work_plots.plot_perfs_per_era(self.qs, figsize=(3, 6))

        self.assertEqual(list(pie.call_args.args[1]), [1, 1, 1])

    @patch("matplotlib.axes.Axes.pie", autospec=True)
    def test_plot_user_performances_per_era_uses_live_performances(self, pie):
        work_plots.plot_user_performances_per_era(self.qs, figsize=(3, 6))

        self.assertEqual(list(pie.call_args.args[1]), [2, 2, 1])


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
