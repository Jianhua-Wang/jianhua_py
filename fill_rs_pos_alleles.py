
# coding: utf-8

import pandas as pd
import numpy as np
import time,sys,os
from subprocess import check_output
from multiprocessing import Pool,Manager

def print_logo():
    logo = '''
==================================================================
     \033[1;33m/\\\033[0m
    \033[1;33m/__\\\033[0m\033[1;31m\\\033[0m            This is a python script for zzy's QTL Database
   \033[1;33m/\033[0m  \033[1;31m---\\\033[0m           Author: Jianhua Wang
  \033[1;33m/\\\033[0m      \033[1;31m\\\033[0m          Date:   04-05-2019
 \033[1;33m/\033[0m\033[1;32m/\\\033[0m\033[1;33m\\\033[0m     \033[1;31m/\\\033[0m
 \033[1;32m/  \   /\033[0m\033[1;31m/__\\\033[0m
\033[1;32m`----`-----\033[0m
==================================================================
    '''
    print(logo)

def rs2pos(rsid):
    out = check_output('tabix {} {}:{}-{}'.format(rs_data, rsid[2], rsid[2:], rsid[2:]),shell=True).decode().strip().split()[2:]
    if len(out) == 0:
        return [np.nan,np.nan,np.nan,np.nan,]
    else:
        return out


def pos2rs(chr_id, pos):
    out = check_output('tabix {} {}:{}-{}'.format(pos_data, chr_id[3:], pos, pos),shell=True).decode().strip().split()[2:]
    if len(out) == 0:
        return [np.nan,np.nan,np.nan,]
    else:
        return out[:3]

def rsmerge(rsid):
    out = check_output('tabix {} {}:{}-{}'.format(merge_data, rsid[2], rsid[2:], rsid[2:]),shell=True).decode().strip().split()
    if len(out) == 0:
        return rsid
    else:
        return 'rs{}'.format(out[2])


def fill_df(df):
    for i in df.index:
        if df.loc[i, [chr_col, pos_col, rsid_col, ref_col, alt_col]].notnull(
        ).values.all():
            continue
        elif pd.notnull(df.loc[i, rsid_col]):
            if df.loc[i, rsid_col].startswith('rs'):
                df.at[i, rsid_col] = rsmerge(df.loc[i, rsid_col])
                chr_name, pos, ref, alt = rs2pos(df.loc[i, rsid_col])
                df.at[i, [chr_col, pos_col, ref_col, alt_col]] = 'chr{}'.format(chr_name), pos, ref, alt
            else:
                df.at[i, rsid_col] = np.nan
        elif df.loc[i, [chr_col, pos_col]].notnull().values.all():
            df.at[i, [rsid_col, ref_col, alt_col]] = pos2rs(*df.loc[i, [chr_col, pos_col]])
        else:
            continue
    leng = len(df)
    df = df.dropna(subset=[chr_col, pos_col, rsid_col, ref_col, alt_col])
    stdout[0] += len(df)
    stdout[1] += (leng-len(df))
    print('\rSuccessful converted: {:,}    Failed: {:,}'.format(*stdout),end='')
    sys.stdout.flush()
    return df


if __name__ == '__main__':
    print_logo()
    rs_data = '/home/jianhua/rs2pos/rsis2pos_sort.txt.gz'
    pos_data = '/home/jianhua/rs2pos/pos2rsid.txt.gz'
    merge_data = '/home/jianhua/rs2pos/merge_sort.txt.gz'
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    # chr_col, pos_col, rsid_col, ref_col, alt_col = '0','1','2','3','4'
    chr_col, pos_col, rsid_col, ref_col, alt_col = 'Marker_Chr','Marker_Position','Marker_Name','A1','A2'

    start = time.time()
    raw = pd.read_csv(input_path,sep='\t',dtype=str,chunksize=10)
    # start process pool
    res = []
    manager = Manager()
    stdout = manager.list([0,0])
    p = Pool(20)
    for data in raw:
        res.append(p.apply_async(fill_df,(data,)))
    p.close()
    p.join()

    print('\nWriting result to {}...'.format(output_path))
    total = len(res)
    if os.path.exists(output_path):
        print('Output file exists, delete it!')
        os.remove(output_path)

    for i,df in enumerate(res):
        if i == 0:
            df.get().fillna('NA').to_csv(output_path,index=False,sep='\t',header=True,mode='a')
        else:
            df.get().fillna('NA').to_csv(output_path,index=False,sep='\t',header=False,mode='a')
        sys.stdout.write('\rComplete {:.2f}%'.format((i+1)/total*100))
        sys.stdout.flush()
    end = time.time()
    print('\n\nTotal: {:,}\tSucceeded: {:,}\tFailed: {:,}\tIn: {:.2f}s.'.format(stdout[0]+stdout[1],stdout[0],stdout[1],end-start))
    print('Have a nice day! :)')
