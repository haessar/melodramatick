from datetime import datetime, timedelta

from django.conf import settings
from matplotlib.ticker import MultipleLocator
import pandas as pd

from melodramatick.utils.plots import EmptyFigure, to_bytes_fig


@to_bytes_fig
def plot_listens_per_month(ax, qs):
    qs = qs.exclude(updated_at__isnull=True).exclude(updated_at__lte=datetime.now()-timedelta(weeks=52))
    if qs:
        if "sqlite3" in settings.DATABASES['default']['ENGINE']:
            months = qs.extra(select={'month': "strftime('%%m', updated_at)"}).values('month', 'tally')
        else:
            months = qs.extra(select={'month': "DATE_FORMAT(updated_at, '%%m')"}).values('month', 'tally')
        df = pd.DataFrame(months).groupby('month').sum()

        df.plot.bar(ax=ax, color=settings.BACKGROUND_COLOUR, rot=45)

        ax.set_title('Listens per month')
        ax.yaxis.set_minor_locator(MultipleLocator(1))
        ax.yaxis.grid(b=True, which='major', color='black', linestyle='-')
        ax.yaxis.grid(b=True, which='minor', linestyle='--')
        ax.set_ylabel("Tally")
        ax.set_xlabel("Month")
        ax.get_legend().remove()
    else:
        raise EmptyFigure
