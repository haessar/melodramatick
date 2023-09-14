from django.urls import path
from django.views.decorators.cache import cache_page

from .views import BalletDetailView, BalletTableView
from melodramatick.work.views import WorkGraphsView


app_name = 'work'
urlpatterns = [
    path('', BalletTableView.as_view(), name='index'),
    path("graphs/", cache_page(60 * 60)(WorkGraphsView.as_view()), name='graphs'),
    path("<int:pk>", BalletDetailView.as_view(), name='work-detail'),
]
