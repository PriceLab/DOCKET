#!/bin/env python3

import argparse
import pandas as pd
import common.integration as integrate
import common.file_io as io


# Takes two files, one containing cell line gene mutation data and the other containing tumor tissue gene mutation data.
# Compare the similarity of mutations (i.e. gene and mutation site within the gene) by estimating the ratio of identical
# mutation sites between the two data sets. Specifically, this is designed to operate on data obtained from GDSC (for
# cell-line-derived gene variants) and TCGA (for patient-derived somatic mutations). However, the analytical methodology
# is general for different cancer types and can therefore operate on data for LUAD (Lung Adenocarcinoma), BRCA (Breast
# Invasive Carcinoma), or other cancer types in the TCGA, with corresponding cell lines from the GDSC project. Highly
# frequently altered somatic mutations from patient derived samples and similar genes in the cell line derived variants
# are identified.
def main(cell_line_file=None,
         tissue_file=None,
         base_directory=None,
         configuration_file=None,
         config_base_directory=None,
         file_out='similar_mutation_sites.csv'):

    # Load cell line and tissue sample mutation data
    cell_line_mut_data = pd.read_csv(cell_line_file, index_col=None)
    sample_mut_data = pd.read_csv(tissue_file, index_col=None)

    # Load configuration data for the current data sets
    config = io.load_json(configuration_file)
    disease_type, samp_config, cell_line_config = config['disease_type'], config['sample'], config['cell_line']
    s_label, s_gene_label, s_mut_label = samp_config['label'], samp_config['gene_label'], samp_config['mutation_label']
    cl_gene_label, cl_mut_label = cell_line_config['gene_label'], cell_line_config['mutation_label']

    # Calculate gene mutation frequencies across tissues
    mut_freq_data = integrate.generate_mutation_matrix(sample_mut_data, s_label, s_gene_label)
    mut_freq_data = mut_freq_data.sum() / mut_freq_data.shape[0]
    mut_freq_data = pd.DataFrame({'gene': mut_freq_data.index, 'frequency': mut_freq_data.values})

    # Calculate mutation similarity scores for high-mutation-frequency genes
    similarity_scores = []
    high_mut_freq_genes = mut_freq_data['gene'][mut_freq_data['frequency'] > 0.05]
    for gene in high_mut_freq_genes:
        cl_data_subset = cell_line_mut_data[cell_line_mut_data[cl_gene_label] == gene]
        s_data_subset = sample_mut_data[sample_mut_data[s_gene_label] == gene]

        cl_mut_labels = [f'{g}{m}' for g, m in zip(cl_data_subset[cl_gene_label], cl_data_subset[cl_mut_label])]
        s_mut_labels = [f'{g}{m}' for g, m in zip(s_data_subset[s_gene_label], s_data_subset[s_mut_label])]
        cl_s_common_mut = [s for s in cl_mut_labels if s in s_mut_labels]

        no_common = len(cl_s_common_mut) == 0
        sim1 = 0 if no_common else len(cl_s_common_mut) / (len(cl_mut_labels) + len(s_mut_labels))
        sim2 = 0 if no_common else len(cl_s_common_mut) / len(cl_mut_labels)
        sim3 = 0 if no_common else len(set(cl_s_common_mut)) / len(set(cl_mut_labels + s_mut_labels))

        similarity_scores.append([gene, sim1, sim2, sim3])

    similarity_scores = pd.DataFrame(similarity_scores, columns=['gene', 'sim1', 'sim2', 'sim3'])
    similarity_scores = mut_freq_data.merge(similarity_scores, left_on='gene', right_on='gene')
    similarity_scores['disease'] = disease_type
    similarity_scores.sort_values(by='sim2', ascending=False, inplace=True)

    similarity_scores.to_csv(file_out, index=False)

    return similarity_scores


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--cell_line_file', help='Cell line data file to load', default=None)
    parser.add_argument('--tissue_file', help='Tissue data file to load', default=None)
    parser.add_argument('--base_dir', help='Base directory for file import', default=None)
    parser.add_argument('--config_file', help='Configuration file to load', default='similarity_compare.config')
    parser.add_argument('--config_base_dir', help='Base directory for configuration file', default=None)
    parser.add_argument('--file_out', help='Similarity data', default='similar_mutation_sites.csv')
    args = parser.parse_args()

    main(cell_line_file=args.cell_line_file,
         tissue_file=args.tissue_file,
         base_directory=args.base_dir,
         configuration_file=args.config_file,
         config_base_directory=args.base_dir,
         file_out=args.file_out)
