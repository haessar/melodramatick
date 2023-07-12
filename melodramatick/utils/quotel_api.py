import datetime
import random

from django.conf import settings
import requests

if __name__ == "__main__":
    import utils.django_initialiser  # noqa: F401
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
}


def quote_of_the_day():
    day = datetime.datetime.today().strftime("%Y:%m:%d")
    random.seed(day)
    quotes = Quote.objects.all()
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
        composer = Composer.objects.get(surname=k)
        if Quote.objects.filter(composer=composer):
            continue
        payload = {"authorId": v}
        response = requests.post(url, json=payload, headers=headers)
        for q in response.json():
            Quote.objects.get_or_create(id=q["quoteId"], composer=composer, quote=q["quote"])


if __name__ == "__main__":
    populate_composer_quotes()
