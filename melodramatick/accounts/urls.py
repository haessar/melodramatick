from django.contrib.auth import views as auth_views
from django.urls import path
from .views import SignUpView, ProfileView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path("<slug:username>", ProfileView.as_view(), name='profile'),
]
