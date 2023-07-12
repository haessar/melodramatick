from django import forms

from .models import Album


class AlbumForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['uri'].initial = "spotify:album:"

    class Meta:
        model = Album
        fields = ('duration', 'id', 'uri', 'image_url')
