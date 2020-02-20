#!/bin/env python3

import argparse
import pandas as pd
from sklearn.preprocessing import normalize
import scipy.cluster.hierarchy as shc
from scipy.cluster.hierarchy import fcluster


def main(file, method='ward', criterion='distance', out='cluster_hier_out.txt'):
    assert isinstance(file, str)

    # Load data to be clustered
    data = pd.read_table(file, index_col=0, header=None)

    # Use data index as labels
    labels = data.index

    # Get data as numpy array and normalize
    values = normalize(data.values)

    # Perform clustering
    linkage = shc.linkage(values, method=method)

    # Generate a list of dendrogram cutoff values
    cutoff_values = [int(100 * c) / 100 for c in linkage[:, 2]]

    # Generate cluster assignments at different cutoff values
    cluster_assignments = [fcluster(linkage, c, criterion=criterion) for c in cutoff_values]

    # Write data to file
    cluster_assignments = pd.DataFrame(cluster_assignments, index=cutoff_values, columns=labels)
    cluster_assignments.to_csv(out, sep='\t', index=True)

    return cluster_assignments


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='File to load')
    parser.add_argument('--method', help='Linkage method', default='ward')
    parser.add_argument('--criterion', help='Criterion to use in forming clusters', default='distance')
    parser.add_argument('--out', help='Output file for cluster results', default='cluster_hier_out.txt')
    args = parser.parse_args()

    main(args.source, args.method, args.criterion, out=args.out)
