#!/bin/env python3

import argparse
import pandas as pd
from sklearn.preprocessing import normalize
import scipy.cluster.hierarchy as shc
from scipy.cluster.hierarchy import fcluster


def main(file, out='cluster_hier_out.txt'):
    assert isinstance(file, str)

    # Load data from .json or .json.gz file
    data = pd.read_json(file)

    # Use column headers as labels
    labels = data.columns

    # Get data as numpy array and transpose
    values = data.values.transpose()

    # Normalize the data
    values = normalize(values)

    # Perform clustering
    linkage = shc.linkage(values, method='ward')

    # Generate a list of dendrogram cutoff values
    cutoff_values = [int(100 * c) / 100 for c in linkage[:, 2]]

    # Generate cluster assignments at different cutoff values
    cluster_assignments = [fcluster(linkage, c, criterion='distance') for c in cutoff_values]

    # Write data to file
    cluster_assignments = pd.DataFrame(cluster_assignments, index=cutoff_values, columns=labels)
    cluster_assignments.to_csv(out, sep='\t', index=True)

    return cluster_assignments


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='File to load')
    parser.add_argument('--out', help='Output file for cluster results', default='cluster_hier_out.txt')
    args = parser.parse_args()

    main(args.source, out=args.out)
