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
from html import unescape
import re

from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
import httpx
from unidecode import unidecode

if __name__ == "__main__":
    import django_initialiser  # noqa: F401
from melodramatick.composer.models import Composer
from opera.models import Opera
from melodramatick.top_list.models import List, ListItem


# %%
def create_soup(url):
    """url: URL of opera list."""
    html = httpx.get(url).text
    return BeautifulSoup(html)


def create_opera_list(soup, url, get_name, get_publication, get_year=None, get_author=None):
    """
    soup: BeautifulSoup object containing full html.
    url: URL of opera list.
    get_X: lambda function to obtain X from each record in soup."""
    name = get_name(soup)
    pub = get_publication(soup)
    year = get_year(soup) if get_year else None
    author = get_author(soup) if get_author else None
    opera_list, _ = List.objects.get_or_create(name=name, publication=pub, url=url, year=year, author=author)
    return opera_list


def create_list_operas(opera_list, record_soup, get_opera, get_composer_surname, get_year=None, get_rank=None,
                       split_char=None, reverse=False):
    """
    opera_list: List object
    record_soup: iterable bs4 ResultSet, containing one record for each opera in list.
    get_X: lambda function to obtain X from each record in record_soup.
    split_char -> str: where a record contains multiple operas, character used as delimiter to split them.
    reverse: boolean to specify whether list is in reverse order.
    """
    missing_composers = set()
    missing_ranks = set()
    if reverse:
        record_soup = reversed(record_soup)
    for idx, record in enumerate(record_soup, 1):
        composer_surname = get_composer_surname(record)
        opera = get_opera(record)
        year = get_year(record) if get_year else ''
        rank = int(get_rank(record)) if get_rank else idx
        try:
            model_composer = Composer.objects.get(surname__iexact=composer_surname)
        except ObjectDoesNotExist:
            model_composer = [c for c in Composer.objects.all() if unidecode(c.surname) == unidecode(composer_surname)]
            if not model_composer:
                print('No match for ' + composer_surname)
                missing_composers.add(composer_surname)
                missing_ranks.add(rank)
                continue
            else:
                model_composer = model_composer[0]
        composer_operas = Opera.objects.filter(composer=model_composer)
        # Deal with case of double record
        if split_char:
            operas = [o.strip() for o in opera.split(split_char)]
        else:
            operas = [opera.strip()]
        for o in operas:
            model_operas = composer_operas.filter(title__icontains=o)
            if not model_operas:
                # Try checking opera akas for alternative name
                model_operas = composer_operas.filter(aka__title__icontains=o)
            if not model_operas:
                # Try checking opera notes for alternative name
                model_operas = composer_operas.filter(notes__icontains=o)
            if not model_operas:
                print('{}: {} not found in database'.format(model_composer, o))
                try:
                    writer.writerow({'title': o, 'year': year, 'composer': model_composer.surname})
                except ValueError:
                    pass
                except NameError as e:
                    if "writer" in str(e):
                        pass
                    else:
                        raise e
                missing_ranks.add(rank)
                continue
            elif model_operas.count() > 1:
                if model_operas.filter(title__iexact=o):
                    model_operas = model_operas.filter(title__iexact=o)
                else:
                    # Assume a cycle of operas is selected in list, in which case create ListItem object for each
                    for cycle_opera in model_operas:
                        ListItem.objects.get_or_create(item=cycle_opera, list=opera_list, position=rank)
                    continue
                assert model_operas.count() == 1, o
            ListItem.objects.get_or_create(item=model_operas.get(), list=opera_list, position=rank)
    if missing_composers:
        with open("notebooks/data/compile_lists_missing_composers.csv", "w", newline='') as f:
            fieldnames = ['surname', 'first_name', 'nationality']
            writ = csv.writer(f)
            writ.writerow(fieldnames)
            blank = ['']*len(missing_composers)
            writ.writerows(zip(*[missing_composers, blank, blank]))
    if missing_ranks:
        print("Following ranks are still missing:\n" + "\n".join(sorted(map(str, missing_ranks))))


# %%
# # OPTIONAL: Run this cell only if you want to create csv of operas missing from db.
csvfile = open('notebooks/data/misc_operas.csv', 'w', newline='')
fieldnames = ['title', 'language', 'year', 'composer']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

# %% [markdown]
# # Add lists in each cell below

