#!/bin/env python3

import argparse
import json
import gzip
import pandas as pd
import numpy as np
pd.set_option('display.max_rows', None)
from scipy import stats

def load_json(file):
    if file.split('.')[-1] == 'gz':
        with gzip.GzipFile(file, 'r') as f:
            data = json.loads(f.read().decode('utf-8'))
    else:
        with open(file, 'r') as f:
            data = json.loads(f.read())
    return data


parser=argparse.ArgumentParser()
parser.add_argument('--infile', help='File to load')
parser.add_argument('--sep', help='Delimiter to use', default='\t')
parser.add_argument('--types_file', help='File with type counts')
parser.add_argument('--index_col', help='Index of column to use as row labels', default=None)
parser.add_argument('--header_row', help='Index of row to use as column labels', default=None)
parser.add_argument('--comment', help='Character to treat as comment signal', default='#')
args=parser.parse_args()

types = load_json(args.types_file)
cols = []

# select clearly numeric columns with at least 10 different values
for i in types:
    if i=='id': continue
    if 'NUM' in types[i] and not 'STR' in types[i] and types[i]['values']>=10:
        cols.append(i)

N = len(cols)

print("#numerical", N, sep="\t")
print('variableA', 'variableB', 'N', 'rho', 'pval', 'adjpval', sep="\t")

if N>1:
    tests = N*(N-1)/2
    
    if args.comment == '0':
        data = pd.read_csv(args.infile, sep=args.sep, usecols=cols, index_col=int(args.index_col), header=int(args.header_row), low_memory=False)
    else:
        data = pd.read_csv(args.infile, sep=args.sep, usecols=cols, index_col=int(args.index_col), header=int(args.header_row), comment=args.comment, low_memory=False)


    for i in range(len(cols)):
        colA = cols[i]
        if not colA in data: continue
        array_A = data[colA].values
        if len(array_A)>5 and len(set(array_A))>1:
            for j in range(i+1,len(cols)):
                colB = cols[j]
                if not colB in data: continue
                array_B = data[colB].values
                if len(array_B)>5 and len(set(array_B))>1:
                    temp_df = pd.DataFrame({'A':array_A, 'B':array_B })
                    temp_df = temp_df.replace(0,np.nan)
                    temp_df = temp_df.dropna()
                    rho, pval = stats.spearmanr(temp_df['A'].values, temp_df['B'].values)
                    if pval <= 0.01:
                        print(colA, colB, len(temp_df['A']), format(rho, '.3f'), format(pval, '.2e'), format(pval*tests, '.2e'), sep="\t")
                        #print(temp_df)
