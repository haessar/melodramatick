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
wikiurl = "https://en.wikipedia.org/wiki/List_of_compositions_by_Giuseppe_Verdi"
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
}

# %%
df['Year'] = df["Premiere"].apply(lambda x: re.search(r'\d{4}', x).group(0))
df['Composer'] = 'Verdi'
data = df.drop(['#', "Libretto", "Acts", "Premiere", "Remarks"], axis=1)
data = data.rename(columns={'Title': 'title', 'Language': 'language', 'Year': 'year', 'Composer': 'composer'})
data['language'] = data['language'].map(LANGUAGE_MAP)
# Drop duplicated/revised operas
data.drop(data[data["title"] == "Jérusalem"].index, inplace=True)
data.drop(data[data["title"] == "Aroldo"].index, inplace=True)
data.drop(data[data["title"] == "Giovanna de Guzman"].index, inplace=True)
data.drop(data[data["title"] == "Le trouvère"].index, inplace=True)
data.drop(data[data["title"] == "Don Carlo"].index, inplace=True)
data

# %%
data.to_csv('notebooks/data/verdi_operas.csv', index=False)
