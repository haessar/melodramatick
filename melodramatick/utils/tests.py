from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
import responses

from .quotel_api import populate_composer_quotes
from .randomisers import work_of_the_day
from .spotify_api import (auth_manager,
                          get_playlist_image, get_playlist_duration,
                          get_album_image, get_album_duration,
                          get_track_image, get_track_duration)
from .widgets import CustomRangeWidget
from melodramatick.accounts.models import CustomUser
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


@patch("melodramatick.utils.spotify_api.SpotifyOAuth")
@patch("melodramatick.utils.spotify_api.SpotifyClientCredentials")
@patch("spotipy.Spotify")
class SpotifyAPITestCase(TestCase):
    def setUp(self):
        self.image_url = "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228"
        self.image_response = {
            "images": [{
                "url": self.image_url,
                "height": 300,
                "width": 300
            }]
        }
        self.playlist_id = "01B72NX2L24VGRbO3bmHXm"
        self.playlist_uri = "spotify:playlist:" + self.playlist_id
        self.album_id = "0KWQDuT2B9dYb7DsUCwSj3"
        self.album_uri = "spotify:album:" + self.album_id
        self.track_uri = "spotify:track:2DhSQuGqHwxtrxuYfUuHRi"

    def test_auth_manager(self, sp, cc, oa):
        auth_manager()
        sp.assert_called_with(auth_manager=cc())
        auth_manager(scope="playlist-read-private")
        sp.assert_called_with(auth_manager=oa())

    def test_get_playlist_image(self, sp, *args):
        sp().playlist.return_value = self.image_response
        self.assertEqual(get_playlist_image(self.playlist_uri), self.image_url)

    def test_get_playlist_duration(self, sp, *args):
        sp().playlist_tracks.return_value = {
            "items": [
                {"track": {"duration_ms": 300000}},
                {"track": {"duration_ms": 600000}}
            ]
        }
        self.assertEqual(get_playlist_duration(self.playlist_id), "15")

    def test_get_album_image(self, sp, *args):
        sp().album.return_value = self.image_response
        self.assertEqual(get_album_image(self.album_uri), self.image_url)

    def test_get_abum_duration(self, sp, *args):
        sp().album_tracks.side_effect = [
            {"items": [
                {"duration_ms": 300000},
                {"duration_ms": 600000}
            ]},
            {"items": []}
        ]
        self.assertEqual(get_album_duration(self.album_id), "15")

    def test_get_track(self, sp, *args):
        sp().track.return_value = {
            "album": self.image_response,
            "duration_ms": 300000
        }
        self.assertEqual(get_track_image(self.track_uri), self.image_url)
        self.assertEqual(get_track_duration(self.track_uri), "5")


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