# %%
# The Guardian - Top 50 operas
url = "https://www.theguardian.com/music/2011/aug/20/top-50-operas"
soup = create_soup(url)
opera_list = create_opera_list(
    soup,
    url,
    get_name=lambda x: x.title.text.split(' | ')[0],
    get_publication=lambda x: x.title.text.split(' | ')[-1],
    get_author=lambda x: x.find('div', {'class': 'dcr-fj5ypv'}).find('a').text,
    get_year=lambda x: "2011",
)
create_list_operas(
    opera_list,
    record_soup=soup.find_all('h2', text=re.compile(r'^[0-9]{1,2}\s.*')),
    # unescape to convert "nbsp;" html chars to "\xa0", which can be replaced.
    get_opera=lambda x: unescape(re.match(r'^[0-9]{1,2}\s(.*)$', x.text.split('(')[0].strip()).group(1)).replace('\xa0', ' '),
    get_composer_surname=lambda x: x.find_next_sibling('p').strong.text.strip().split(' ')[-1],
    get_year=lambda x: re.match(r'.*([0-9]{4})$', x.find_next_sibling('p').em.text.strip()).group(1),
    split_char='/'
)

# %%
# Opera Sense - Top 10 Most Popular Operas
url = "https://www.operasense.com/most-popular-operas/"
soup = create_soup(url)
opera_list = create_opera_list(
    soup,
    url,
    get_name=lambda x: x.find('h1').text,
    get_publication=lambda x: x.find('meta', {'property': 'og:site_name'}).attrs['content'],
    get_author=lambda x: x.find('h4', {'class': 'author'}).find('strong').text,
    get_year=lambda x: re.search(r'\d{4}', x.find('time', {'class': 'entry-date'}).text).group()
)
create_list_operas(
    opera_list,
    record_soup=soup.find('ol').find_all('li'),
    get_opera=lambda x: x.em.text,
    get_composer_surname=lambda x: re.search(r', by ([^.]*)', x.text).group(1),
)

# %%
# Classical Music - 20 Greatest operas of all time
url = "https://www.classical-music.com/features/works/20-greatest-operas-all-time/"
soup = create_soup(url)
opera_list = create_opera_list(
    soup,
    url,
    get_name=lambda x: "The 20 Greatest Operas of all time",
    get_publication=lambda x: "Classical Music",
    get_author=lambda x: "BBC Music Magazine",
    get_year=lambda x: "2019",
)
create_list_operas(
    opera_list,
    record_soup=soup.find('section', {'itemprop': 'articleBody'}).find_all('h2'),
    get_composer_surname=lambda x: x.find('a').text,
    get_opera=lambda x: re.search(r"’s\s([^(]*)", x.text).group(1).strip().replace("’", "'"),
    get_year=lambda x: re.search(r".*\((\d{4})\)*", x.text).group(1).strip(),
    reverse=True
)

# %%
# Talk Classical - Top 272 Recommended Operas
url = "https://www.talkclassical.com/17996-compilation-tc-top-recommended.html"
soup = create_soup(url)
opera_list = create_opera_list(
    soup,
    url,
    get_name=lambda x: "Top 272 Recommended Operas",
    get_publication=lambda x: "Talk Classical",
)
li_pattern = r"^[0-9]{1,3}\.\s"
# Fix spelling errors
records = soup.find('div', {'id': 'post_message_269342'}).text \
            .replace('Martin y Soler', 'Martín y Soler') \
            .replace('De Falla', 'Falla') \
            .replace('Rimski', 'Rimsky') \
            .replace('Paisello', 'Paisiello') \
            .replace('The Makropulos Case', 'The Makropulos Affair') \
            .replace('Mitridate Re di Ponto', 'Mitridate, re di Ponto') \
            .replace('La Favorita', 'La favorite') \
            .replace('Kat’a Kabanova', 'Káťa Kabanová') \
            .replace('Johnny Spielt Auf', 'Jonny Spielt Auf') \
            .replace('Hyppolite et Aricie', 'Hippolyte et Aricie') \
            .replace('Kitesh', 'Kitezh') \
            .replace('Sorochyntsky Fair', 'The Fair at Sorochyntsi') \
            .replace('Satygraha', 'Satyagraha') \
            .replace('Licht cycle', 'Licht') \
            .replace("Elisabetta Regina d'Inghilterra", "Elisabetta, regina d'Inghilterra") \
            .replace("Lady Macbeth of the Mtsensk District", "Lady Macbeth of Mtsensk") \
            .replace("Pelléas and Mélisande", "Pelléas et Mélisande") \
            .replace("Dialogues des Carmelites", "Dialogues des Carmélites") \
            .replace('\r', '')
create_list_operas(
    opera_list,
    record_soup=filter(re.compile(r"{}(.*)$".format(li_pattern)).match, records.split('\n')),
    get_composer_surname=lambda x: re.search(r"{}(.*)\s[-,–]".format(li_pattern), x).group(1),
    get_opera=lambda x: re.search(r"{}.*[^a-zA-Z0-9_,]\s(.*)$".format(li_pattern), x).group(1)
)

