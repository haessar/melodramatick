from django.urls import path

from .views import spotify_playback_view

app_name = 'listen'
urlpatterns = [
    path("play/<opera>/", spotify_playback_view, name="playback"),
]
