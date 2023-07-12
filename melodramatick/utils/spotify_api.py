from django.conf import settings
import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


def auth_manager(scope=None):
    if not scope:
        auth_manager = SpotifyClientCredentials(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
        )
    else:
        auth_manager = SpotifyOAuth(
            scope=scope,
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri="http://localhost:8000",
            show_dialog=False,
            cache_handler=CacheFileHandler(".cache")
        )
    return spotipy.Spotify(auth_manager=auth_manager)


def get_playlist_image(playlist_uri):
    scope = "playlist-read-private playlist-read-collaborative"
    sp = auth_manager(scope)
    pl = sp.playlist(playlist_uri)
    return pl['images'][0]['url']


def get_playlist_duration(playlist_id):
    scope = "playlist-read-private playlist-read-collaborative"
    sp = auth_manager(scope)
    track_durations = sp.playlist_tracks(playlist_id, fields=['items.track.duration_ms'])
    total_ms = sum(d['track']['duration_ms'] for d in track_durations['items'])
    return str(int(total_ms/(1000*60)))


def get_album_image(album_uri):
    sp = auth_manager()
    al = sp.album(album_uri)
    return al['images'][0]['url']


def get_album_duration(album_id):
    sp = auth_manager()
    offset = 0
    increment = 50
    items = []
    while True:
        response = sp.album_tracks(album_id, limit=50, offset=offset)
        if response['items']:
            items.extend(response['items'])
            offset += increment
        else:
            break
    total_ms = sum(track['duration_ms'] for track in items)
    return str(int(total_ms/(1000*60)))
