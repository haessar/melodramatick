from collections import Counter, OrderedDict

from django.conf import settings
from matplotlib.ticker import MultipleLocator
import pandas as pd

from melodramatick.utils.plots import to_bytes_fig


@to_bytes_fig
def plot_perfs_per_year(ax, qs):
    qs = qs.exclude(date__isnull=True).exclude(date__exact='')
    if "sqlite3" in settings.DATABASES['default']['ENGINE']:
        years = qs.extra(select={'year': "strftime('%%Y', date)"}).values('year')
    else:
        years = qs.extra(select={'year': "DATE_FORMAT(date, '%%Y')"}).values('year')
    perfs_by_year = OrderedDict(sorted(Counter(y['year'] for y in years.filter(streamed=False)).items()))
    streams_by_year = OrderedDict(sorted(Counter(y['year'] for y in years.filter(streamed=True)).items()))
    all_years = [y['year'] for y in years.distinct().order_by('year')]
    df = pd.DataFrame(columns=all_years, data=[perfs_by_year, streams_by_year], index=['Live', 'Streamed'])

    df.T.plot.bar(stacked=True, ax=ax, color=[settings.BACKGROUND_COLOUR, settings.STREAMED_COLOUR], rot=0)

    ax.set_title('Performances per year')
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.grid(b=True, which='major', color='black', linestyle='-')
    ax.yaxis.grid(b=True, which='minor', linestyle='--')
    ax.set_ylabel("Count")
    ax.set_xlabel("Year")
