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
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

# %%
# get the response in the form of html
wikiurl = "https://en.wikipedia.org/wiki/List_of_compositions_by_Giacomo_Puccini"
table_class = "wikitable sortable jquery-tablesorter"
response = requests.get(wikiurl)
print(response.status_code)

# %%
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', {'class': 'wikitable'})

# %%
df = pd.read_html(str(table))
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
df['year'] = df['Premiere']['Date'].apply(str).apply(lambda x: re.search(r'\d{4}', x).group(0))
df['title'] = df['Title']['Title']
df['language'] = df['Language']['Language'].map(LANGUAGE_MAP)
df['composer'] = 'Puccini'
print(df.head())


# %%
# Fix Turandot title
df.loc[df['title'].str.contains('Turandot'), 'title'] = 'Turandot'
data = df[['title', 'language', 'year', 'composer']]
# Remove multi-index
data.columns = data.columns.get_level_values(0)
# Designate Il trittico operas
idx = data.loc[data['title'].isin(['Il tabarro', 'Suor Angelica', 'Gianni Schicchi'])].index
data.loc[idx, 'title'] += " (Il trittico)"
data = data.drop(data[data['title'] == "Il trittico"].index, axis=0)
data

# %%
data.to_csv('notebooks/data/puccini_operas.csv', index=False)
