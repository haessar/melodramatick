from operator import itemgetter

from django.db.models import Count, Max, Sum, Q
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm
from .models import CustomUser
from melodramatick.composer.models import Composer
from melodramatick.listen.models import Listen
from melodramatick.listen.plots import plot_listens_per_week
from melodramatick.performance.models import Company, Performance, Venue
from melodramatick.performance.plots import plot_perfs_per_year
from melodramatick.utils.annotation import user_listens_per_era
from melodramatick.work.models import Work


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


@method_decorator([vary_on_cookie, cache_page(60 * 1)], name='dispatch')
class ProfileView(DetailView):
    model = CustomUser
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = 'accounts/profile.html'

    def _set_awards_tab_context_data(self, context):
        context["progress"] = sorted(
            self.user.progress.filter(count__gt=0).filter(list__site=self.request.site),
            key=lambda x: x.ticks_to_next_award)
        context["awards"] = sorted(
            self.user.award.filter(list__site=self.request.site),
            key=lambda x: (x.level.rank, -x.list.length))

    def _set_performances_tab_context_data(self, context):
        context["performances"] = Performance.objects.filter(user=self.user).order_by('-date')
        context["most_watched"] = Work.objects.annotate(
            tally=Count("performance", filter=Q(
                performance__user=self.user,
                performance__site=self.request.site))
            ).order_by("-tally").first()
        context["most_visited"] = Venue.objects.annotate(
            tally=Count("performance", filter=Q(
                performance__user=self.user,
                performance__streamed=False,
                performance__site=self.request.site))
            ).order_by("-tally").first()
        context["most_watched_company"] = Company.objects.annotate(
            tally=Count("performance", filter=Q(
                performance__user=self.user,
                performance__site=self.request.site))
            ).order_by("-tally").first()
        context["most_watched_composer"] = Composer.objects.annotate(
            tally=Count("work__performance", filter=Q(
                work__performance__user=self.user,
                work__performance__site=self.request.site))
            ).order_by("-tally").first()
        context["perfs_per_year"] = plot_perfs_per_year(context["performances"], figsize=(6, 6))

    def _set_listens_tab_context_data(self, context):
        context["listens"] = Listen.objects.filter(user=self.user)
        max_tally = context["listens"].aggregate(Max("tally"))["tally__max"]
        context["most_listened"] = context["listens"].filter(tally=max_tally).first()
        context["most_listened_composer"] = Composer.objects.annotate(
            tally=Sum("work__listen__tally", filter=Q(
                work__listen__user=self.user,
                work__listen__site=self.request.site))
            ).order_by("-tally").first()
        try:
            context["most_listened_era"] = max(
                user_listens_per_era(Work.objects.all(), self.user),
                key=itemgetter(1)
            )
        except ValueError:
            pass
        context["listens_per_week"] = plot_listens_per_week(context["listens"], figsize=(6, 6))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.user = self.get_object()
        self._set_awards_tab_context_data(context)
        self._set_performances_tab_context_data(context)
        self._set_listens_tab_context_data(context)
        return context
