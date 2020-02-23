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
args = parser.parse_args()

# Load data to be clustered
data = pd.read_table(args.source, index_col=0, header=None)

# Use data index as labels
labels = data.index

# Get data as numpy array and normalize
values = normalize(data.values)

# Perform clustering
linkage = shc.linkage(values, method=args.method)

# Generate a list of dendrogram cutoff values
distances, num_distances = linkage[:, 2], len(linkage[:, 2])
cutoff_values = [np.mean(distances[i: min(i+2, num_distances)]) for i in range(num_distances)]
cutoff_values = np.unique(cutoff_values)

# Generate cluster assignments at different cutoff values
cluster_assignments = [fcluster(linkage, c, criterion=args.criterion) for c in reversed(cutoff_values)]

# Write results to stdout
index = list(range(len(cluster_assignments)))
cluster_assignments = pd.DataFrame(cluster_assignments, index=index, columns=labels)
print(cluster_assignments.to_csv(sep='\t', index=True))
