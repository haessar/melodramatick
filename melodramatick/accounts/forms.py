from django.contrib.auth.models import Permission
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.contenttypes.models import ContentType

from .models import CustomUser
from melodramatick.performance.models import Performance


class CustomUserCreationForm(UserCreationForm):

    def save(self, commit=True):
        user = super().save(commit)
        content_type = ContentType.objects.get_for_model(Performance)
        change_permission = Permission.objects.get(codename="change_performance", content_type=content_type)
        view_permission = Permission.objects.get(codename="view_performance", content_type=content_type)
        user.user_permissions.add(change_permission)
        user.user_permissions.add(view_permission)
        if commit:
            user.save()
        return user

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')
