from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Count
import pandas as pd

from melodramatick.utils.plots import EmptyFigure, to_bytes_fig


WEEKS_AGO = 7
DATE_FORMAT = "%Y-%m-%d"


@to_bytes_fig
def plot_listens_per_week(ax, qs):
    qs = qs.exclude(updated_at__isnull=True).exclude(updated_at__lte=datetime.now()-timedelta(weeks=WEEKS_AGO))
    if qs:
        week_idx = pd.date_range(
            start=datetime.now()-timedelta(weeks=WEEKS_AGO),
            end=datetime.now(), freq="W-MON").strftime(DATE_FORMAT)
        all_weeks_df = pd.DataFrame(index=week_idx)
        # "Count" the number of listens, rather than "Sum" the tally. This is because a Listen that is updated
        # with an increment to tally X will not necessarily have been listened to X times that week.
        df = pd.DataFrame(qs.values('updated_at__week', 'updated_at__year').annotate(count=Count('tally')))
        df = df.groupby(['updated_at__week', 'updated_at__year']).sum().reset_index()
        # Determine start date of week (from Monday)
        df['week'] = (
            df['updated_at__week'].astype(str) + '-' + df['updated_at__year'].astype(str)
            ).apply(lambda x: datetime.strptime(x + '-1', '%W-%Y-%w').strftime(DATE_FORMAT))
        df = pd.concat([all_weeks_df, df.set_index('week')[['count']]], axis=1).sort_index()

        df.plot.bar(ax=ax, color=settings.BACKGROUND_COLOUR)

        ax.set_title('Listens per week (past {})'.format(WEEKS_AGO))
        ax.yaxis.grid(b=True, which='major', color='black', linestyle='-')
        ax.set_ylabel("Count")
        ax.set_xlabel("Week beginning")
        ax.set_xticklabels(df.index, rotation=45, ha="right", rotation_mode='anchor')
        ax.get_legend().remove()
    else:
        raise EmptyFigure
