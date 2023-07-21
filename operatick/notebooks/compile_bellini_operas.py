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
wikiurl = "https://en.wikipedia.org/w/index.php?title=Vincenzo_Bellini&oldid=1034656614#Operas"
table_class = "wikitable sortable jquery-tablesorter"
response = requests.get(wikiurl)
print(response.status_code)

# %%
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', {'class': 'wikitable'})

# %%
df = pd.read_html(str(table))
df = pd.DataFrame(df[0])
print(df.head(20))
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
df['year'] = df['Premiere']['Date'].apply(str).apply(lambda x: re.findall(r'\d{4}', x)[-1])
df['title'] = df['Title']['Title']
df['language'] = LANGUAGE_MAP['Italian']
df['composer'] = 'Bellini'
print(df.head(20))


# %%
# Remove everything between brackets in title
df['title'] = df['title'].str.replace(r"[\(\[].*?[\)\]]", "")
data = df[['title', 'language', 'year', 'composer']]
# Remove multi-index
data.columns = data.columns.get_level_values(0)
# Drop duplicated/revised operas
data.drop(data[data["title"] == "Bianca e Gernando"].index, inplace=True)
data


# %%
data.to_csv('notebooks/data/bellini_operas.csv', index=False)
