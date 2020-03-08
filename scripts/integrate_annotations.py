#!/bin/env python3

import argparse
import pandas as pd
import common.integration as integrate
import common.file_io as io


# Takes two files, one containing drug/mutation sensitivity associations and one containing drug annotations.
def main(associations_file=None,
         annotations_file=None,
         base_directory=None,
         configuration_file=None,
         config_base_directory=None,
         annotations_out='mutation_drug_pairs_annotated.csv',
         enrichment_out='mutation_drug_pair_enrichment.csv'):

    # Load drug/mutation sensitivity associations and drug annotations data
    associations_data = pd.read_csv(associations_file, index_col=None)
    annotations_data = pd.read_csv(annotations_file, index_col=0)

    # Load configuration data for drug annotations
    config = io.load_json(configuration_file)

    # Merge annotations with associations data and write to file
    annotated_data = integrate.merge_annotations(associations_data, annotations_data, config)
    annotated_data.to_csv(annotations_out, index=False)

    # Compute enrichment scores
    enrich_config = config['enrichment']
    f1, f2 = enrich_config['feature1'], enrich_config['feature2']
    enrichment_scores = integrate.compute_enrichment_all(annotated_data, f1, f2, threshold=0.05)

    # Eliminate poor enrichment scores
    high_p_val_res = enrichment_scores['p_val_res'] > 0.99
    high_p_val_sen = enrichment_scores['p_val_sen'] > 0.99
    enrichment_scores = enrichment_scores.loc[~(high_p_val_res & high_p_val_sen)]
    enrichment_scores.to_csv(enrichment_out, index=False)

    return annotations_data


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--associations_file', help='Mutation/drug associations data file to load', default=None)
    parser.add_argument('--annotations_file', help='Drug annotations data file to load', default=None)
    parser.add_argument('--base_dir', help='Base directory for file import', default=None)
    parser.add_argument('--config_file', help='Configuration file to load', default='drug_annotations.config')
    parser.add_argument('--config_base_dir', help='Base directory for configuration file', default=None)
    parser.add_argument('--annotations_out', help='Annotated associations data',
                        default='mutation_drug_pairs_annotated.csv')
    parser.add_argument('--enrichment_out', help='Output file for enrichment results',
                        default='mutation_drug_pair_enrichment.csv')
    args = parser.parse_args()

    main(associations_file=args.associations_file,
         annotations_file=args.annotations_file,
         base_directory=args.base_dir,
         configuration_file=args.config_file,
         config_base_directory=args.base_dir,
         annotations_out=args.annotations_out,
         enrichment_out=args.enrichment_out)
