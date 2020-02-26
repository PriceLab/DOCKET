#!/bin/env python3

import argparse
import pandas as pd
from scipy.stats import chi2_contingency
import common.file_io as io


def main(cl_attr_counts_file, cl_members_file):
    assert isinstance(cl_attr_counts_file, str)

    # Load occurrence counts for all attributes and parent/children trios at all branch points
    # in hierarchical clustering results
    occur_counts = io.load_json(cl_attr_counts_file)

    # Load cluster members data
    cl_members = io.load_json(cl_members_file)

    # Generate tables of enrichment results and write to file
    column_headings = ['cluster_level', 'cl1_count', 'cl2_count', 'attribute', 'chi2', 'p_value']
    for id_, data in occur_counts.items():
        # Get attribute value counts data for cluster pair
        cl1_counts = data['child1']
        cl2_counts = data['child2']

        # Get cluster members data for cluster pair
        cl1_members = cl_members[id_]['child1']
        cl2_members = cl_members[id_]['child2']
        total_members_count = len(cl1_members) + len(cl2_members)

        # Skip current cluster hierarchy level for low total members count
        if total_members_count < 50:
            continue

        enrich_results = []
        for attr, counts in cl1_counts.items():
            # For each cluster, get value counts for the current attribute
            current_cnts1 = counts
            current_cnts2 = cl2_counts[attr]

            # Convert to dataframe and replace empty string in index, if present
            counts_df = pd.DataFrame({f'{id_}.1': current_cnts1, f'{id_}.2': current_cnts2})
            counts_df.index = ['NA' if not s else s for s in counts_df.index]
            nrows, _ = counts_df.shape

            # Skip if there are not at least two rows (attribute values) for the given attribute
            if nrows < 2:
                continue

            chi2, p, dof, ex = chi2_contingency(counts_df)
            enrich_results.append([id_, len(cl1_members), len(cl2_members), attr, chi2, p])

        # If results are not empty, write to file
        if len(enrich_results) > 0:
            enrich_results = pd.DataFrame(enrich_results, columns=column_headings)
            enrich_results.sort_values(by='p_value', inplace=True)
            enrich_results.to_csv(f'enrich_results_{id_}.txt.gz', sep='\t', index=False)


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--counts_file', help='Attribute occurrence counts file',
                        default='pairwise_occurrence_counts.json.gz')
    parser.add_argument('--cluster_members', help='Cluster members file', default='cluster_members.json.gz')
    args = parser.parse_args()

    main(args.counts_file, args.cluster_members)
