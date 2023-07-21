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
#     display_name: 'Python 3.9.7 (''venv'': venv)'
#     language: python
#     name: python3
# ---

# %%
from bs4 import BeautifulSoup
import pandas as pd
import requests

if __name__ == "__main__":
    import django_initialiser  # noqa: F401
from melodramatick.work.models import SubGenre

# %%
wikiurl = "https://en.wikipedia.org/wiki/List_of_opera_genres?wprov=sfti1"
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
df["Genre"] = df["Genre"].str.replace(r"[\(\[].*?[\)\]]", "").str.strip()

# %%
for g in df["Genre"]:
    SubGenre.objects.get_or_create(name=g)
