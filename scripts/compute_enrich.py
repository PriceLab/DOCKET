#!/bin/env python3

import argparse
import pandas as pd
import common.file_io as io
import common.enrichment as enrich


def main(data_file, hist_file, cluster_file, out='enrichment_out.txt', filter_frac=0.1, resample_size=50):
    assert isinstance(data_file, str)
    assert isinstance(hist_file, str)
    assert isinstance(cluster_file, str)

    # Load histogram data (provides occurrence counts for all attributes)
    hist_data = io.load_json(hist_file)

    # Get only attributes and attribute values for which there are sufficient data
    columns = ['attribute', 'attribute_value', 'count', 'fraction']
    attributes_for_enrichment = enrich.get_attributes_for_enrichment(hist_data, filter_frac)
    attributes_for_enrichment = pd.DataFrame(attributes_for_enrichment, columns=columns).set_index(columns[:2])

    # Get the original, raw data for analysis
    cols_data = pd.read_json(data_file)

    # Keep only columns for which there are sufficient data
    columns_to_keep = attributes_for_enrichment.index.get_level_values(0).unique()
    cols_data = cols_data[columns_to_keep]

    # Get labels for non-numeric columns
    non_numeric_column_labels = list(cols_data.select_dtypes('object').columns)

    # Transform non-numeric columns by making lowercase and replacing white space
    for label in non_numeric_column_labels:
        cols_data[label] = cols_data[label].apply(lambda x: '-'.join(x.lower().split()))

    # Get cluster assignments for individuals
    cl_assignments = pd.read_csv(cluster_file, sep='\t', index_col=0)
    cl_assignments = cl_assignments.values[-10:].tolist()
    cl_assignments.reverse()

    # Get list of clusters that are within a specified size range
    clusters = [enrich.to_cluster_id(i, cl, cnt) for i, cl_list in enumerate(cl_assignments)
                for cl, cnt in pd.Series(cl_list).value_counts().sort_index().items()
                if enrich.in_range(cnt, len(cl_list), filter_frac)]
    clusters = enrich.remove_repeat_clusters(clusters, cl_assignments)

    # Calculate enrichment on each attribute
    enrichment_results = []
    for attr in columns_to_keep:
        # Get attribute values associated with the current attribute
        attr_values = attributes_for_enrichment.loc[attr, :].index

        # Get the fractional occurrence of attribute values in each cluster
        attr_data = cols_data[attr]
        attr_value_counts, attr_value_fractions = enrich.get_cluster_attribute_fractions(
            attr_data, attr_values, cl_assignments, clusters)

        # For current attribute, calculate enrichment over all clusters
        for cl in clusters:
            # Parse cluster string id
            cl_grp, cl_id, cl_cnt = enrich.parse_cluster_id(cl)

            cl_resample = enrich.get_resample_fractions(cl, attr_data, attr_values, resample_size)

            for attr_val in attr_values:
                # Get stats on attribute value occurrence in entire data set
                count_in_full_dataset = attributes_for_enrichment.loc[attr, attr_val]['count']
                fraction_in_full_dataset = attributes_for_enrichment.loc[attr, attr_val]['fraction']

                # Get stats on attribute value occurrence in cluster
                cnt_with_attr_val = attr_value_counts[cl][attr_val]
                frac_with_attr_val = attr_value_fractions[cl][attr_val]

                # Get quantile of observed occurrence fraction
                fraction_rank = enrich.get_sorted_position(frac_with_attr_val, cl_resample[attr_val])
                fraction_quantile = fraction_rank / resample_size

                # Store results as a data frame
                current_results = [
                    f'{cl_grp}.{cl_id}',  # Cluster identifier (e.g. 0.1)
                    attr,  # Attribute (e.g. sex)
                    attr_val,  # Attribute value (e.g. male, female)
                    count_in_full_dataset,  # Count in full data set
                    fraction_in_full_dataset,  # Fraction in full data set
                    cl_cnt,   # Count of members within cluster
                    cnt_with_attr_val,  # Count in cluster with attribute value
                    frac_with_attr_val,  # Fraction in cluster with attribute value
                    fraction_quantile  # Quantile of observed occurrence fraction
                ]
                print(current_results)
                enrichment_results.append(current_results)

    columns = ['cluster_id', 'attribute', 'attribute_value', 'total_count', 'total_fraction',
               'cluster_count', 'attr_value_count', 'attr_value_fraction', 'quantile']
    return pd.DataFrame(enrichment_results, columns=columns)


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--data', help='Data file', default='cols_data.json.gz')
    parser.add_argument('--hist', help='Histograms file', default='cols_hist.json.gz')
    parser.add_argument('--cluster', help='Clusters file', default='rows_hier_clusters.txt')
    parser.add_argument('--out', help='Output file for enrichment results', default='enrichment_out.txt')
    args = parser.parse_args()

    main(args.data, hist_file=args.hist, cluster_file=args.cluster)
