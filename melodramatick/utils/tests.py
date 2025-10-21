from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from .randomisers import work_of_the_day
from .widgets import CustomRangeWidget
from melodramatick.accounts.models import CustomUser


class CustomRangeWidgetTestCase(TestCase):
    def setUp(self):
        self._id = "id_duration_range"
        self.widget = CustomRangeWidget(attrs={'data-range_min': 0, 'data-range_max': 360})

    def test_get_context(self):
        context = self.widget.get_context("duration_range", None, {"id": self._id})
        self.assertListEqual([sw['attrs']['id'] for sw in context['widget']['subwidgets']],
                             [self._id + "_min", self._id + "_max"])
        self.assertEqual(context['widget']['value_text'], ' - ')

    def test_get_context_with_value(self):
        context = self.widget.get_context("duration_range", [10, 100], {"id": self._id})
        self.assertEqual(context['widget']['value_text'], '10 - 100')


class RandomisersTestCase(TestCase):
    fixtures = ['album.json', 'composer.json', 'contenttypes.json', 'listen.json',
                'opera.json', 'sites.json', 'user.json', 'work.json']

    def test_work_of_the_day(self):
        anon_user = AnonymousUser()
        user1 = CustomUser.objects.get(id=1)
        user2 = CustomUser.objects.get(id=2)
        wod = work_of_the_day(anon_user)
        with self.assertRaises(AttributeError):
            wod.listen_count
        wod = work_of_the_day(user1)
        self.assertEqual(wod.listen_count, 1)
        wod = work_of_the_day(user2)
        self.assertEqual(wod.listen_count, 3)
