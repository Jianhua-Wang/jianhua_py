from bs4 import BeautifulSoup
import requests
import pandas as pd
import argparse
import os
from urllib.request import urlretrieve
from tqdm import tqdm


def print_logo():
    logo = '''
========================================================================
     \033[1;33m/\\\033[0m
    \033[1;33m/__\\\033[0m\033[1;31m\\\033[0m            Download SRA and GEO fastq, simple and faster
   \033[1;33m/\033[0m  \033[1;31m---\\\033[0m
  \033[1;33m/\\\033[0m      \033[1;31m\\\033[0m          Author: Jianhua Wang
 \033[1;33m/\033[0m\033[1;32m/\\\033[0m\033[1;33m\\\033[0m     \033[1;31m/\\\033[0m         Date:   08-09-2021
 \033[1;32m/  \   /\033[0m\033[1;31m/__\\\033[0m
\033[1;32m`----`-----\033[0m
========================================================================
    '''
    print(logo)


def gsm2srx(gsm):
    '''Get SRX ID of GSM.

    >>> gsm2srx('GSM2496146')
    'SRX2577854'
    '''
    response = requests.get(
        f'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gsm}')
    soup = BeautifulSoup(response.content, 'lxml')

    srx_id = None
    for a in soup.select('a'):
        if a.text.startswith('SRX'):
            srx_id = a.text
    return srx_id


def gse2bioproj(gse):
    '''Get PRJNA ID of GSE

    >>> gse2bioproj('GSE139635')
    'PRJNA583471'
    '''
    res = requests.get(
        f'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gse}')
    soup = BeautifulSoup(res.content, 'lxml')

    bioproj = None
    for a in soup.select('a'):
        if a.text.startswith('PRJNA'):
            bioproj = a.text
    return bioproj


def search_ENA(acc):
    '''Get SRR, GSM, SE/PE, Read Count, url, Sample Name from ENA

    >>> search_ENA('SRR10376211')
    [{'sample_accession': 'SAMN13164622', 'sample_alias': 'GSM4144990', \
'sample_title': 'HARPE on DPE - replicate 1 in cells', 'run_accession': 'SRR10376211', \
'read_count': '3766075', 'library_layout': 'SINGLE', \
'fastq_ftp': 'ftp.sra.ebi.ac.uk/vol1/fastq/SRR103/011/SRR10376211/SRR10376211.fastq.gz'}]
    '''
    if acc.startswith('GSE'):
        acc = gse2bioproj(acc)
    elif acc.startswith('GSM'):
        acc = gsm2srx(acc)
    else:
        pass
    ena_url = 'https://www.ebi.ac.uk/ena/portal/api/filereport'
    selected_cols = ','.join([
        'sample_alias', 'sample_title', 'run_accession', 'read_count',
        'library_layout', 'fastq_ftp',
    ])
    res = requests.get(
        f'{ena_url}?accession={acc}&result=read_run&fields={selected_cols}&format=json'
    )
    return pd.DataFrame(res.json())


def my_hook(t):
    last_b = [0]

    def update_to(b=1, bsize=1, tsize=None):
        if tsize is not None:
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b

    return update_to


def download_fq(url, out_f):
    with tqdm(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=out_f) as t:
        urlretrieve(url, filename=f'{out_f}.tmp',
                    reporthook=my_hook(t), data=None)
    os.rename(f'{out_f}.tmp', out_f)


def parseArguments():
    parser = argparse.ArgumentParser(usage="python fastq_dl.py SRR9595574",
                                     description="Given a GSE, GSM, SRX, or SRR accession and download the fastq files",)
    parser.add_argument('Accession', nargs='?', type=str,
                        help='GEO or SRA Accession, i.e. SRR9595574, SRX2577854, GSM2496146, or GSE87254. Use "," to specify more than one Accession'),
    parser.add_argument('-f', '--file', type=str,
                        help='Accession list file', metavar=''),
    args = parser.parse_args()
    return args


def main():
    print_logo()
    accs = []
    args = parseArguments()
    if args.file:
        accs = open(args.file, 'r')
        accs = [i.strip() for i in accs.readlines()]
    else:
        accs = args.Accession.split(',')

    meta = []
    for acc in accs:
        meta.append(search_ENA(acc))
    meta = pd.concat(meta, ignore_index=True)
    i = 0
    while True:
        if i == 0:
            meta_file = f'./meta.txt'
        else:
            meta_file = f'./meta.{i}.txt'
        if os.path.exists(meta_file):
            i += 1
        else:
            meta.to_csv(meta_file, sep='\t', index=False)
            break
    print(f'save meta information to {meta_file}')

    for srr, urls in meta[['run_accession', 'fastq_ftp']].values:
        urls = urls.split(';')
        if len(urls) == 1:
            download_fq(f'ftp://{urls[0]}', f'{srr}.fastq.gz')
        else:
            for i, url in enumerate(urls, start=1):
                download_fq(f'ftp://{url}', f'{srr}_{i}.fastq.gz')


if __name__ == '__main__':
    main()
