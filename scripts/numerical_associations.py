#!/bin/env python3

import argparse
import common.file_io as io
import pandas as pd
import numpy as np
pd.set_option('display.max_rows', None)
from scipy import stats

parser=argparse.ArgumentParser()
parser.add_argument('--infile', help='File to load')
parser.add_argument('--sep', help='Delimiter to use', default='\t')
parser.add_argument('--types_file', help='File with type counts')
parser.add_argument('--index_col', help='Index of column to use as row labels', default=0)
parser.add_argument('--header_row', help='Index of row to use as column labels', default=0)
args=parser.parse_args()

types = io.load_json(args.types_file)
cols = []

# select clearly numeric columns with at least 10 different values
for i in types:
    if i=='id': continue
    if 'NUM' in types[i] and not 'STR' in types[i] and types[i]['values']>=10:
        cols.append(i)

N = len(cols)
pairs = []
tests_done = 0

if N>1:
    data = pd.read_csv(args.infile, sep=args.sep, usecols=cols, index_col=int(args.index_col), header=int(args.header_row), comment=None, low_memory=False)

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
                    tests_done = tests_done + 1
                    if pval <= 0.05:
                        blob = {'A': colA, 'B': colB, 'N': len(temp_df['A']), 'rho': format(rho, '.3f'), 'pval': pval}
                        pairs.append(blob)

print("#numerical", N, sep="\t")
print("#tests_done", tests_done, sep="\t")
print('variableA', 'variableB', 'N', 'rho', 'pval', sep="\t")

significant = []
for pair in pairs:
    corrected = pair['pval']*tests_done
    if corrected <= 0.05:
        pair['pval'] = format(corrected, '.2e')
        significant.append(pair)
        print(pair['A'], pair['B'], pair['N'], pair['rho'], pair['pval'], sep="\t")

result = {'relationship': 'is_correlated_to', 'test_type': 'Spearman correlation', 'correction': 'Bonferroni', 'numerical_columns': N, 'tests_done': tests_done, 'tests_passed': len(significant), 'tests': significant}
io.write_json(result, 'num_assoc.json.gz')

