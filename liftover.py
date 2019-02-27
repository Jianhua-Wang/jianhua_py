#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
from pyliftover import LiftOver
import sys,argparse,time,os
from multiprocessing import Pool,Manager

# define arguments
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
    parser.add_argument('--withchr', action='store_true', help='exist when chromosome of input starts with chr, and output starts with chr, either')
    parser.add_argument('--gzip', action='store_true', help='exist when input is .gz file, but output text file, still')
    parser.add_argument('--headless', action='store_true', help='exist when input is headless file, and output headless file, either')

    args = parser.parse_args()
    return args
args = parseArguments()

# for .gz file
if args.gzip:
    gzip = 'gzip'
else:
    gzip = None

# define old to new
lo = LiftOver(args.old, args.new)

# define separator
if args.sep == 'table':
    sep = '\t'
else:
    sep = ','

# for headless file
if args.headless:
    demo = pd.read_csv(args.input,sep=sep,dtype=str,nrows=10,compression=gzip)
    names = [str(x) for x in range(len(demo.columns))]
else:
    names = None

# convert genome build of single site (without chr), if no result return ['na','na']
def lift_single_site_without_chr(old_chr,old_pos):
    old_chr = 'chr{}'.format(old_chr)
    old_pos = int(old_pos)
    lift = lo.convert_coordinate(old_chr, old_pos)
    if len(lift) == 0:
        return ['na','na']
    else:
        new_chr = lift[0][0][3:]
        new_pos = int(lift[0][1])
        return [new_chr,new_pos]

# convert genome build of single site (with chr), if no result return ['na','na']
def lift_single_site_with_chr(old_chr,old_pos):
    old_pos = int(old_pos)
    lift = lo.convert_coordinate(old_chr, old_pos)
    if len(lift) == 0:
        return ['na','na']
    else:
        new_chr = lift[0][0][3:]
        new_pos = int(lift[0][1])
        return ['chr{}'.format(new_chr),new_pos]

# convert genome build of whole dataframe, return dataframe without failed sites
def run(data,i):
    if args.withchr:
        data.iloc[:,[args.chr,args.pos]] = [lift_single_site_with_chr(data.loc[x][args.chr],data.loc[x][args.pos]) for x in data.index]
    else:
        data.iloc[:,[args.chr,args.pos]] = [lift_single_site_without_chr(data.loc[x][args.chr],data.loc[x][args.pos]) for x in data.index]
    leng = len(data) 
    data = data[data.iloc[:,args.chr]!='na']
    list1[0] += len(data)
    list1[1] += (leng-len(data))
    print('\rSuccessful converted: {:,}    Failed: {:,}'.format(list1[0],list1[1]),end='')
    sys.stdout.flush()
    return data

if __name__ == '__main__':
    unlifted_file = args.input
    lifted_file = args.output
    if os.path.exists(lifted_file):
        os.remove(lifted_file)
    unlifted = pd.read_csv(unlifted_file,sep=sep,dtype=str,chunksize=10000,compression=gzip,names=names)
    start = time.time()
    print('\nOriginal Build: {}\tNew Build: {}\tThread: {}\n'.format(args.old,args.new,args.thread))
    # start process pool
    res = []
    manager = Manager()
    list1 = manager.list([0,0])
    p = Pool(args.thread)
    for i,data in enumerate(unlifted):
        res.append(p.apply_async(run,(data,i,)))
    p.close()
    p.join()

    print('\nWriting result to {}...'.format(args.output))
    total = len(res)
    for i,df in enumerate(res):
        if args.headless:
            header = 0
        else:
            header = i+1 == True
        df.get().to_csv(args.output,index=False,sep=sep,header=header,mode='a')
        sys.stdout.write('\rComplete {:.2f}%'.format((i+1)/total*100))
        sys.stdout.flush()
    end = time.time() 
    print('\n\nTotal: {:,}\tSucceeded: {:,}\tFailed: {:,}\tIn: {:.2f}s.'.format(list1[0]+list1[1],list1[0],list1[1],end-start))
    print('Have a nice day! :)')