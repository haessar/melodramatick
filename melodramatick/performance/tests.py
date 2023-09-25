from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.test import TestCase

from .admin import PerformanceAdmin
from .models import Performance
from .views import tick_view
from melodramatick.accounts.models import CustomUser
from melodramatick.work.models import Work


class PerformanceAdminTestCase(TestCase):
    fixtures = ['user.json', 'sites.json', 'company.json', 'performance.json', 'venue.json', 'composer.json', 'work.json']

    def setUp(self):
        self.performance_admin = PerformanceAdmin(model=Performance, admin_site=AdminSite())
        self.request = self.client.get("/").wsgi_request
        self.request.user = CustomUser.objects.get(id=1)

    def test_get_queryset(self):
        qs = self.performance_admin.get_queryset(self.request)
        # Superuser sees all performances
        self.assertQuerysetEqual(qs, Performance.objects.all().order_by('-date'))
        self.request.user = CustomUser.objects.get(id=2)
        qs = self.performance_admin.get_queryset(self.request)
        # Regular user only sees their own performances
        self.assertQuerysetEqual(qs, Performance.objects.filter(user=2).order_by('-date'))

    def test_merge_performances(self):
        total_performance_count = len(Performance.objects.all())
        qs = Performance.objects.filter(id__in=[1, 4])
        self.performance_admin.merge_performances(self.request, qs)
        # Fail to merge due to multiple users
        self.assertIn("multiple users", str(list(get_messages(self.request))[-1]))
        qs = Performance.objects.filter(id__in=[1, 2])
        works = list(Work.objects.filter(id__in=qs.values('work')))
        self.performance_admin.merge_performances(self.request, qs)
        # Successful merged performance with both works from two individual performances.
        self.assertQuerysetEqual(Performance.objects.last().work.all(), works)
        # Should be one less total performance (2 merging becomes 1)
        self.assertEqual(len(Performance.objects.all()), total_performance_count - 1)

    def test_split_performance_multiple_objects(self):
        qs = Performance.objects.filter(id__in=[1, 2])
        self.performance_admin.split_performance(self.request, qs)
        # Fail to split due to multiple performances in queryset
        self.assertIn("more than one", str(list(get_messages(self.request))[-1]))

    def test_split_performance_single_work(self):
        qs = Performance.objects.filter(id=1)
        self.performance_admin.split_performance(self.request, qs)
        # Fail to split due to performance only being single work
        self.assertIn("single work", str(list(get_messages(self.request))[-1]))

    def test_split_performance_success(self):
        total_performance_count = len(Performance.objects.all())
        qs = Performance.objects.filter(id=3)
        works = list(Work.objects.filter(id__in=qs.values('work')))
        self.performance_admin.split_performance(self.request, qs)
        # Should be one more total performance (1 splitting becomes 2)
        self.assertEqual(len(Performance.objects.all()), total_performance_count + 1)
        with self.assertRaises(Performance.DoesNotExist):
            qs.get()
        new_performances = Performance.objects.all().order_by('-id')[:2]
        # Original works should appear across the two new performances
        self.assertQuerysetEqual(Work.objects.filter(id__in=new_performances.values('work')), works)


class TickViewTestCase(TestCase):
    fixtures = ['composer.json', 'sites.json', 'user.json', 'work.json']

    def setUp(self):
        self.request = self.client.get("/").wsgi_request
        self.request.META['HTTP_REFERER'] = "/"
        self.request.user = CustomUser.objects.get(id=1)

    def test_tick_view(self):
        work_id = 230 if self.request.site.id == 1 else 722
        tick_view(self.request, work=work_id)
        qs = Performance.objects.all()
        # Only 1 performance object should be created...
        self.assertEqual(len(qs), 1)
        performance = qs.first()
        self.assertQuerysetEqual(performance.work.all(), Work.objects.filter(id=work_id))
        self.assertEqual(performance.user, self.request.user)
        tick_view(self.request, work=work_id)
        qs = Performance.objects.all()
        # ...and then deleted.
        self.assertEqual(len(qs), 0)
