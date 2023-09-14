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
wikiurl = "https://en.wikipedia.org/wiki/List_of_operas_by_Richard_Strauss"
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
df['year'] = df['Period[a]']['Period[a]'].apply(str).apply(lambda x: re.match(r'\d{4}', x).group(0))
df['title'] = df['Title']['Title']
df['language'] = 'de'
df['composer'] = 'Strauss'
print(df.head())


# %%
# Remove everything between brackets in title
df['title'] = df['title'].str.replace(r"[\(\[].*?[\)\]]", "")
data = df[['title', 'language', 'year', 'composer']]
# Remove multi-index
data.columns = data.columns.get_level_values(0)
# Drop duplicated/revised operas
data.drop(data[data["title"] == "Ariadne auf Naxos,second version"].index, inplace=True)
data.drop_duplicates(inplace=True)
data

# %%
data.to_csv('notebooks/data/strauss_operas.csv', index=False)
