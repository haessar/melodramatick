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
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import re

from bs4 import BeautifulSoup
from django.conf import settings
from google.cloud import translate_v2 as translate
import numpy as np
import pandas as pd
import requests

if __name__ == "__main__":
    import django_initialiser  # noqa: F401
from melodramatick.work.models import SubGenre

# %%
# get the response in the form of html
wikiurl = "https://en.wikipedia.org/wiki/List_of_operas_by_Gaetano_Donizetti"
table_class = "wikitable sortable plainrowheaders jquery-tablesorter"
response = requests.get(wikiurl)
print(response.status_code)

# %%
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', {'class': 'wikitable'})

# %%
df = pd.read_html(str(table), flavor='bs4')
df = pd.DataFrame(df[0])
print(df.head())
print(df.columns)

# %%
LANGUAGE_MAP = {
    "Italian": "it",
    "English": "en",
    "German": "de",
    "Russian": "ru",
    "Czech": "cz",
    "French": "fr",
    "Latin": "la",
}

# %%
df['year'] = df['Premiere[2]']['Date'].apply(str).apply(lambda x: re.findall(r'\d{4}', x)[-1])
df['title'] = df['Title']['Title']
df['language'] = LANGUAGE_MAP['Italian']
df['composer'] = 'Donizetti'
print(df.head())


# %%
# Change language for titles with French translation notes
df.loc[df['title'].str.contains('French'), 'language'] = LANGUAGE_MAP['French']
# Remove everything between brackets in title
df['title'] = df['title'].str.replace(r"[\(\[].*?[\)\]]", "").str.strip()

# %%
# Predict language using title and genre
df['genre'] = df['Genre']['Genre'].replace(np.nan, "").apply(str)
translate_client = translate.Client.from_service_account_json(settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON)
language_prediction = (df['title'] + ' ' + df['genre']).apply(lambda x: translate_client.detect_language(x).get("language"))

# %%
sg_map = {}
df["genre"] = df["genre"].str.replace(r"[\(\[].*?[\)\]]", "").str.strip()
for g in df["genre"]:
    if g and g not in sg_map:
        print("~~~ " + g)
        sg = SubGenre.objects.filter(name__contains=g)
        if len(sg) > 1:
            sg = SubGenre.objects.filter(name__iexact=g)
        if len(sg) == 1:
            print(sg)
            obj = sg.get()
        elif not sg:
            obj, _ = SubGenre.objects.get_or_create(name=g.capitalize())
        else:
            continue
        sg_map[g] = obj

# %%
# Apply language prediction as long as it falls in LANGUAGE_MAP ("it" is default)
mask = language_prediction.isin(LANGUAGE_MAP.values())
df.loc[mask, 'language'] = list(language_prediction.loc[mask])

# %%
data = df[['title', 'language', 'year', 'composer', 'genre']]
# Remove multi-index
data.columns = data.columns.get_level_values(0)
# Drop duplicated/revised operas
data.drop(data[data["title"] == "L'eremitaggio di Liverpool"].index, inplace=True)
data.drop(data[data["title"] == "Le convenienze teatrali"].index, inplace=True)
data.drop(data[data["title"] == "Otto mesi in due ore, ossia Gli esiliati in Siberia"].index, inplace=True)
data.drop(data[data["title"] == "Buondelmonte"].index, inplace=True)
data.drop(data[data["title"] == "Lucie de Lammermoor"].index, inplace=True)
data.drop(data[data["title"] == "Betly, o La capanna svizzera"].index, inplace=True)
data.drop(data[data["title"] == "Il duca d'Alba"].index, inplace=True)
data.drop(data[data["title"] == "Dom Sebastian von Portugal"].index, inplace=True)
data


# %%
data.to_csv('notebooks/data/donizetti_operas.csv', index=False)


# %%
# Update genres
# for idx, row in data.iterrows():
#     if row["genre"] in sg_map:
#         obj = Opera.objects.get(title=row["title"])
#         if not obj.sub_genre:
#             obj.sub_genre = sg_map[row["genre"]]
#             obj.save()
