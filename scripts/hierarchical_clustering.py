#!/bin/env python3

import argparse
import pandas as pd
from sklearn.preprocessing import normalize
import scipy.cluster.hierarchy as shc
from scipy.cluster.hierarchy import fcluster
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--source', help='File to load')
parser.add_argument('--method', default='ward', help='Linkage method')
parser.add_argument('--criterion', default='distance', help='The criterion to use informing clusters')
parser.add_argument('--linkage_out', default='hier_cluster_linkage.txt.gz', help='Clustering linkage table output file')
args = parser.parse_args()

# Load data to be clustered
data = pd.read_table(args.source, index_col=0, header=None)

# Use data index as labels
labels = data.index

# Get data as numpy array and normalize
values = data.values
#values = normalize(values)

# Perform clustering and write linkage table to output file
linkage_table = shc.linkage(values, method=args.method)
pd.DataFrame(linkage_table).to_csv(args.linkage_out, sep='\t', index=False, header=False)

# Generate a list of dendrogram cutoff values
distances, num_distances = linkage_table[:, 2], len(linkage_table[:, 2])
cutoff_values = [np.mean(distances[i: min(i+2, num_distances)]) for i in range(num_distances)]

# Generate cluster assignments at different cutoff values
cluster_assignments = [fcluster(linkage_table, c, criterion=args.criterion) for c in reversed(cutoff_values)]

# Write results to stdout
index = list(range(len(cluster_assignments)))
cluster_assignments = pd.DataFrame(cluster_assignments, index=index, columns=labels)
print(cluster_assignments.to_csv(sep='\t', index=True))
