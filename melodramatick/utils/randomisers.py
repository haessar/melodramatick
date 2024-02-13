import datetime
import random

if __name__ == "__main__":
    import melodramatick.utils.django_initialiser  # noqa: F401
from django.contrib.sites.models import Site
from melodramatick.composer.models import Quote
from melodramatick.listen.models import Album
from melodramatick.work.models import Work


def _daily_seed():
    day = datetime.datetime.today().strftime("%Y:%m:%d")
    random.seed(day)


def quote_of_the_day():
    _daily_seed()
    quotes = Quote.objects.filter(composer__sites__in=[Site.objects.get_current()])
    if quotes:
        return quotes[random.randint(0, len(quotes))]


def work_of_the_day():
    _daily_seed()
    today = datetime.datetime.now()
    albums = Album.objects.filter(work__site=Site.objects.get_current())
    works = Work.objects.filter(album__in=albums)
    if works:
        anniversary_works = works.filter(composer__birth_date__month=today.month, composer__birth_date__day=today.day)
        if anniversary_works:
            works = anniversary_works
        work = works[random.randint(0, len(works))]
        work.random_album = random.choice(work.album.all())
        return work
