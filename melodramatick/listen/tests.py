from unittest.mock import patch

from django.test import TestCase

from .models import Album, Listen
from .views import spotify_playback_view
from melodramatick.accounts.models import CustomUser
from melodramatick.work.models import Work


class SpotifyPlaybackViewTestCase(TestCase):
    fixtures = ["testtick_composer.json", "user.json", "testtick_work.json", "testtick_testitem.json"]

    def setUp(self):
        response = self.client.get("/")
        self.request = response.wsgi_request
        self.request.META['HTTP_REFERER'] = "/"
        self.request.user = CustomUser.objects.get(id=1)

    def test_spotify_playback_view(self):
        work_id = 230
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


class ListenModelTestCase(TestCase):
    fixtures = ["testtick_composer.json", "user.json", "testtick_work.json", "testtick_testitem.json"]

    def test_str(self):
        listen = Listen.objects.create(
            work=Work.objects.get(id=230),
            user=CustomUser.objects.get(id=1),
            site_id=4,
        )

        self.assertEqual(str(listen), "user1")


class AlbumModelTestCase(TestCase):
    fixtures = ["testtick_album.json", "testtick_composer.json", "testtick_work.json", "testtick_testitem.json"]

    def test_image_returns_image_url(self):
        album = Album.objects.get(id="1234567890abcdefGHIJKL")

        self.assertEqual(album.image, "https://example.com/")

    def test_image_returns_none_without_image_url(self):
        album = Album(image_url=None)

        self.assertIsNone(album.image)

    def test_delete_uses_url_when_inline_form_has_no_id(self):
        existing = Album.objects.get(id="1234567890abcdefGHIJKL")
        existing.url = "https://example.com/album"
        existing.save()
        inline_album = Album(url=existing.url)

        inline_album.delete()

        self.assertFalse(Album.objects.filter(id="1234567890abcdefGHIJKL").exists())

    def test_delete_uses_uri_when_inline_form_has_no_id_or_url(self):
        existing = Album.objects.get(id="1234567890abcdefGHIJKL")
        inline_album = Album(uri=existing.uri)

        inline_album.delete()

        self.assertFalse(Album.objects.filter(id="1234567890abcdefGHIJKL").exists())

    @patch("melodramatick.listen.models.get_album_duration", return_value="120")
    @patch("melodramatick.listen.models.get_album_image", return_value="https://example.com/album.jpg")
    def test_album_uri_sets_image_and_duration(self, get_album_image, get_album_duration):
        Album.objects.create(
            id="aaaaaaaaaaaaaaaaaaaaaa",
            work=Work.objects.get(id=230),
            uri="spotify:album:aaaaaaaaaaaaaaaaaaaaaa",
        )

        album = Album.objects.get(id="aaaaaaaaaaaaaaaaaaaaaa")
        self.assertEqual(album.image_url, "https://example.com/album.jpg")
        self.assertEqual(album.duration, 120)
        get_album_image.assert_called_once_with("spotify:album:aaaaaaaaaaaaaaaaaaaaaa")
        get_album_duration.assert_called_once_with("spotify:album:aaaaaaaaaaaaaaaaaaaaaa")

    @patch("melodramatick.listen.models.get_track_duration", return_value="5")
    @patch("melodramatick.listen.models.get_track_image", return_value="https://example.com/track.jpg")
    def test_track_uri_sets_image_and_duration(self, get_track_image, get_track_duration):
        Album.objects.create(
            id="bbbbbbbbbbbbbbbbbbbbbb",
            work=Work.objects.get(id=230),
            uri="spotify:track:bbbbbbbbbbbbbbbbbbbbbb",
        )

        album = Album.objects.get(id="bbbbbbbbbbbbbbbbbbbbbb")
        self.assertEqual(album.image_url, "https://example.com/track.jpg")
        self.assertEqual(album.duration, 5)
        get_track_image.assert_called_once_with("spotify:track:bbbbbbbbbbbbbbbbbbbbbb")
        get_track_duration.assert_called_once_with("spotify:track:bbbbbbbbbbbbbbbbbbbbbb")

    @patch("melodramatick.listen.models.get_playlist_duration", return_value="60")
    @patch("melodramatick.listen.models.get_playlist_image", return_value="https://example.com/playlist.jpg")
    def test_playlist_uri_sets_image_and_duration(self, get_playlist_image, get_playlist_duration):
        Album.objects.create(
            id="cccccccccccccccccccccc",
            work=Work.objects.get(id=230),
            uri="spotify:playlist:cccccccccccccccccccccc",
        )

        album = Album.objects.get(id="cccccccccccccccccccccc")
        self.assertEqual(album.image_url, "https://example.com/playlist.jpg")
        self.assertEqual(album.duration, 60)
        get_playlist_image.assert_called_once_with("spotify:playlist:cccccccccccccccccccccc")
        get_playlist_duration.assert_called_once_with("spotify:playlist:cccccccccccccccccccccc")

    @patch("melodramatick.listen.models.get_album_duration")
    @patch("melodramatick.listen.models.get_album_image")
    def test_existing_image_and_duration_are_not_replaced(self, get_album_image, get_album_duration):
        Album.objects.create(
            id="dddddddddddddddddddddd",
            work=Work.objects.get(id=230),
            uri="spotify:album:dddddddddddddddddddddd",
            image_url="https://example.com/existing.jpg",
            duration=45,
        )

        album = Album.objects.get(id="dddddddddddddddddddddd")
        self.assertEqual(album.image_url, "https://example.com/existing.jpg")
        self.assertEqual(album.duration, 45)
        get_album_image.assert_not_called()
        get_album_duration.assert_not_called()

    @patch("melodramatick.listen.models.get_album_duration", return_value=None)
    @patch("melodramatick.listen.models.get_album_image", return_value=None)
    def test_empty_api_responses_do_not_update_fields(self, get_album_image, get_album_duration):
        Album.objects.create(
            id="eeeeeeeeeeeeeeeeeeeeee",
            work=Work.objects.get(id=230),
            uri="spotify:album:eeeeeeeeeeeeeeeeeeeeee",
        )

        album = Album.objects.get(id="eeeeeeeeeeeeeeeeeeeeee")
        self.assertIsNone(album.image_url)
        self.assertEqual(album.duration, 0)
