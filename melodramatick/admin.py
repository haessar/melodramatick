import adminactions.actions as actions
from django.conf import settings

from django.contrib import admin
from django.contrib.admin.forms import AuthenticationForm

from melodramatick.performance.admin import PerformanceAdmin
from melodramatick.performance.models import Performance


class UserAdminSite(admin.AdminSite):
    """
    Admin site specifically for non-superusers.
    """

    login_form = AuthenticationForm
    site_header = '{} Administration'.format(settings.SITE)
    site_title = settings.SITE

    def has_permission(self, request):
        """
        Checks if the current user has access.
        """
        return request.user.is_active


user_admin = UserAdminSite(name='user-admin')
user_admin.register(Performance, PerformanceAdmin)

admin.site.site_header = '{} Administration - Root'.format(settings.SITE)
admin.site.site_title = settings.SITE

# register all adminactions
actions.add_to_site(admin.site)
