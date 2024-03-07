from unittest.mock import patch

from django.test import TestCase
import responses

from .quotel_api import populate_composer_quotes
from .widgets import CustomRangeWidget
from melodramatick.composer.models import Quote


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


@patch("melodramatick.utils.quotel_api.COMPOSER_AUTHOR_ID", {"Adam": 10000, "Beethoven": 22212})
class QuotelAPITestCase(TestCase):
    fixtures = ["composer.json", "sites.json", "quote.json"]

    @responses.activate
    def test_populate_composer_quotes(self):
        responses.add(responses.POST, "https://quotel-quotes.p.rapidapi.com/quotes",
                      json=[{"quoteId": "100", "quote": "This is a quote by Adam."}])
        self.assertEqual(Quote.objects.count(), 1)
        populate_composer_quotes()
        self.assertEqual(Quote.objects.count(), 2)
