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

import pandas as pd
import numpy as np
import time,sys,os,tabix
from subprocess import check_output
from multiprocessing import Pool,Manager

merge_tabix = '/f/jianhua/rs2pos/b153/merged_b153.txt.gz'
rs2pos_tabix = '/f/jianhua/rs2pos/b153/snp2pos_b153.txt.gz'
pos2rs_tabix = '/f/jianhua/rs2pos/b153/pos2snp_b153.txt.gz'


def rsid2position_alleles(rsid):
    '''
    check whether the rsid was merged into other rsid
    If rsID was merged into multiple rsIDs, use the first one (i.e. rs1448824014).
    query hg19 coordinate and alleles
    Use the first alternative allele for multiallelic sites.
    
    >>> rsid2position_alleles('rs4728142')
    >>> ['7', '128573967', 'G', 'A']
    '''
    merge_out = check_output(
        f'tabix {merge_tabix} {rsid[2]}:{rsid[2:]}-{rsid[2:]}', shell=True)
    if merge_out == b'':
        merged_rsid = rsid[2:]
    else:
        merged_rsid = merge_out.decode().split()[-1]

    rs2pos_out = check_output(
        f'tabix {rs2pos_tabix} {merged_rsid[0]}:{merged_rsid}-{merged_rsid}',
        shell=True)
    if rs2pos_out == b'':
        return [np.nan] * 4
    else:
        return rs2pos_out.decode().split()[2:6]


def position2_rsid_alleles(chrom,pos):
    '''
    query by hg19 coordinate and get rsid, ref, alt
    use the first record for multiallelic sites, for example, chr7:24944757
    
    >>> position2_rsid_alleles('chr7',24944757)
    >>> ['rs132', 'T', 'A']
    '''
    if str(chrom).startswith('chr'):
        chrom = chrom[3:]
    
    pos2rs_out = check_output(f'tabix {pos2rs_tabix} {chrom}:{pos}-{pos}',shell=True)
    if pos2rs_out == b'':
        return [np.nan] * 3
    else:
        return pos2rs_out.decode().split()[2:5]


def fill_all(chrom,pos,rsid,ref,alt):
    '''
    fill the missing value in chrom,pos,rsid,ref,alt according to the known one(s).
    
    '''
    daying


position2_rsid_alleles(1,1118275)


