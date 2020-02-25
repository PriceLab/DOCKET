#!/bin/env python3

import argparse
import pandas as pd
import common.file_io as io
import common.enrichment as enrich


def main(attr_data_file,
         attr_counts_file,
         cluster_data_file,
         out='rows_enrichment.txt',
         filter_frac=0.1,
         resample_size=50):

    assert isinstance(attr_data_file, str)
    assert isinstance(attr_counts_file, str)
    assert isinstance(cluster_data_file, str)

    # Load attribute value counts data (provides occurrence counts for all attributes)
    attr_counts_data = io.load_json(attr_counts_file)

    # Get only attributes and attribute values for which there are sufficient data
    columns = ['attribute', 'attribute_value', 'count', 'fraction']
    attributes_for_enrichment = enrich.get_attributes_for_enrichment(attr_counts_data, filter_frac)
    attributes_for_enrichment = pd.DataFrame(attributes_for_enrichment, columns=columns).set_index(columns[:2])

    # Get the original, raw attributes data for analysis
    attr_data = pd.read_json(attr_data_file)

    # Make sure that headers and row indexes are strings
    attr_data.index = [str(lab) for lab in attr_data.index]
    attr_data.columns = [str(lab) for lab in attr_data.columns]

    # Keep only columns for which there are sufficient data
    columns_to_keep = attributes_for_enrichment.index.get_level_values(0).unique()
    attr_data = attr_data[columns_to_keep]

    # Get labels for non-numeric columns
    non_numeric_column_labels = list(attr_data.select_dtypes('object').columns)

    # Transform non-numeric columns by making lowercase and replacing white space
    for label in non_numeric_column_labels:
        attr_data[label] = attr_data[label].apply(lambda x: '-'.join(x.lower().split()))

    results = enrich.get_enrichment_scores(attributes_for_enrichment, columns_to_keep, attr_data, cluster_data_file,
                                           resample_size, filter_fraction=filter_frac)
    results.to_csv(out, sep='\t')


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--attr_data', help='Attributes data file', default='cols_attribute_data.json.gz')
    parser.add_argument('--attr_counts', help='Attribute counts file', default='cols_attribute_counts.json.gz')
    parser.add_argument('--cluster_data', help='Clusters file', default='rows_hier_clusters.txt')
    parser.add_argument('--out', help='Output file for enrichment results', default='rows_enrichment.txt')
    args = parser.parse_args()

    main(args.attr_data,
         attr_counts_file=args.attr_counts,
         cluster_data_file=args.cluster_data,
         out=args.out)
