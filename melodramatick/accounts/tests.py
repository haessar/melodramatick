from django.test import TestCase
from django.urls import reverse


class ProfileViewTestCase(TestCase):
    fixtures = ['contenttypes.json', 'user.json', 'listen.json', 'work.json', 'opera.json', 'composer.json', 'sites.json',
                'performance.json', 'venue.json', 'company.json']

    def setUp(self):
        self.response = self.client.get(reverse('profile', kwargs={'username': 'user1'}))

    def test_get_context_data(self):
        # TODO Add tests for context["progress"] and context["awards"]
        if self.response.wsgi_request.site.id == 1:
            self.assertEqual(len(self.response.context_data['listens']), 2)
            self.assertEqual(self.response.context_data['most_listened'].tally, 2)
            self.assertEqual(len(self.response.context_data['performances']), 3)
            self.assertEqual(self.response.context_data['most_watched'].tally, 2)
            self.assertEqual(self.response.context_data['most_visited'].tally, 2)
            self.assertEqual(self.response.context_data['most_watched_company'].tally, 3)
        elif self.response.wsgi_request.site.id == 2:
            self.assertEqual(self.response.context_data['most_listened'].tally, 3)
            self.assertEqual(len(self.response.context_data['listens']), 1)
        self.assertTemplateUsed(self.response, 'accounts/profile.html')
