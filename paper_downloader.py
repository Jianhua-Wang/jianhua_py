# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import urllib.request

sci_hub = 'https://sci-hub.tw'
doi = '10.1038/s41467-017-02317-2'


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

url = 'https://www.nature.com/nature/volumes/582/issues/7812'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'lxml')

article_list = []
for article in soup.select('article'):
    doi_suffix = article.select('a')[0].attrs['href'].split('/')[-1]
    if doi_suffix.startswith('s'):
        article_list.append(f'10.1038/{doi_suffix}')

for doi in article_list[13:]:
    try:
        download_paper_from_scihub(doi,'nature')
    except:
        continue
    print(doi)


