# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import json
import bz2
import numpy as np
import pandas as pd
import gzip
from subprocess import call,check_output

version = 'b153'

# # Create merged SNP file

# Download the merged SNP (ftp://ftp.ncbi.nlm.nih.gov/snp/archive/b153/JSON/refsnp-merged.json.bz2)

# Parse the bz2 json file

cnt = 0
with open(f'./merged_{version}.txt', 'w') as f_out:
    with bz2.BZ2File('./refsnp-merged.json.bz2', 'rb') as f_in:
        for line in f_in:
            rs_obj = json.loads(line.decode('utf-8'))
            refsnp_id = rs_obj['refsnp_id']
            for merge_into in rs_obj['merged_snapshot_data']['merged_into']:
                f_out.write(f"{refsnp_id[0]}\t{refsnp_id}\t{merge_into}\n")
                for dbsnp1_merges in rs_obj['dbsnp1_merges']:
                    dbsnp1_merges = dbsnp1_merges['merged_rsid']
                    f_out.write(f"{dbsnp1_merges[0]}\t{dbsnp1_merges}\t{merge_into}\n")
            cnt += 1
#             if (cnt == 10 ):
#                 break

# sort txt file

# +
parsed_df = pd.read_csv(f'./merged_{version}.txt',sep='\t',names=[1,2,3])

parsed_df = parsed_df.sort_values([1,2])

parsed_df.to_csv(f'./merged_{version}.txt',sep='\t',index=False,header=False)
# -

# bgzip and create index

# !bgzip merged_b153.txt
# !tabix -C -s 1 -b 2 -e 2 merged_b153.txt.gz

# # Create position2snp and snp2position file

# Download VCF file of b153 (ftp://ftp.ncbi.nlm.nih.gov/snp/archive/b153/VCF/GCF_000001405.25.gz)

# split the multiallelic sites

# !bcftools norm GCF_000001405.38.gz -m - -O z -o GCF_000001405.38.nomultiallelic.gz

# count lines of header

n_header = 0
with gzip.open('./GCF_000001405.38.nomultiallelic.gz','rb') as f:
    for line in f:
        if line.decode('utf-8').startswith('##'):
            n_header += 1
        else:
            break

# - read every 100000 line
# - replace the name of #CHROM with 1..22
# - write to position2snp file (mode: add)
# - use the first int of rsid as the "chrom" and rsid as the "POS"
# - write to snp2position file (mode: add)

# create chrom name map dict

chr_name_map = pd.Series(data=list(range(1, 23)) + ['X', 'Y'],
                         index=check_output('tabix -l ./GCF_000001405.38.gz',
                                            shell=True).decode().split()[:24])

for df in pd.read_csv('./GCF_000001405.38.nomultiallelic.gz',
                      sep='\t',
                      skiprows=n_header,
                      compression='gzip',
                      usecols=['#CHROM', 'POS', 'ID', 'REF', 'ALT'],
                      chunksize=100000):
    # replace chr
    df['#CHROM'] = df['#CHROM'].map(chr_name_map)

    # remove chrM
    df = df.dropna()
    # stop when df are all chrM
    if len(df) == 0:
        break

    # use first int of rsid as fake chr
    df['rsid'] = df['ID'].map(lambda rsid: rsid[2:])
    df['rsid_1st'] = df['ID'].map(lambda rsid: rsid[2])

    # write pos2snp file
    df[['#CHROM', 'POS', 'ID', 'REF',
        'ALT']].to_csv(f'./pos2snp_{version}.txt',
                       sep='\t',
                       index=False,
                       header=False,
                       mode='a')
    # write snp2pos file
    df[['rsid_1st', 'rsid', '#CHROM', 'POS', 'REF',
        'ALT']].to_csv(f'./snp2pos_{version}_unsorted.txt',
                       sep='\t',
                       index=False,
                       header=False,
                       mode='a')

# !wc -l pos2snp_b153.txt
# !wc -l snp2pos_b153_unsorted.txt

# sort, bgzip, index

# +
# #!sort -k 1,1 -k 2,2n snp2pos_b153_unsorted.txt > snp2pos_b153.txt

# !bgzip snp2pos_b153.txt
# !bgzip pos2snp_b153.txt

# !tabix -s 1 -b 2 -e 2 pos2snp_b153.txt.gz
# !tabix -C -s 1 -b 2 -e 2 snp2pos_b153.txt.gz
# -

# query example

# !tabix pos2snp_b153.txt.gz 1:10019-10019
# !tabix snp2pos_b153.txt.gz 7:775809821-775809821


