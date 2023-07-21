# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Django Shell-Plus
#     language: python
#     name: django_extensions
# ---

# %%
# Run using 'python manage.py shell_plus --notebook' with venv activated.

# %%
import csv

from unidecode import unidecode

if __name__ == "__main__":
    import django_initialiser  # noqa: F401
from melodramatick.composer.models import Composer
from melodramatick.listen.models import Album
from melodramatick.utils.spotify_api import auth_manager, get_playlist_duration
from opera.models import Opera

# %%
user_id = "js07whh"
composer = ""
overwrite = False
if overwrite and not composer:
    print('WARNING - This will overwrite spotify_links for ALL operas!')


def unformat_title(title):
    return unidecode(title.lower().strip())


# %%
url = "https://api.spotify.com/v1/users/{}/playlists".format(user_id)
scope = "playlist-read-private playlist-read-collaborative"
sp = auth_manager(scope=scope)

# %%
# Gather all user playlists
offset = 0
increment = 50
items = []
while True:
    response = sp.user_playlists(user_id, limit=50, offset=offset)
    if response['items']:
        items.extend(response['items'])
        offset += increment
    else:
        break
len(items)

# %%
# Remove incomplete playlists from consideration
items = [i for i in items if i['tracks']['total'] >= 8]
if composer:
    # Consider only items that contain composer name
    items = [i for i in items if composer.lower() in i['name'].lower()]
# Set item title based on following format: "Composer - Title - Conductor"
output = []
for item in items:
    try:
        item['composer'] = item['name'].split(' - ')[0].strip()
        item['title'] = item['name'].split(' - ')[1].strip()
    except IndexError:
        print('item ' + item['name'] + ' in incorrect format')
    else:
        item['duration'] = get_playlist_duration(item['id'], sp)
        output.append(item)

# %%
# (optional) Find composers who might not have been added to db yet
if not composer:
    missing_composers = set()
    for playlist in output:
        if not Composer.objects.filter(surname__iexact=playlist['composer']):
            print('Composer "{}" not found in db'.format(playlist['composer']))
            missing_composers.add(playlist['composer'])
    if missing_composers:
        with open("data/update_spotifiy_links_missing_composers.csv", "w", newline='') as f:
            fieldnames = ['surname', 'first_name', 'nationality', 'era']
            writ = csv.writer(f)
            writ.writerow(fieldnames)
            blank = ['']*len(missing_composers)
            writ.writerows(zip(*[missing_composers, blank, blank, blank]))

# %%
# (optional) Find operas that might not have been added to db yet
csvfile = open('data/playlist_operas.csv', 'w', newline='')
fieldnames = ['title', 'language', 'year', 'composer']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

if not composer:
    for playlist in output:
        composer_qs = Composer.objects.filter(surname__iexact=playlist['composer'])
        if composer_qs:
            opera_qs = Opera.objects.filter(composer__in=composer_qs)
            if not opera_qs.filter(title__icontains=playlist['title']):
                # Handle icontains failure for non-ASCII chars in SQLite (see https://www.sqlite.org/faq.html#q18)
                if not opera_qs.filter(title__icontains=playlist['title'].title()):
                    if not opera_qs.filter(aka__title__icontains=playlist['title']):
                        if not opera_qs.filter(aka__title__icontains=playlist['title'].title()):
                            writer.writerow({'title': playlist['title'], 'year': '', 'composer': playlist['composer']})
                            print(playlist['title'])

csvfile.close()

# %%
model_operas = Opera.objects.filter(composer__surname=composer) if composer else Opera.objects.all()
assigned_playlist_ids = set()
for opera in model_operas:
    if not opera.album.filter() or overwrite:
        title = unformat_title(opera.title)
        if title == "falstaff":
            print()
        opera_composer = unformat_title(str(opera.composer.surname))
        available_items = [i for i in output if title == unformat_title(i['title'])
                           and opera_composer == unformat_title(i["composer"])]
        if not available_items and opera.aka.filter():
            for aka in opera.aka.filter():
                aka_title = unformat_title(aka.title)
                available_items += [i for i in output if aka_title == unformat_title(i['title'])
                                    and opera_composer == unformat_title(i["composer"])]
        existing_playlist_ids = {a.id for a in opera.album.filter() if "playlist" in a.uri}
        if available_items:
            print("Adding spotify_link(s) to {} - {}".format(composer if composer else opera_composer.title(), opera))
            for item in available_items:
                pl, _ = Album.objects.get_or_create(id=item["id"])
                pl.work = opera
                if pl.duration and pl.duration != int(item["duration"]):
                    print("pre-existing playlist {} duration has changed from {} to {}".format(
                        item["uri"],
                        pl.duration,
                        item["duration"]
                    ))
                pl.duration = int(item["duration"])
                pl.uri = item["uri"]
                try:
                    image_url = item["images"][0]["url"]
                    if image_url:
                        pl.image_url = image_url
                except IndexError:
                    pass
                pl.save()
                assigned_playlist_ids.add(item["id"])
                existing_playlist_ids.discard(item["id"])
        if existing_playlist_ids:
            print("Following user playlist Album models can no longer be found on Spotify:")
            print("\n".join([str(a.uri) for a in opera.album.filter(id__in=existing_playlist_ids)]))
if assigned_playlist_ids:
    for o in output:
        if o["id"] not in assigned_playlist_ids:
            print("Unassigned spotify_link: {} - {}".format(o["composer"], o["title"]))
