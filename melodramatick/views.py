from django.views.generic.base import TemplateView

from melodramatick.utils.quotel_api import quote_of_the_day


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["qod"] = quote_of_the_day()
        return context
