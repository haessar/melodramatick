from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import django_tables2 as tables

from melodramatick.performance.models import Performance
from melodramatick.utils.rendering import render_playback_button, render_tickbox


def playback_column(verbose_name):
    return tables.Column(
        linkify=("listen:playback", {'work': tables.A("id")}),
        attrs={'a': {"class": "spotify_play"}},
        verbose_name=verbose_name,
        orderable=False
    )


class WorkTable(tables.Table):
    position = tables.Column(accessor="list_rank", verbose_name="Rank", empty_values=())
    title = tables.Column(accessor="title")
    composer = tables.Column(accessor="composer")
    year = tables.Column(accessor="year", order_by="year")
    sub_genre = tables.Column(accessor="sub_genre")
    notes = tables.Column(accessor="notes")
    total_lists = tables.Column(accessor="total_lists", verbose_name="Top Lists", order_by="-total_lists")
    user_listens = tables.Column(accessor="user_listens", verbose_name="Listens", order_by="-user_listens")
    random_uri = playback_column("Play random")
    uri = playback_column("Play")
    duration = tables.Column(accessor="duration", verbose_name="Duration", empty_values=())
    user_performances = tables.Column(accessor="user_performances", verbose_name="Performances", order_by="-user_performances")
    tickbox = tables.Column(linkify=("performance:tick", {'work': tables.A("id")}),
                            empty_values=(), orderable=False, verbose_name=settings.SITE)
    performance_list = tables.Column(accessor="performance")

    def render_composer(self, record):
        return record.composer.surname

    def render_title(self, value, record):
        return format_html('<a href={}>{}</a>', reverse('work:work-detail', args=(record.id,)), value)

    def render_performance_list(self, value):
        performances = value.filter(user=self.request.user)
        log = ""
        for p in performances.order_by('date'):
            log += '<p class="expanded{}"><a href={}>'.format(" streamed" if p.streamed else "",
                                                              reverse('user-admin:performance_performance_change',
                                                                      args=(p.id,)))
            log += p.date.date.strftime('%Y') + "\t-\t" if p.date else ""
            if any((p.company, p.venue, p.notes)):
                log += "\t-\t".join(filter(None, (str(p.company), str(p.venue), p.notes)))
                if p.streamed:
                    log += " (streamed)"
            else:
                log += "No performance info"
            log += "</a></p>"
        return mark_safe(log)

    def render_random_uri(self, record):
        return render_playback_button(record.random_uri)

    def render_uri(self, record):
        return render_playback_button(record.uri)

    def render_tickbox(self, record):
        _, tickbox = render_tickbox(self.request.user, record)
        return tickbox

    def render_user_listens(self, record):
        return record.user_listens if record.user_listens else "—"

    def render_user_performances(self, record):
        return record.user_performances if record.user_performances else "—"

    class Meta:
        def assign_row_id(**kwargs):
            """
            Assign 'ticked' id to row if performance has been logged.
            """
            id = "ticked"
            record = kwargs.get('record', None)
            user = kwargs['table'].request.user
            performances = Performance.objects.filter(user=user)
            if record:
                filt = performances.filter(work=record)
                if filt:
                    return (id + "-stream-only" if all(p.streamed for p in filt) else id)
            return ""
        template_name = "work/table.html"
        exclude = ['id']
        row_attrs = {
            "id": assign_row_id,
        }
