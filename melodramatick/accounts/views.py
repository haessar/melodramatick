from django.db.models import Max
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm
from .models import CustomUser
from melodramatick.listen.models import Listen


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
        context["progress"] = sorted(
            user.progress.filter(count__gt=0).filter(list__site=self.request.site),
            key=lambda x: x.ticks_to_next_award)
        context["awards"] = sorted(
            user.award.filter(list__site=self.request.site),
            key=lambda x: (x.level.rank, -x.list.length))
        context["listens"] = Listen.objects.filter(user=user)
        max_tally = context["listens"].aggregate(Max("tally"))["tally__max"]
        context["most_listened"] = context["listens"].filter(tally=max_tally).first()
        return context
