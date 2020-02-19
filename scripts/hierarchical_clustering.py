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

# Load data from .json or .json.gz file
data = pd.read_table(args.source, index_col=0, header=None).T

# Use column headers as labels
labels = data.columns

# Get data as numpy array and transpose
values = data.values.transpose()

# Normalize the data
values = normalize(values)

# Perform clustering
linkage = shc.linkage(values, method=args.method)

# Generate a list of dendrogram cutoff values
cutoff_values = [int(100 * c) / 100 for c in linkage[:, 2]]
cutoff_values = np.unique(cutoff_values)

# Generate cluster assignments at different cutoff values
cluster_assignments = [fcluster(linkage, c, criterion=args.criterion) for c in reversed(cutoff_values)]

# Write results to stdout
cluster_assignments = pd.DataFrame(cluster_assignments, index=cutoff_values, columns=labels)
print(cluster_assignments.to_csv(sep='\t', index=True))
