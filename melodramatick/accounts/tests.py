from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse

from .forms import CustomUserCreationForm
from .models import CustomUser


class ProfileViewTestCase(TestCase):
    fixtures = ['user.json', 'testtick_listen.json', 'testtick_work.json', 'testtick_testitem.json',
                'testtick_composer.json', 'testtick_performance.json', 'testtick_venue.json',
                'testtick_company.json']

    def setUp(self):
        self.client.force_login(CustomUser.objects.get(id=1))
        self.response = self.client.get(reverse('profile', kwargs={'username': 'user1'}))

    def test_get_context_data(self):
        # TODO Add tests for context["progress"] and context["awards"]
        self.assertEqual(len(self.response.context_data['listens']), 2)
        self.assertEqual(self.response.context_data['most_listened'].tally, 2)
        self.assertEqual(self.response.context_data['most_listened_composer'].tally, 2)
        self.assertEqual(len(self.response.context_data['performances']), 3)
        self.assertEqual(self.response.context_data['most_watched'].tally, 2)
        self.assertEqual(self.response.context_data['most_watched_composer'].tally, 2)
        self.assertEqual(self.response.context_data['most_visited'].tally, 2)
        self.assertEqual(self.response.context_data['most_watched_company'].tally, 3)
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
