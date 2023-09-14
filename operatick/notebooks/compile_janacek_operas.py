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
wikiurl = "https://en.wikipedia.org/w/index.php?title=List_of_compositions_by_Leo%C5%A1_Jan%C3%A1%C4%8Dek&oldid=1022677798"
table_class = "wikitable sortable plainrowheaders jquery-tablesorter"
response = requests.get(wikiurl)
print(response.status_code)

# %%
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', {'class': 'wikitable'})
titles = []
for title in table.findAll('i'):
    try:
        titles.append(title.find('a').text)
    except AttributeError:
        pass
# First 9 titles are Operas
titles = titles[:9]
titles

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
df = df[df['Genre'] == 'Opera']
df['year'] = df['Date composed'].apply(str).apply(lambda x: re.findall(r'\d{4}', x)[-1])
df['title'] = titles
df['language'] = LANGUAGE_MAP['Czech']
df['composer'] = 'Janáček'
print(df.head(10))


# %%
data = df[['title', 'language', 'year', 'composer']]
data

# %%
data.to_csv('notebooks/data/janacek_operas.csv', index=False)
