from django.urls import path

from . import views

app_name = 'composer'
urlpatterns = [
    path('', views.ComposerListView.as_view(), name='index'),
    path('composer-autocomplete/', views.ComposerAutocomplete.as_view(), name="composer-autocomplete"),
]
