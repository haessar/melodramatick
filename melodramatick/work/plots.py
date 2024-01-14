from collections import Counter

import itertools

from django.conf import settings
from django.db.models import Avg, Count
import matplotlib
from matplotlib.ticker import MultipleLocator
import numpy as np
import seaborn as sns

from melodramatick.utils.plots import to_bytes_fig

matplotlib.use('Agg')

ERAS_CMAP = dict(zip([v for _, v in settings.ERAS_MAP], sns.color_palette("rocket", len(settings.ERAS_MAP))))
ERAS_ORDER = {v: idx for idx, (_, v) in enumerate(settings.ERAS_MAP)}


def era_from_years(yr_list):
    eras = []
    for yr in yr_list:
        for yr_rng, era in settings.ERAS_MAP:
            start, end = map(int, yr_rng.split("-"))
            if round(yr) in range(start, end + 1):
                eras.append(era)
                break
    return eras


@to_bytes_fig
def plot_works_by_decade(ax, qs):
    by_decades = (
        qs
        .extra(select={'year': 'FLOOR(year/10)*10'})
        .values('year', 'user_listens', 'user_perfs')
        .annotate(dcount=Count('year'))
        .order_by()
    )

    decades = [int(x['year']) for x in by_decades]
    counts = [x['dcount'] for x in by_decades]
    listens = [x['user_listens'] for x in by_decades]
    perfs = [x['user_perfs'] for x in by_decades]

    label = settings.WORK_PLURAL_LABEL.title()
    ax.bar(decades, counts, width=5, label=label)
    ax.bar(decades, listens, width=4, label='User listens')
    ax.bar(decades, perfs, width=3, label='User performances')

    ax.set_title('{} by decade'.format(label))
    ax.set_ylabel("Count")
    ax.set_xlabel("Decade")
    ax.set_xticks(range(min(decades), max(decades) + 1, 10))
    ax.set_xticklabels(range(min(decades), max(decades) + 1, 10), rotation=45)
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.grid(b=True, which='major', color='r', linestyle='-')
    ax.yaxis.grid(b=True, which='minor', linestyle='--')
    ax.legend()


@to_bytes_fig
def plot_works_per_composer(ax, qs):
    by_composer = (
        qs
        .values('composer__surname')
        .order_by()
        .annotate(wcount=Count('composer'))
        .order_by('-wcount')
        .annotate(avg_yr=Avg('year'))
    )[:10]

    composers = [x['composer__surname'] for x in by_composer]
    works = [x['wcount'] for x in by_composer]
    yrs = [x['avg_yr'] for x in by_composer]
    eras = era_from_years(yrs)

    sns.set_theme(style="whitegrid")
    sns.barplot(x=composers, y=works, hue=eras, palette=ERAS_CMAP, dodge=False, ax=ax)

    ax.set_title('{} per composer'.format(settings.WORK_PLURAL_LABEL.title()))
    ax.set_xticklabels(composers, rotation=45)
    ax.set_ylabel("Count")
    ax.yaxis.grid()
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(*zip(*sorted(list(zip(handles, labels)), key=lambda x: ERAS_ORDER.get(x[1]))), title='Era', loc='upper right')


@to_bytes_fig
def plot_perfs_per_composer(ax, qs):
    by_composer = (
        qs
        .values('composer__surname', 'user_perfs')
        .order_by()
        .annotate(ocount=Count('composer'))
        .order_by('-user_perfs')
        .exclude(user_perfs=0)
        .annotate(avg_yr=Avg('year'))
    )[:10]

    composers = [x['composer__surname'] for x in by_composer]
    perfs = [x['user_perfs'] for x in by_composer]
    yrs = [x['avg_yr'] for x in by_composer]
    eras = era_from_years(yrs)

    sns.set_theme(style="whitegrid")
    if composers:
        sns.barplot(x=composers, y=perfs, hue=eras, palette=ERAS_CMAP, dodge=False, ax=ax)

    ax.set_title('User performances per composer')
    ax.set_xticklabels(composers, rotation=45)
    ax.set_ylabel("Count")
    ax.yaxis.grid(which="minor")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(*zip(*sorted(list(zip(handles, labels)), key=lambda x: ERAS_ORDER.get(x[1]))), title='Era', loc='upper right')


