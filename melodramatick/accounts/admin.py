from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email']
    fieldsets = UserAdmin.fieldsets + (
        (_('Playback'), {'fields': ('spotify_player',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
