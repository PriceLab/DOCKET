#!/bin/env python3

import argparse
import pandas as pd
import common.integration as integrate
import common.file_io as io


# Takes two files, one containing cell line mutation matrix data and the other containing cell line drug response data.
# Merge these two tables and run drug sensitivity analysis for mutations in a specified list of genes. The selection of
# genes of interest is based on results of similarity comparison of mutations in cell lines (data derived from GDSC) and
# in tumor tissues (data derived from TCGA).
def main(mut_matrix_file=None,
         drug_response_file=None,
         mut_similarity_file=None,
         base_directory=None,
         configuration_file=None,
         config_base_directory=None,
         merged_out='mutation_drug_merged.csv',
         mut_drug_pairs_out='mutation_drug_pairs.csv'):

    # Load mutation matrix and drug response data
    mut_matrix_data = pd.read_csv(mut_matrix_file, index_col=0)
    drug_response_data = pd.read_csv(drug_response_file, index_col=0)

    # Load cell line/tumor mutation similarity data
    mut_similarity_data = pd.read_csv(mut_similarity_file, index_col=False)

    # Merge mutation matrix and drug response tables by rows, or by columns, or row to column, or column to row, based
    # on preliminary analysis of row/column similarities (Jaccard similarity) in the two tables.
    jr2r, jc2c, jr2c, jc2r = integrate.compute_jaccard_similarity(mut_matrix_data, drug_response_data)
    if jr2r > 0.5:
        merged_data = integrate.matrix_merge(mut_matrix_data, drug_response_data, merge_type='r2r')
    elif jc2c > 0.5:
        merged_data = integrate.matrix_merge(mut_matrix_data, drug_response_data, merge_type='c2c')
    elif jr2c > 0.5:
        merged_data = integrate.matrix_merge(mut_matrix_data, drug_response_data, merge_type='r2c')
    elif jc2r > 0.5:
        merged_data = integrate.matrix_merge(mut_matrix_data, drug_response_data, merge_type='c2r')
    else:
        merged_data = None

    if merged_data is None:
        print('Warning: tables not merged because of insufficient similarity between rows and/or columns.')
        print('Returning None!')
        return None
    else:
        # Write merged table to file
        merged_data.to_csv(merged_out)

    # Load configuration data for drug response analysis
    config = io.load_json(configuration_file)
    gene_list = [] if 'gene_list' not in list(config.keys()) else config['gene_list']
    drug_list = [] if 'drug_list' not in list(config.keys()) else config['drug_list']
    gene_list_filter = None if 'gene_list_filter' not in list(config.keys()) else config['gene_list_filter']

    # If gene list filters were specified, filter mutation similarity data and get the resulting gene list
    if gene_list_filter is not None:
        sim2_filter = None if 'sim2' not in list(gene_list_filter.keys()) else gene_list_filter['sim2']
        sim3_filter = None if 'sim3' not in list(gene_list_filter.keys()) else gene_list_filter['sim3']
        if sim2_filter is not None:
            mut_similarity_data = mut_similarity_data[mut_similarity_data['sim2'] > sim2_filter]
        if sim3_filter is not None:
            mut_similarity_data = mut_similarity_data[mut_similarity_data['sim3'] > sim3_filter]
        gene_list = mut_similarity_data['gene']

    # If the drug list is empty, get it from the drug response table
    if len(drug_list) < 1:
        drug_list = list(drug_response_data.columns)

    # If the gene list is empty, get it from the mutation matrix table
    if len(gene_list) < 1:
        gene_list = list(mut_matrix_data.columns)

    # Calculate drug sensitivity metrics and write to file
    drug_sensitivity = integrate.calculate_drug_sensitivity(merged_data, gene_list, drug_list)
    drug_sensitivity.to_csv(mut_drug_pairs_out, index=None)

    return drug_sensitivity


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--mut_matrix_file', help='Cell line mutation data file to load', default=None)
    parser.add_argument('--drug_response_file', help='Cell line drug response data file to load', default=None)
    parser.add_argument('--mut_similarity_file', help='Cell line/tumor mutation similarity file',
                        default='similar_mutation_sites.csv')
    parser.add_argument('--base_dir', help='Base directory for file import', default=None)
    parser.add_argument('--config_file', help='Configuration file to load', default='drug_response.config')
    parser.add_argument('--config_base_dir', help='Base directory for configuration file', default=None)
    parser.add_argument('--merged_out', help='Mutation and drug response data', default='mutation_drug_merged.csv')
    parser.add_argument('--mut_drug_pairs_out', help='Mutation/drug pair data', default='mutation_drug_pairs.csv')
    args = parser.parse_args()

    main(mut_matrix_file=args.mut_matrix_file,
         drug_response_file=args.drug_response_file,
         mut_similarity_file=args.mut_similarity_file,
         base_directory=args.base_dir,
         configuration_file=args.config_file,
         config_base_directory=args.base_dir,
         merged_out=args.merged_out,
         mut_drug_pairs_out=args.mut_drug_pairs_out)
