from unittest.mock import patch

from django.test import TestCase

from melodramatick.accounts.models import CustomUser


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
