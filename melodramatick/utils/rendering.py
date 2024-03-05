from django.templatetags.static import static
from django.utils.html import format_html

from melodramatick.performance.models import Performance


def render_playback_button(value):
    return format_html('<img uri="{}:play" src="{}" width="24px;"/>', value, static("images/Spotify-Play-Button.png"))


def render_tickbox(user, work, scale=1):
    performances = Performance.objects.filter(user=user)
    if performances.filter(work=work):
        ticked = True
        tickbox_img, width = "images/ticked.png", str(scale * 28) + "px"
    else:
        ticked = False
        tickbox_img, width = "images/unticked.png", str(scale * 24) + "px"
    return ticked, format_html('<img src="{}" width="{};"/>', static(tickbox_img), width)
