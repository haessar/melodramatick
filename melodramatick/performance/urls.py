from django.urls import path

from .views import tick_view

app_name = 'performance'
urlpatterns = [
    path("tick/<work>/", tick_view, name="tick"),
]
