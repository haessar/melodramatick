"""
Run within Django shell:
    exec(open("./melodramatick/utils/quotel_api.py").read())
"""

import datetime
import random

from django.conf import settings
import requests

if __name__ == "__main__":
    import melodramatick.utils.django_initialiser  # noqa: F401
from django.contrib.sites.models import Site
from melodramatick.composer.models import Composer, Quote


COMPOSER_AUTHOR_ID = {
    "Mozart": 12340,
    "Verdi": 17455,
    "Puccini": 15666,
    "Wagner": 18331,
    "Rossini": 17139,
    "Beethoven": 22212,
    "Bizet": 12243,
    "Monteverdi": 24328,
    "Britten": 5077,
    "Strauss": 18300,
    "Stravinsky": 1694,
    "Massenet": 30277,
    "Rameau": 21603,
    "Berlioz": 8033,
    "Berg": 12676,
    "Mussorgsky": 28978,
    "Glass": 19614,
    "Leoncavallo": 27101,
    "Meyerbeer": 15663,
    "Weber": 3831,
    "Gershwin": 9837,
    "Mascagni": 20929,
    "Debussy": 24176,
    "Ravel": 24023,
    "Menotti": 15699,
    "Dvořák": 14289,
}


def quote_of_the_day():
    day = datetime.datetime.today().strftime("%Y:%m:%d")
    random.seed(day)
    quotes = Quote.objects.filter(composer__sites__in=[Site.objects.get_current()])
    if quotes:
        return quotes[random.randint(1, len(quotes))]


def populate_composer_quotes():
    url = "https://quotel-quotes.p.rapidapi.com/quotes"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": settings.RAPID_API_KEY,
        "X-RapidAPI-Host": "quotel-quotes.p.rapidapi.com"
    }
    for k, v in COMPOSER_AUTHOR_ID.items():
        composer = Composer.all_sites.get(surname=k)
        if Quote.objects.filter(composer=composer):
            continue
        payload = {"authorId": v}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            for q in response.json():
                _, created = Quote.objects.get_or_create(id=q["quoteId"], composer=composer, quote=q["quote"])
                if created:
                    print("added {} quote with ID {}".format(k, q["quoteId"]))


if __name__ == "__main__":
    populate_composer_quotes()
