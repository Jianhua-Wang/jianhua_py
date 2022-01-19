#!/usr/bin/env python

import pandas as pd
import requests
import re
import os
import sys

def get_citation(doi):
    try:
        py_dir = os.path.split(os.path.realpath(__file__))[0]
        journal_names = pd.read_csv(f'{py_dir}/journals.csv', header=None)
        journal_names = journal_names[journal_names[5].notnull()]
        journal_names = pd.Series(index=journal_names[1].values, data=journal_names[5].values)
        headers = {"Accept": "application/vnd.citationstyles.csl+json, application/rdf+xml"}
        res = requests.get(f'https://doi.org/{doi}', headers=headers)
        meta = res.json()
        journal = meta['container-title']
        journal_short = journal_names[journal]
        year = meta['published-print']['date-parts'][0][0]
        title = meta['title']
        given_name = meta['author'][0]['given']
        family_name = meta['author'][0]['family']
        given_name = ' '.join([i[0].upper()+'.' for i in re.split(' |-',given_name)])
        print('SHORT CITATION')
        print(f'{family_name}, {given_name} et al. {journal_short} ({year})')
        print('\nFULL CITATION')
        print(f'{family_name}, {given_name} et al. {year}. {title}. {journal}. DOI:[{doi}](http://dx.doi.org/{doi})')
    except:
        print('Failed.')

if __name__ == '__main__':
    get_citation(sys.argv[1])