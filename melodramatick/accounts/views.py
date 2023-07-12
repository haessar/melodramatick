from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm
from .models import CustomUser


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ProfileView(DetailView):
    model = CustomUser
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context["progress"] = sorted(user.progress.filter(count__gt=0), key=lambda x: x.ticks_to_next_award)
        context["awards"] = sorted(user.award.all(), key=lambda x: (x.level.rank, -x.list.length))
        return context
