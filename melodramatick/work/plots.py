from collections import Counter

from django.conf import settings
from django.db.models import Count, Q
import matplotlib
from matplotlib.ticker import MultipleLocator
import numpy as np
import seaborn as sns

from melodramatick.utils.plots import EmptyFigure, to_bytes_fig
from melodramatick.listen.models import Listen
from melodramatick.performance.models import Performance

matplotlib.use('Agg')

ERAS_CMAP = dict(zip([v for _, v in settings.ERAS_MAP], sns.color_palette("rocket", len(settings.ERAS_MAP))))
ERAS_ORDER = {v: idx for idx, (_, v) in enumerate(settings.ERAS_MAP)}


def era_from_years(yr_list):
    if isinstance(yr_list, (int, float)):
        yr_list = [yr_list]

    eras = []
    for yr in yr_list:
        for yr_rng, era in settings.ERAS_MAP:
            start, end = map(int, yr_rng.split("-"))
            if round(yr) in range(start, end + 1):
                eras.append(era)
                break
    return eras


def plot_stacked_composer_bars(ax, composer_eras, title, ylabel):
    top_composers = sorted(
        composer_eras,
        key=lambda composer: (-sum(composer_eras[composer].values()), composer),
    )[:10]
    if len(top_composers) == 0:
        raise EmptyFigure

    x_positions = np.arange(len(top_composers))
    bottoms = np.zeros(len(top_composers))
    era_order = [era for _, era in settings.ERAS_MAP]

    sns.set_theme(style="whitegrid")
    for era in era_order:
        counts = [composer_eras[composer][era] for composer in top_composers]
        if any(counts):
            ax.bar(x_positions, counts, bottom=bottoms, color=ERAS_CMAP[era], label=era)
            bottoms += counts

    ax.set_title(title)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(top_composers, rotation=45)
    ax.set_ylabel(ylabel)
    ax.yaxis.grid(which="minor")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(*zip(*sorted(list(zip(handles, labels)), key=lambda x: ERAS_ORDER.get(x[1]))), title='Era', loc='upper right')


@to_bytes_fig
def plot_works_by_decade(ax, qs):
    by_decades = (
        qs
        .extra(select={'year': 'FLOOR(year/10)*10'})
        .values('year')
        .annotate(
            works=Count('id'),
            listened=Count('id', filter=Q(user_listened=True)),
            ticked=Count('id', filter=Q(user_ticks=True)),
        )
        .order_by()
    )

    decades = [int(x['year']) for x in by_decades]
    counts = [x['works'] for x in by_decades]
    listens = [x['listened'] for x in by_decades]
    ticked = [x['ticked'] for x in by_decades]

    label = settings.WORK_PLURAL_LABEL.title()
    ax.bar(decades, counts, width=5, label=label)
    ax.bar(decades, listens, width=4, label='User listened works')
    ax.bar(decades, ticked, width=3, label='User ticked works')

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
    composer_eras = {}
    for composer, year in qs.values_list('composer__surname', 'year'):
        eras = era_from_years(year)
        if eras:
            composer_eras.setdefault(composer, Counter())[eras[0]] += 1

    plot_stacked_composer_bars(
        ax,
        composer_eras,
        '{} per composer'.format(settings.WORK_PLURAL_LABEL.title()),
        "Count",
    )


@to_bytes_fig
def plot_user_ticks_per_composer(ax, qs):
    composer_eras = {}
    for work in qs:
        if not work.user_ticks:
            continue
        composer = work.composer.surname
        eras = era_from_years(work.year)
        if eras:
            composer_eras.setdefault(composer, Counter())[eras[0]] += 1

    plot_stacked_composer_bars(ax, composer_eras, 'User ticks per composer', "Ticks")


@to_bytes_fig
def plot_listens_per_composer(ax, qs, user):
    composer_eras = {}
    for composer, year, tally in (
        Listen.objects
        .filter(user=user, work__in=qs)
        .values_list('work__composer__surname', 'work__year', 'tally')
    ):
        eras = era_from_years(year)
        if not eras:
            continue
        composer_eras.setdefault(composer, Counter())[eras[0]] += tally

    plot_stacked_composer_bars(ax, composer_eras, 'User listen tallies per composer', "Listen tally")


@to_bytes_fig
def plot_user_performances_per_composer(ax, qs, user):
    performance_years = {}
    for perf_id, composer, year in (
        Performance.objects
        .filter(user=user, streamed=False, work__in=qs)
        .values_list('id', 'work__composer__surname', 'work__year')
        .distinct()
    ):
        performance_years.setdefault((composer, perf_id), []).append(year)

    composer_eras = {}
    for (composer, _perf_id), years in performance_years.items():
        eras = era_from_years(sum(years) / len(years))
        if eras:
            composer_eras.setdefault(composer, Counter())[eras[0]] += 1

    plot_stacked_composer_bars(ax, composer_eras, 'User performances per composer', "Performances")


@to_bytes_fig
def plot_works_per_era(ax, qs):
    era_counts = Counter([w.era for w in qs])
    counts = era_counts.values()
    eras = era_counts.keys()

    ax.pie(counts, labels=eras, colors=[ERAS_CMAP[e] for e in eras], autopct='%.0f%%')
    ax.set_title('Proportion of {} per era'.format(settings.WORK_PLURAL_LABEL))


@to_bytes_fig
def plot_user_ticks_per_era(ax, qs):
    by_era = Counter([w.era for w in qs if w.user_ticks])
    by_era = sorted(by_era.items(), key=lambda x: x[0])
    if by_era:
        eras, perfs = zip(*by_era)
        ax.pie(perfs, labels=eras, colors=[ERAS_CMAP[e] for e in eras], autopct='%.0f%%')
    else:
        raise EmptyFigure
    ax.set_title('Proportion of user ticks per era')


@to_bytes_fig
def plot_user_performances_per_era(ax, qs, user):
    era_performances = set()
    for perf_id, year in (
        Performance.objects
        .filter(user=user, streamed=False, work__in=qs)
        .values_list('id', 'work__year')
        .distinct()
    ):
        eras = era_from_years(year)
        if eras:
            era_performances.add((eras[0], perf_id))
    by_era = sorted(Counter(era for era, _ in era_performances).items(), key=lambda x: x[0])
    if by_era:
        eras, perfs = zip(*by_era)
        ax.pie(perfs, labels=eras, colors=[ERAS_CMAP[e] for e in eras], autopct='%.0f%%')
    else:
        raise EmptyFigure
    ax.set_title('Proportion of user performances per era')


@to_bytes_fig
def plot_listens_per_era(ax, qs, user):
    era_listens = Counter()
    for year, tally in (
        Listen.objects
        .filter(user=user, work__in=qs)
        .values_list('work__year', 'tally')
    ):
        eras = era_from_years(year)
        if eras:
            era_listens[eras[0]] += tally
    by_era = sorted(era_listens.items(), key=lambda x: x[0])
    if by_era:
        eras, listens = zip(*by_era)
        ax.pie(listens, labels=eras, colors=[ERAS_CMAP[e] for e in eras], autopct='%.0f%%')
    else:
        raise EmptyFigure
    ax.set_title('Proportion of user listen tallies per era')


@to_bytes_fig
def plot_duration_hist(ax, qs):
    by_duration = (
        qs
        .values('album__duration')
    )

    data = [x['album__duration'] for x in by_duration if x['album__duration']]
    if not data:
        raise EmptyFigure
    ax.hist(data, bins=20)
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
    if set(counts) == {0}:
        raise EmptyFigure
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
