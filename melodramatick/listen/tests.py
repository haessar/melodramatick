from django.test import TestCase

from .models import Listen
from .views import spotify_playback_view
from melodramatick.accounts.models import CustomUser
from melodramatick.work.models import Work


class SpotifyPlaybackViewTestCase(TestCase):
    fixtures = ["composer.json", "sites.json", "user.json", "work.json"]

    def setUp(self):
        response = self.client.get("/")
        self.request = response.wsgi_request
        self.request.META['HTTP_REFERER'] = "/"
        self.request.user = CustomUser.objects.get(id=1)

    def test_spotify_playback_view(self):
        work_id = 230 if self.request.site.id == 1 else 722
        spotify_playback_view(self.request, work=work_id)
        spotify_playback_view(self.request, work=work_id)
        qs = Listen.objects.all()
        # Only 1 listen object should be created...
        self.assertEqual(len(qs), 1)
        listen = qs.first()
        # ...with tally of 2
        self.assertEqual(listen.tally, 2)
        self.assertEqual(listen.user, self.request.user)
        work = Work.objects.get(id=work_id)
        self.assertEqual(listen.work, work)
