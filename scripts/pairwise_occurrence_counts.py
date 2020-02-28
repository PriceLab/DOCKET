#!/bin/env python3

import argparse
import pandas as pd
import common.file_io as io
import common.enrichment as enrichment


def main(source_file, cl_members_file, counts_out_file):
    assert isinstance(source_file, str)

    # Load original data in json format
    data = io.load_json(source_file)
    data = pd.DataFrame(data)

    # Load cluster members and labels data
    cl_members_data = io.load_json(cl_members_file)

    # Get occurrence counts for all attributes and parent/children trios at all branch points in the cluster hierarchy
    all_occurrence_counts = {}
    for i in range(len(cl_members_data) - 1):
        parent_cnts, child1_cnts, child2_cnts = \
            enrichment.get_parent_child_occurrence_counts(str(i), data, cl_members_data)
        all_counts = {'parent': parent_cnts, 'child1': child1_cnts, 'child2': child2_cnts}
        all_occurrence_counts[str(i)] = all_counts

    # Write occurrence count data to file
    io.write_json(all_occurrence_counts, counts_out_file)


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='Original data file', default='cols_data.json.gz')
    parser.add_argument('--cluster_members', help='Cluster members file', default='cluster_members.json.gz')
    parser.add_argument('--counts_out', help='Output file for enrichment results',
                        default='pairwise_occurrence_counts.json.gz')
    args = parser.parse_args()

    main(args.source, args.cluster_members, args.counts_out)
