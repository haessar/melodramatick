from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse

from .forms import CustomUserCreationForm
from .models import CustomUser


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
            self.assertEqual(self.response.context_data['most_listened_composer'].tally, 2)
            self.assertEqual(len(self.response.context_data['performances']), 3)
            self.assertEqual(self.response.context_data['most_watched'].tally, 2)
            self.assertEqual(self.response.context_data['most_watched_composer'].tally, 2)
            self.assertEqual(self.response.context_data['most_visited'].tally, 2)
            self.assertEqual(self.response.context_data['most_watched_company'].tally, 3)
        elif self.response.wsgi_request.site.id == 2:
            self.assertEqual(self.response.context_data['most_listened'].tally, 3)
            self.assertEqual(len(self.response.context_data['listens']), 1)
        self.assertTemplateUsed(self.response, 'accounts/profile.html')


class SignUpViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_custom_user_creation_form(self):
        user = CustomUser.objects.all()[0]
        self.assertEqual(user.user_permissions.count(), 0)
        request = HttpRequest()
        request.POST = {
            "username": "testuser",
            "password1": user.password,
            "password2": user.password,
        }
        form = CustomUserCreationForm(request.POST)
        testuser = form.save()
        self.assertEqual(testuser.user_permissions.count(), 2)
