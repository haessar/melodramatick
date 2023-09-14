from django.urls import path
from django.views.decorators.cache import cache_page
from melodramatick.work.views import WorkGraphsView

from .views import OperaDetailView, OperaTableView


app_name = 'work'
urlpatterns = [
    path('', OperaTableView.as_view(), name='index'),
    path("graphs/", cache_page(60 * 60)(WorkGraphsView.as_view()), name='graphs'),
    path("<int:pk>", OperaDetailView.as_view(), name='work-detail'),
]
