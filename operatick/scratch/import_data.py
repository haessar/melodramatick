import json

from django.conf import settings
from django.core.management import call_command
from django.db.utils import IntegrityError

if __name__ == "__main__":
    import django_initialiser  # noqa: F401
from django.contrib.sites.models import Site
from melodramatick.models import (
    CustomUser,
    Composer,
    Group,
    Quote,
    SubGenre,
    Company,
    Performance,
    Venue,
    List
)
from operatick.models import Opera


site = Site.objects.get(id=settings.SITE_ID)
"""
COMPOSER
"""
with open("operatick/scratch/composer.json", 'r') as f:
    composers = json.load(f)

for c in composers:
    try:
        composer = Composer.objects.create(
            id=c['fields']['id'],
            first_name=c['fields']['first_name'],
            nationality=c['fields']['nationality'],
            complete=c['fields']['complete'],
            gender=c['fields']['gender'],
            surname=c['pk']
        )
        composer.sites.add(site)
    except IntegrityError:
        print("Composers already loaded. Skipping")
        break

with open("operatick/scratch/group.json", 'r') as f:
    groups = json.load(f)

for g in groups:
    composers = [Composer.objects.get(surname=c) for c in g['fields']['composer']]
    try:
        group = Group.objects.create(id=g['pk'], name=g['fields']['name'])
        group.composer.set(composers)
    except IntegrityError:
        print("Groups already loaded. Skipping")
        break


with open("operatick/scratch/quote.json", 'r') as f:
    quotes = json.load(f)

for q in quotes:
    c = q['fields']['composer']
    composer = Composer.objects.get(surname=c)
    try:
        Quote.objects.create(id=q['pk'], composer=composer, quote=q['fields']['quote'])
    except IntegrityError:
        print("Quotes already loaded. Skipping")
        break

"""
WORK
"""
call_command('loaddata', 'operatick/scratch/genre.json')
call_command('loaddata', 'operatick/scratch/sub_genre.json')

with open("operatick/scratch/opera.json", 'r') as f:
    operas = json.load(f)

for o in operas:
    c = o['fields']['composer']
    composer = Composer.objects.get(surname=c)
    o['fields']['composer'] = composer
    sg = o['fields']['sub_genre']
    if sg:
        sub_genre = SubGenre.objects.get(id=sg)
        o['fields']['sub_genre'] = sub_genre
    try:
        opera = Opera.objects.create(
            id=o['pk'],
            site=site,
            **o['fields'],
        )
    except IntegrityError:
        print("Operas already loaded. Skipping")
        break

call_command('loaddata', 'operatick/scratch/aka.json')


"""
PERFORMANCE
"""
with open('operatick/scratch/company.json', 'r') as f:
    companies = json.load(f)

for idx, c in enumerate(companies, 1):
    try:
        Company.objects.create(id=idx, site=site, name=c['pk'])
    except IntegrityError:
        print("Companies already loaded. Skipping")
        break

# call_command('loaddata', 'operatick/scratch/venue.json')

with open('operatick/scratch/venue.json', 'r') as f:
    venues = json.load(f)

for v in venues:
    try:
        venue = Venue.objects.create(id=v['pk'], **v['fields'])
        venue.sites.add(site)
    except IntegrityError:
        print("Venues already loaded. Skipping")
        break

with open('operatick/scratch/performance.json', 'r') as f:
    performances = json.load(f)

for p in performances:
    c = p['fields']['company']
    company = Company.objects.get(name=c)
    venue = Venue.objects.get(id=p['fields']['venue'])
    user = CustomUser.objects.get()
    works = [Opera.objects.get(id=i) for i in p['fields']['work']]
    try:
        performance = Performance.objects.create(
            id=p['pk'],
            date=p['fields']['date'],
            company=company,
            venue=venue,
            notes=p['fields']['notes'],
            user=user,
            streamed=p['fields']['streamed'],
            site=site
        )
        performance.work.set(works)
    except IntegrityError:
        print("Performances already loaded. Skipping.")
        break


"""
LISTEN
"""
call_command('loaddata', 'operatick/scratch/listen.json')
call_command('loaddata', 'operatick/scratch/album.json')


"""
TOP LIST
"""
# call_command('loaddata', 'operatick/scratch/list.json')

with open('operatick/scratch/list.json', 'r') as f:
    lists = json.load(f)

for li in lists:
    try:
        List.objects.create(id=li['pk'], site=site, **li['fields'])
    except IntegrityError:
        print("Top Lists already loaded. Skipping")
        break

call_command('loaddata', 'operatick/scratch/list_item.json')
