#!/bin/env python3

import argparse
import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as shc
from scipy.cluster.hierarchy import fcluster
import common.clustering as cluster
import common.file_io as io


def main(file,
         method='ward',
         criterion='distance',
         cl_labels_out='cluster_labels.txt.gz',
         cl_members_out='cluster_members.json.gz'):

    assert isinstance(file, str)

    # Load data to be clustered
    data = pd.read_table(file, index_col=0, header=None)

    # Normalize data down columns (i.e. features or attributes)
    data = (data - data.mean(axis=0)) / data.std(axis=0)

    # Use data index as labels
    labels = np.array(data.index)

    # Perform clustering
    linkage_table = shc.linkage(data.values, method=method)

    # Identify members of all clusters of size 2 or greater
    cluster_members = cluster.get_cluster_membership(linkage_table, labels)

    # Write cluster membership to file
    io.write_json(cluster_members, cl_members_out)

    # Generate a list of dendrogram cutoff values
    distances, num_distances = linkage_table[:, 2], len(linkage_table[:, 2])
    cutoff_values = [np.mean(distances[i: min(i+2, num_distances)]) for i in range(num_distances)]

    # Generate cluster assignments at different cutoff values
    cluster_assignments = [fcluster(linkage_table, c, criterion=criterion) for c in reversed(cutoff_values)]

    # Write cluster labels to file
    index = list(range(len(cluster_assignments)))
    cluster_assignments = pd.DataFrame(cluster_assignments, index=index, columns=labels)
    cluster_assignments.to_csv(cl_labels_out, sep='\t', index=True)

    return cluster_assignments


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='File to load')
    parser.add_argument('--method', help='Linkage method', default='ward')
    parser.add_argument('--criterion', help='Criterion to use in forming clusters', default='distance')
    parser.add_argument('--cl_labels_out', help='Output file for cluster labels', default='cluster_labels.txt.gz')
    parser.add_argument('--cl_members_out', help='Output file for cluster members', default='cluster_members.json.gz')
    args = parser.parse_args()

    main(args.source, args.method, args.criterion, cl_labels_out=args.cl_labels_out, cl_members_out=args.cl_members_out)
