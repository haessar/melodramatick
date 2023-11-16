from django.db.models import Count, Max, Q
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm
from .models import CustomUser
from melodramatick.listen.models import Listen
from melodramatick.performance.models import Performance, Venue
from melodramatick.performance.plots import plot_perfs_per_year
from melodramatick.work.models import Work


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
        context["performances"] = Performance.objects.filter(user=user).order_by('-date')
        max_tally = context["listens"].aggregate(Max("tally"))["tally__max"]
        context["most_listened"] = context["listens"].filter(tally=max_tally).first()
        works_with_counts = Work.objects.filter(performance__in=context['performances']).annotate(Count('performance'))
        context["most_watched"] = works_with_counts.order_by('-performance__count').first()
        venues = Venue.objects.annotate(venue_tally=Count("performance", filter=Q(performance__user=user)))
        context["most_visited"] = venues.order_by('-venue_tally').first()
        context["perfs_per_year"] = plot_perfs_per_year(context["performances"], figsize=(6, 6))
        return context
