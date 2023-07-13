from django.urls import reverse
from django.utils.html import format_html
import django_tables2 as tables

from .models import List


class TopListTable(tables.Table):
    length = tables.Column(accessor="list_work_count")
    url = tables.Column(accessor="url", verbose_name="URL", orderable=False)

    class Meta:
        model = List
        template_name = 'django_tables2/bootstrap4.html'
        exclude = ['id']
        sequence = ('publication', 'name', 'year', 'author', 'length', 'url')

    def render_name(self, record):
        return format_html('<a href={}?top_list={}>{}</a>', reverse('work:index'), record.id, record.name)

    def render_url(self, record):
        return format_html('<a href={} target="_blank">Link</a>', record.url)
