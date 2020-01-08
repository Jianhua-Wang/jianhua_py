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
from pyliftover import LiftOver
import sys, argparse, time, os
from multiprocessing import Pool


def lift_single_site(old_chr_old_pos):
    old_chr,old_pos = old_chr_old_pos
    new_coordinates = [np.nan,np.nan]
    if str(old_chr).startswith('chr'):
        lift = lo.convert_coordinate(old_chr, old_pos)
        if len(lift) != 0:
            new_chr = lift[0][0]
            new_pos = int(lift[0][1])
            new_coordinates = [new_chr,new_pos]
    else:
        old_chr = f'chr{old_chr}'
        lift = lo.convert_coordinate(old_chr, old_pos)
        if len(lift) != 0:
            new_chr = lift[0][0][3:]
            new_pos = int(lift[0][1])
            new_coordinates = [new_chr,new_pos]
    return new_coordinates


def main():
    start = time.time()
    if args.gzip:
        gzip = 'gzip'
    else:
        gzip = None

    # define old to new
    global lo
    lo = LiftOver(args.old, args.new)

    # define separator
    if args.sep == 'table':
        sep = '\t'
    else:
        sep = ','

    if os.path.exists(args.output):
        print(f'Output file exists, overwrite it.')
        os.remove(args.output)
    
    print(f'\nOriginal Build: {args.old}\tNew Build: {args.new}\tThread: {args.thread}\n')
    succeed, total = 0,0
    demo = pd.read_csv(args.input,sep=sep,dtype=str,nrows=1,compression=gzip)
    if args.headless:
        names = [str(x) for x in range(len(demo.columns))]
        chr_id,bp = names[args.chr],names[args.pos]
    else:
        names = None
        write_header = open(args.output,'w')
        write_header.write(f'{args.sep}'.join(demo.columns)+'\n')
        write_header.close()
        chr_id,bp = demo.columns[args.chr],demo.columns[args.pos]

    for df in pd.read_csv(args.input,sep=sep,chunksize=10000,compression=gzip):
        p = Pool(args.thread)
        df[[chr_id,bp]] = p.map(lift_single_site,df[[chr_id,bp]].values)
        p.close()
        total += len(df)
        df = df.dropna(subset=[chr_id,bp])
        succeed += len(df)
        df = df.astype({chr_id:str,bp:int})
        df.to_csv(args.output,sep=sep,index=False,mode='a',header=False)
        print(f'\rSucceed: {succeed :,}\t\tFailed: {total-succeed :,}',end='')
        sys.stdout.flush()
    end = time.time()
    print(f'\rTotal: {total :,}\tSucceed: {succeed :,}\tFailed: {total-succeed :,}\tIn: {end-start :.2f}s')
    print('Have a nice day! :)')


def print_logo():
    logo = '''
========================================================================
     \033[1;33m/\\\033[0m
    \033[1;33m/__\\\033[0m\033[1;31m\\\033[0m            Convert Genome Build of Summary Statistics
   \033[1;33m/\033[0m  \033[1;31m---\\\033[0m           
  \033[1;33m/\\\033[0m      \033[1;31m\\\033[0m          Author: Jianhua Wang
 \033[1;33m/\033[0m\033[1;32m/\\\033[0m\033[1;33m\\\033[0m     \033[1;31m/\\\033[0m         Date:   01-07-2020
 \033[1;32m/  \   /\033[0m\033[1;31m/__\\\033[0m
\033[1;32m`----`-----\033[0m
========================================================================
    '''
    print(logo)


def parseArguments():
    parser = argparse.ArgumentParser(usage="conver genome build of txt or csv file, require pyliftover",description="python liftover.py -c 0 -p 1 test.txt test_lifted.txt",)
    parser.add_argument('input', type=str, help='input unlifted file'),
    parser.add_argument('output', type=str, help='output lifted file'),
    parser.add_argument('-c','--chr', type=int, help='colunm positon of chromosome (0-based), default=0',default=0,metavar=''),
    parser.add_argument('-p','--pos', type=int, help='colunm positon of base pair (0-based), default=1',default=1,metavar=''),
    parser.add_argument('-o','--old', type=str, choices=['hg17','hg18','hg19','hg38'], help='Genome Build of input file, choose from [hg17,hg18,hg19,hg38], default=hg19',default='hg19',metavar='')
    parser.add_argument('-n','--new', type=str, choices=['hg17','hg18','hg19','hg38'], help='Genome Build of output file, choose from [hg17,hg18,hg19,hg38], default=hg38',default='hg38',metavar='')
    parser.add_argument('-s','--sep', type=str, choices=['table','comma'], help='separator of input file, choose from [table,comma], default=table',default='table',metavar='')
    parser.add_argument('-t','--thread', type=int, help='threads you want to run, default=20',default=20,metavar='')
#     parser.add_argument('--withchr', action='store_true', help='exist when chromosome of input starts with chr, and output starts with chr, either')
    parser.add_argument('--gzip', action='store_true', help='exist when input is .gz file, but output text file, still')
    parser.add_argument('--headless', action='store_true', help='exist when input is headless file, and output headless file, either')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    print_logo()
    args = parseArguments()
    main()
