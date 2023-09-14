"""melodramatick URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
import notifications.urls

from .admin import user_admin
from .views import HomePageView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('accounts/', include('melodramatick.accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/clearcache/', include('clearcache.urls')),
    path('admin/', admin.site.urls),
    path('adminactions/', include('adminactions.urls')),
    path('user-admin/', user_admin.urls),
    path('composers/', include('melodramatick.composer.urls')),
    path('top-lists/', include('melodramatick.top_list.urls')),
    path('performances/', include('melodramatick.performance.urls')),
    path('', include('melodramatick.listen.urls')),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
]

if settings.DEVELOPMENT_MODE is True:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))

if settings.SITE_ID == 1:
    urlpatterns.append(path('works/', include('operatick.urls')))
elif settings.SITE_ID == 2:
    urlpatterns.append(path('works/', include('balletick.urls')))
