from django.urls import path

from . import views

app_name = 'top_list'
urlpatterns = [
    path('', views.TopListView.as_view(), name='index'),
]
