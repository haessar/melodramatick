from urllib.parse import urlparse

from django import forms

from .models import Album


class AlbumForm(forms.ModelForm):
    def save(self, commit):
        album_type, id = filter(None, urlparse(self.instance.url).path.split('/'))
        self.instance.id = id
        self.instance.uri = "spotify:{}:{}".format(album_type, id)
        return super().save(commit)

    class Meta:
        model = Album
        fields = "__all__"
