# -*- coding: utf-8 -*-
#! /usr/bin/env python
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from tqdm import tqdm
import sys,os

# process bar
def my_hook(t):
    last_b = [0]

    def update_to(b=1, bsize=1, tsize=None):
        if tsize is not None:
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b

    return update_to

def download_paper_from_scihub(doi):

    try:
        sci_hub = 'https://sci-hub'
        suffix_list = ['se','st','tw']
        soup = ''
        for suffix in suffix_list:
            response = requests.get(f'{sci_hub}.{suffix}/{doi}')
            if response.status_code == 200:
                print('\nConnected to sci-hub.')
                soup = BeautifulSoup(response.content, 'lxml')
                break
            else:
                continue

        citation = soup.select_one('#citation').get_text()
        print(f'\nThe paper you are looking for is:\n{citation}')

        download_link = soup.select_one('button')['onclick'].split('\'')[1]
        if not download_link.startswith('http'):
            download_link = f'https:{download_link}'

        print('\nDowload PDF')
        filename = download_link.split('/')[-1].split('?')[0]
        with tqdm(unit = 'B', unit_scale = True, unit_divisor = 1024, miniters = 1, desc = filename) as t:
            urlretrieve(download_link, filename = f'{filename}.tmp', reporthook = my_hook(t), data = None)
        os.rename(f'{filename}.tmp',filename)
        print(f"Saved paper to {filename}.")
    except:
        print(f'Failed retrieve PDF for {doi}, check on browser.')


if __name__ == '__main__':
    for doi in sys.argv[1].split(','):
        download_paper_from_scihub(doi)