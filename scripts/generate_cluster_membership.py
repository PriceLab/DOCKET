#!/bin/env python3

import argparse
import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as shc
from scipy.cluster.hierarchy import fcluster
import common.clustering as cluster
import common.file_io as io


def main(file,
         link_table_in='rows_hier_linkage.txt.gz',
         cl_members_out='cluster_members.json.gz'):

    assert isinstance(file, str)

    # Load original data
    data = pd.read_table(file, index_col=0, header=None)

    # Use data index as labels
    labels = np.array(data.index)

    # Load hierarchical clustering linkage table
    linkage_table = pd.read_table(link_table_in, index_col=False, header=None)

    # Identify members of all clusters of size 2 or greater
    cluster_members = cluster.get_cluster_membership(linkage_table.values, labels)

    # Write cluster membership to file
    io.write_json(cluster_members, cl_members_out)
    
    return cluster_members


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='File to load')
    parser.add_argument('--link_table_in', help='Hierarchical clustering linkage table', default='hier_linkage.txt.gz')
    parser.add_argument('--cl_members_out', help='Output file for cluster members', default='cluster_members.json.gz')
    args = parser.parse_args()

    main(args.source, args.link_table_in, cl_members_out=args.cl_members_out)
