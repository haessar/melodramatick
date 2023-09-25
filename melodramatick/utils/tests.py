from django.test import TestCase

from .widgets import CustomRangeWidget


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