# %%
# Gramophone - Top 10 Operas
url = "https://www.gramophone.co.uk/features/article/top-10-operas"
soup = create_soup(url)
opera_list = create_opera_list(
    soup,
    url,
    get_name=lambda x: "Top 10 Operas",
    get_publication=lambda x: "Gramophone",
    get_year=lambda x: re.search(r'\d{4}', x.find('span', {'class': 'published-date'}).text).group()
)
create_list_operas(
    opera_list,
    record_soup=soup.find('div', {'id': 'rich-text'}).find_all('h2')[:-1],
    get_composer_surname=lambda x: x.select('strong')[0].extract().text,
    get_opera=lambda x: re.search(r"(^[^\(]+)", x.text).group(1).strip(),
)

# %%
# Operabase - 10 most played titles
url = "https://www.operabase.com/statistics/en"
soup = create_soup(url)
opera_list = create_opera_list(
    soup,
    url,
    get_name=lambda x: "10 most played titles",
    get_publication=lambda x: "Operabase",
)
create_list_operas(
    opera_list,
    record_soup=soup.find_all('div', {'class': "jss219"})[0].find_all('tr', {'class': 'MuiTableRow-root'})[1:],
    get_composer_surname=lambda x: x.find_all("td")[1].text.split(",")[0],
    get_opera=lambda x: x.find_all("td")[0].text,
)

# %%
# Talk Classical - Top 200 Recommended Operas
url = "https://www.talkclassical.com/threads/the-tc-top-200-recommended-operas-2020-version.65366/"
soup = create_soup(url)
opera_list = create_opera_list(
    soup,
    url,
    get_name=lambda x: "Top 200 Recommended Operas",
    get_publication=lambda x: "Talk Classical",
    get_year=lambda x: "2020",
)
li_pattern = r"^(?P<rank>[0-9]{3})\s\-\s(?P<composer>.*)\s\-\s(?P<opera>.*)$"
# Fix spelling errors
records = soup.find('div', {'id': 'content_post_id_1800461'}).text \
    .replace('Don Carlo(s)', 'Don Carlo') \
    .replace('Pélléas et Mélisande', 'Pelléas et Mélisande') \
    .replace('Mussorgky', 'Mussorgsky') \
    .replace('R. Strauss', 'Strauss') \
    .replace('Dialogue des Carmélites', 'Dialogues des Carmélites') \
    .replace('Jenufa', 'Jenůfa') \
    .replace('Katja Kabanova', 'Káťa Kabanová') \
    .replace('Stiffelio / Aroldo', 'Stiffelio') \
    .replace('Medea / Medée', 'Médée') \
    .replace('City of Kitezh', 'City Kitezh') \
    .replace('Vek Makropulos', 'The Makropulos Affair') \
    .replace('Saul & David', 'Saul Og David') \
    .replace('The fairy-queen (16p)', 'The Fairy Queen') \
    .replace('Enescu', 'Enesco') \
    .replace('Charpentier', 'Charpentier (Gustave)') \
    .replace('Guercoeur', 'Guercœur') \
    .replace('Bajazed', 'Bajazet')
end_idx = [i for i, s in enumerate(records.split("\n")) if '200 -' in s][0] + 1
create_list_operas(
    opera_list,
    record_soup=filter(re.compile(li_pattern).match, records.split('\n')[:end_idx]),
    get_composer_surname=lambda x: re.search(li_pattern, x).group("composer"),
    get_opera=lambda x: re.search(li_pattern, x).group("opera"),
    get_rank=lambda x: re.search(li_pattern, x).group("rank"),
)

# %%
# Talk Classical - Top 200 Recommended Operas (2015)
url = "https://www.talkclassical.com/threads/the-tc-top-200-recommended-operas-2015-version.40887/"
soup = create_soup(url)
opera_list = create_opera_list(
    soup,
    url,
    get_name=lambda x: "Top 200 Recommended Operas (2015)",
    get_publication=lambda x: "Talk Classical",
    get_year=lambda x: "2015",
)
li_pattern = r"^(?P<rank>[0-9]{1,3})\.\s(?P<composer>.*)\:\s(?P<opera>.*)$"
records = soup.find('div', {'id': 'content_post_id_975710'}).text \
    .replace('Enescu', 'Enesco') \
    .replace('Charpentier', 'Charpentier (Gustave)')
create_list_operas(
    opera_list,
    record_soup=filter(re.compile(li_pattern).match, records.split('\n')),
    get_composer_surname=lambda x: re.search(li_pattern, x).group("composer"),
    get_opera=lambda x: re.search(li_pattern, x).group("opera"),
    get_rank=lambda x: re.search(li_pattern, x).group("rank"),
)

# %%
# # OPTIONAL: Close csv file.
csvfile.close()
