from django.urls import path

from melodramatick.work.views import WorkGraphsView
from .views import TestitemDetailView, TestitemTableView


app_name = 'work'
urlpatterns = [
    path('', TestitemTableView.as_view(), name='index'),
    path('graphs/', WorkGraphsView.as_view(), name='graphs'),
    path('<int:pk>', TestitemDetailView.as_view(), name='work-detail'),
]
