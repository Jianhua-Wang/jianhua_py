# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import urllib.request
import datetime

sci_hub = 'https://sci-hub.tw'


# # Download PDF from sci-hub via DOI

def download_paper_from_scihub(doi,paper_dir):
    response = requests.get(f'{sci_hub}/{doi}')
    soup = BeautifulSoup(response.content, 'lxml')
    button = '⇣ save'

    for a in soup.select('a'):
        if a.text == button:
            break
    download_link = a.attrs['onclick'].split('\'')[1]
    if not download_link.startswith('http'):
        download_link = f'https:{download_link}'
    urllib.request.urlretrieve(download_link, f"{paper_dir}/{doi.replace('.','_').replace('/','_')}.pdf")


doi = '10.1038/s41586-020-2398-2'
download_paper_from_scihub(doi)

# # Get DOI list of CNS

# ## Nature

# +
now = datetime.datetime.now()
nature_start_date = datetime.datetime(2020, 6, 18)

nature_volumes = 582+now.month-nature_start_date.month
nature_issues = 7812+(now.day-nature_start_date.day)//7
# -

nature_url = f'https://www.nature.com/nature/volumes/{nature_volumes}/issues/{nature_issues}'
response = requests.get(nature_url)
soup = BeautifulSoup(response.content, 'lxml')

nature_article_list = []
for article in soup.select('article'):
    doi_suffix = article.select('a')[0].attrs['href'].split('/')[-1]
    if doi_suffix.startswith('s'):
        nature_article_list.append(f'10.1038/{doi_suffix}')

nature_article_list

# ## Science



# # Traverse DOI list and report failed items

for doi in article_list[13:]:
    try:
        download_paper_from_scihub(doi,'nature')
    except:
        continue
    print(doi)


