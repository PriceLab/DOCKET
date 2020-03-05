#!/bin/env python3

import argparse
import json
import gzip
import pandas as pd
import numpy as np
from collections import Counter
import math
pd.set_option('display.max_rows', None)
from scipy import stats as ss

def load_json(file):
    if file.split('.')[-1] == 'gz':
        with gzip.GzipFile(file, 'r') as f:
            data = json.loads(f.read().decode('utf-8'))
    else:
        with open(file, 'r') as f:
            data = json.loads(f.read())
    return data

def conditional_entropy(x,y):
    # entropy of x given y
    y_counter = Counter(y)
    xy_counter = Counter(list(zip(x,y)))
    total_occurrences = sum(y_counter.values())
    entropy = 0
    for xy in xy_counter.keys():
        p_xy = xy_counter[xy] / total_occurrences
        p_y = y_counter[xy[1]] / total_occurrences
        ratio = p_y/p_xy
        if ratio>0:
            entropy += p_xy * math.log(p_y/p_xy)
    return entropy

def theil_u(x,y):
    s_xy = conditional_entropy(x,y)
    x_counter = Counter(x)
    total_occurrences = sum(x_counter.values())
    p_x = list(map(lambda n: n/total_occurrences, x_counter.values()))
    s_x = ss.entropy(p_x)
    if s_x == 0:
        return 1
    else:
        return (s_x - s_xy) / s_x

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
# select categorical columns with at least two but no more than ten different values
# at least ten rows must have a non-null value
for i in sorted(types.keys()):
    if types[i]['values']<2 or types[i]['values']>10: continue
    if 'STR' in types[i]:
        if 'NUM' in types[i]:
            if types[i]['STR']+types[i]['NUM']>=10:
                cols.append(i)
        elif types[i]['STR']>=10:
            cols.append(i)
    elif 'NUM' in types[i] and types[i]['NUM']>=10:
        cols.append(i)

print("#categorical",len(cols),sep="\t")
print('variableA', 'variableB', 'N', 'Theil_B_A', 'Theil_A_B', sep="\t")

if cols:
    if args.comment == '0':
        data = pd.read_csv(args.infile, sep=args.sep, usecols=cols, index_col=int(args.index_col), header=int(args.header_row), low_memory=False)
    else:
        data = pd.read_csv(args.infile, sep=args.sep, usecols=cols, index_col=int(args.index_col), header=int(args.header_row), comment=args.comment, low_memory=False)


    for i in range(len(cols)):
        varA = cols[i]
        if not varA in data: continue
        for j in range(i+1,len(cols)):
            varB = cols[j]
            if not varB in data: continue
            trim = pd.DataFrame({'A': data[varA].values, 'B': data[varB].values}).dropna()
            if len(trim['A'])<10: continue
            theil_B_given_A = theil_u(trim['A'],trim['B'])
            theil_A_given_B = theil_u(trim['B'],trim['A'])
        
            if theil_B_given_A>=0.5 and theil_A_given_B>=0.5:
                print(varA, varB, len(trim['A']), \
                    format(theil_B_given_A, '.3f'), \
                    format(theil_A_given_B, '.3f'), \
                    sep="\t")
            
