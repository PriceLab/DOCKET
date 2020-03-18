#!/bin/env python3

import sys, argparse
import numpy as np
#from scipy import stats
#from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import gzip
#import brewer2mpl


parser=argparse.ArgumentParser()
parser.add_argument('infile', nargs='?', default=sys.stdin, help='File with PCA values')
parser.add_argument('outfile', nargs='?', default=sys.stdin, help='Where to save the plot')
parser.add_argument('--clustering', help='File with clustering information')
parser.add_argument('--clusters', help='Number of clusters to display', default=3)
parser.add_argument('--components', help='Number of components', default=2)
parser.add_argument('--c1', help='First component (x axis)', default=0)
parser.add_argument('--c2', help='Second component (y axis)', default=1)
args=parser.parse_args()
infile = args.infile
outfile = args.outfile
clustersfile = args.clustering
clusters = int(args.clusters)
c = int(args.components)
c1 = int(args.c1)
c2 = int(args.c2)

#colorset = brewer2mpl.get_map('Set2', 'qualitative', 8).mpl_colors

# read PCA
names = np.genfromtxt(fname = infile, dtype='str', usecols = range(0, 1))
Y = np.genfromtxt(fname = infile, dtype='float', usecols = range(1, c+1))

color = 'black'
# read clustering information if available
if clustersfile:
    with gzip.open(clustersfile, 'rb') as cf:
        ids = cf.readline().decode('utf8').strip()
        ids = ids[1:]
        ### the following will fail if there aren't enough clusters
        for i in range(int(clusters)-1):
            throwaway = cf.readline()
        clust = cf.readline().decode('utf8').strip()
        clust = clust.split('\t')
        color = clust[1:]
        
        ### the following assumes that the identifiers in the clustering are in the same order as in the PCA output file
        ### this seems to be true, but we should match names <-> ids to do this properly
        color = [float(c)/clusters for c in color]
        #color = [colorset[int(i)] for i in color]

# plot
tp = np.array(Y).transpose()
plt.figure()
if len(names)>3:
    plt.scatter(tp[c1],tp[c2],c=color,marker='o',s=7, edgecolor='black', facecolor=color, linewidth=0.15)

plt.savefig(outfile + '.png')
plt.savefig(outfile + '.pdf')
