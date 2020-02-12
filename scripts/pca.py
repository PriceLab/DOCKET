#!/bin/env python3

import sys, argparse
import numpy as np
from scipy import stats
from sklearn.decomposition import PCA

parser=argparse.ArgumentParser()
parser.add_argument('file', nargs='?', default=sys.stdin, help='File with data')
parser.add_argument('--L', help='Fingerprint length')
parser.add_argument('--components', help='Number of components', default=10)
parser.add_argument('--skip', help='Number of columns to skip', default=2)
args=parser.parse_args()
file = args.file
L = int(args.L)
c = int(args.components)
skip = int(args.skip)

# read fingerprints
#X = np.loadtxt(fname = file, usecols = range(skip, L+skip))
names = np.genfromtxt(fname = file, dtype='str', usecols = range(0, 1))
X = np.genfromtxt(fname = file, dtype='float', usecols = range(skip, L+skip))

# normalize raw fingerprints
for i in range(0, len(X)):
    X[i] = stats.zscore(X[i])

# compute PCA
if c>L:
    c = L
if c>len(names):
    c = len(names)
pca = PCA(n_components=c)
pca.fit(X)
Y = pca.transform(X)

#out = pca.explained_variance_ratio_
#out = np.insert(out, 0, np.sum(out))
#print('\t'.join([str(x) for x in out]))

# spill out
for i in range(0, len(names)):
    #line = '\t'.join([str(x) for x in Y[i]])
    line = '\t'.join(["{:.4f}".format(x) for x in Y[i]])
    print(names[i]+'\t'+line)
