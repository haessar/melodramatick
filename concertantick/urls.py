from django.urls import path

from .views import ConcertoDetailView, ConcertoTableView
from melodramatick.work.views import WorkGraphsView


app_name = 'work'
urlpatterns = [
    path('', ConcertoTableView.as_view(), name='index'),
    path('graphs/', WorkGraphsView.as_view(), name='graphs'),
    path('<int:pk>', ConcertoDetailView.as_view(), name='work-detail'),
]