@to_bytes_fig
def plot_listens_per_composer(ax, qs):
    by_composer = (
        qs
        .values('composer__surname', 'user_listens')
        .order_by()
        .annotate(ocount=Count('composer'))
        .order_by('-user_listens')
        .exclude(user_listens=0)
        .annotate(avg_yr=Avg('year'))
    )[:10]

    composers = [x['composer__surname'] for x in by_composer]
    listens = [x['user_listens'] for x in by_composer]
    yrs = [x['avg_yr'] for x in by_composer]
    eras = era_from_years(yrs)

    sns.set_theme(style="whitegrid")
    if composers:
        sns.barplot(x=composers, y=listens, hue=eras, palette=ERAS_CMAP, dodge=False, ax=ax)

    ax.set_title('User listens per composer')
    ax.set_xticklabels(composers, rotation=45)
    ax.set_ylabel("Count")
    ax.yaxis.grid(which="minor")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(*zip(*sorted(list(zip(handles, labels)), key=lambda x: ERAS_ORDER.get(x[1]))), title='Era', loc='upper right')


@to_bytes_fig
def plot_works_per_era(ax, qs):
    era_counts = Counter([w.era for w in qs])
    counts = era_counts.values()
    eras = era_counts.keys()

    ax.pie(counts, labels=eras, colors=[ERAS_CMAP[e] for e in eras], autopct='%.0f%%')
    ax.set_title('Proportion of {} per era'.format(settings.WORK_PLURAL_LABEL))


@to_bytes_fig
def plot_perfs_per_era(ax, qs):
    by_era = sorted([(w.era, w.user_perfs) for w in qs.exclude(user_perfs=0)], key=lambda x: x[0])
    by_era = [(key, sum(num for _, num in value)) for key, value in itertools.groupby(by_era, lambda x: x[0])]
    if by_era:
        eras, perfs = zip(*by_era)
        ax.pie(perfs, labels=eras, colors=[ERAS_CMAP[e] for e in eras], autopct='%.0f%%')
    ax.set_title('Proportion of user performances per era')


@to_bytes_fig
def plot_listens_per_era(ax, qs):
    by_era = sorted([(w.era, w.user_listens) for w in qs.exclude(user_listens=0)], key=lambda x: x[0])
    by_era = [(key, sum(num for _, num in value)) for key, value in itertools.groupby(by_era, lambda x: x[0])]
    if by_era:
        eras, listens = zip(*by_era)
        ax.pie(listens, labels=eras, colors=[ERAS_CMAP[e] for e in eras], autopct='%.0f%%')
    ax.set_title('Proportion of user listens per era')


@to_bytes_fig
def plot_duration_hist(ax, qs):
    by_duration = (
        qs
        .values('album__duration')
    )

    ax.hist([x['album__duration'] for x in by_duration if x['album__duration']], bins=20)
    ax.set_title('Album durations')
    ax.set_xlabel("Duration (minutes)")
    ax.set_ylabel("Count")


@to_bytes_fig
def plot_top_lists_by_decade(ax, qs):
    by_decades = (
        qs
        .extra(select={'year': 'FLOOR(year/10)*10'})
        .values('year')
        .annotate(dcount=Count('list'))
        .order_by()
    )
    decades = [int(x['year']) for x in by_decades]
    counts = [x['dcount'] for x in by_decades]
    ax.bar(decades, counts,  width=5)

    ax.set_title('Top lists by decade')
    ax.set_ylabel("Count")
    ax.set_xlabel("Decade")
    ax.set_xticks(range(min(decades), max(decades) + 1, 10))
    ax.set_xticklabels(range(min(decades), max(decades) + 1, 10), rotation=45)
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.grid(b=True, which='major', color='r', linestyle='-')
    minor_ticks = np.arange(0, max(counts) + 10, 5)
    ax.set_yticks(minor_ticks, minor=True)
    ax.yaxis.grid(b=True, which='minor', linestyle='--')
