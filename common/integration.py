
import numpy as np
import pandas as pd
import statsmodels.stats.multitest as multi
import itertools
import scipy.stats as stats


# Generate a table of 0/1 values indicating absence (0) or presence (1) of gene mutations in tumor samples
def generate_mutation_matrix(sample_data, sample_column, gene_column):  # , label_forTable):
    # Get unique tissue sample and gene labels
    sample_list = set(sample_data[sample_column])
    gene_list = set(sample_data[gene_column])

    # Generate the mutation matrix
    mutation_matrix = {}
    for sample in sample_list:
        selection = sample_data[sample_column] == sample
        sample_gene_list = set(sample_data.loc[selection][gene_column].values)

        gene_is_present = [1 if g in sample_gene_list else 0 for g in gene_list]
        mutation_matrix[sample] = gene_is_present

    gene_mut_matrix = pd.DataFrame.from_dict(mutation_matrix, orient='index', columns=gene_list)

    # if label_forTable:
    #     gene_mut_matrix.columns = [f'{s}_{label_forTable}' for s in gene_mut_matrix.columns]

    return gene_mut_matrix


# Compute row-row, column-column, row-column, and column-row Jaccard similarities between two matrices. Return four
# values corresponding to these four row/column label similarity metrics.
def compute_jaccard_similarity(mat1, mat2):
    # Get row and column labels for the two matrices
    row_labels1, col_labels1 = list(mat1.index), list(mat1.columns)
    row_labels2, col_labels2 = list(mat2.index), list(mat2.columns)

    jaccard_r2r = len(set(row_labels1).intersection(set(row_labels2))) / len(set(row_labels1 + row_labels2))
    jaccard_c2c = len(set(col_labels1).intersection(set(col_labels2))) / len(set(col_labels1 + col_labels2))
    jaccard_r2c = len(set(row_labels1).intersection(set(col_labels2))) / len(set(row_labels1 + col_labels2))
    jaccard_c2r = len(set(col_labels1).intersection(set(row_labels2))) / len(set(col_labels1 + row_labels2))

    return jaccard_r2r, jaccard_c2c, jaccard_r2c, jaccard_c2r


# Merge two matrices according to the specified merge type: 'r2r' is row to row merge, 'c2c' is column to column merge,
# 'r2c' is row to column merge, and 'c2r' is column to row merge (default is 'r2r').
def matrix_merge(mat1, mat2, merge_type='r2r'):
    if merge_type == 'r2r':
        print('Merging tables row to row...')
        return pd.merge(mat1, mat2, left_index=True, right_index=True, how='inner')
    elif merge_type == 'c2c':
        print('Merging tables column to column...')
        return pd.merge(mat1.transpose(), mat2.transpose(), left_index=True, right_index=True, how='inner')
    elif merge_type == 'r2c':
        print('Merging tables row to column...')
        return pd.merge(mat1, mat2.transpose(), left_index=True, right_index=True, how='inner')
    elif merge_type == 'c2r':
        print('Merging tables column to row...')
        return pd.merge(mat1.transpose(), mat2, left_index=True, right_index=True, how='inner')
    else:
        print('Warning: invalid merge type specified (valid types are \'r2r\', \'c2c\', \'r2c\', or \'c2r\').')
        print('Returning None...')
        return None


# Calculate drug sensitivity metrics
def calculate_drug_sensitivity(merged_mat, genelist_input, druglist_input):
    drug_list_intersect = set(druglist_input).intersection(set(merged_mat.columns))
    gene_list_intersect = set(genelist_input).intersection(set(merged_mat.columns))

    data_to_use = merged_mat[list(drug_list_intersect.union(gene_list_intersect))]

    def compare_expression(data, pair):
        d, g = pair
        data_subset = data[list(pair)].dropna(axis=0)

        if all(data_subset[g].value_counts() > 3):
            wt_vals = data_subset.loc[data_subset[g] == 0][d]
            mut_vals = data_subset.loc[data_subset[g] == 1][d]

            sci_test = stats.ttest_ind(mut_vals, wt_vals, axis=0, equal_var=True)
            size_effect = (np.mean(mut_vals) - np.mean(wt_vals))/(np.std(list(mut_vals) + list(wt_vals)))

            return g, d, sci_test[1], size_effect
        else:
            return None

    drug_gene_pairs = list(itertools.product(drug_list_intersect, gene_list_intersect))
    results = [compare_expression(data_to_use, pair) for pair in drug_gene_pairs]
    results = [s for s in results if s is not None]
    results = pd.DataFrame(results, columns=['F1', 'F2', 'p', 'SE'])

    # Add additional columns
    fdr_list_table = multi.multipletests(results['p'], alpha=0.5, method='fdr_bh', is_sorted=False)
    results['FDR'] = pd.to_numeric(fdr_list_table[1])
    results['-logP'] = -np.log(results['p'])

    results.sort_values(by='p', ascending=True, inplace=True)

    return results


# Merge associations and annotations data on specified key, keeping specified columns for annotations
def merge_annotations(associations_data, annotations_data, configuration):
    # Configuration must contain left/right keys on which to merge and what columns to keep from the right table
    left_key, right_key = configuration['left_key'], configuration['right_key']
    keep = configuration['right_columns_to_keep']

    keep_annotations_data = annotations_data[[right_key] + keep]
    merged_data = pd.merge(associations_data, keep_annotations_data, left_on=left_key, right_on=right_key)

    return merged_data


# Computer enrichment scores for a given feature1 and feature2 value (note, this function assumes that the
# annotation data contains columns 'SE' and 'p'
def compute_enrichment(annotated_data, feature1, val1, feature2, val2, threshold):
    f1_filter = annotated_data[feature1] == val1
    f2_filter = annotated_data[feature2] == val2
    resistance_filter = annotated_data['SE'] > 0.0
    sensitivity_filter = annotated_data['SE'] < 0.0
    significance_filter = annotated_data['p'] < threshold

    # Get counts needed to calculate resistance enrichment
    num_res_f2 = sum(f1_filter & resistance_filter & f2_filter)
    num_res_f2_sig = sum(f1_filter & resistance_filter & f2_filter & significance_filter)
    num_res_not_f2 = sum(f1_filter & resistance_filter & ~f2_filter)
    num_res_not_f2_sig = sum(f1_filter & resistance_filter & ~f2_filter & significance_filter)
    data_for_fisher_res = [[num_res_f2_sig, num_res_f2 - num_res_f2_sig],
                           [num_res_not_f2_sig, num_res_not_f2 - num_res_not_f2_sig]]

    # Get counts needed to calculate sensitivity enrichment
    num_sen_f2 = sum(f1_filter & sensitivity_filter & f2_filter)
    num_sen_f2_sig = sum(f1_filter & sensitivity_filter & f2_filter & significance_filter)
    num_sen_not_f2 = sum(f1_filter & sensitivity_filter & ~f2_filter)
    num_sen_not_f2_sig = sum(f1_filter & sensitivity_filter & ~f2_filter & significance_filter)
    data_for_fisher_sen = [[num_sen_f2_sig, num_sen_f2 - num_sen_f2_sig],
                           [num_sen_not_f2_sig, num_sen_not_f2 - num_sen_not_f2_sig]]

    # Calculate significance values (i.e. p-values)
    _, p_value_res = stats.fisher_exact(data_for_fisher_res, alternative='greater')
    _, p_value_sen = stats.fisher_exact(data_for_fisher_sen, alternative='greater')

    return p_value_res, p_value_sen


# Compute enrichment scores for all combinations of feature1 and feature2 values (note, this function assumes that the
# annotation data contains columns 'SE' and 'p'
def compute_enrichment_all(annotated_data, feature1, feature2, threshold):
    # Get feature1 and feature2 values
    f1_values = set(annotated_data[feature1])
    f2_values = set(annotated_data[feature2])

    # Get all pair-wise combinations of feature1 and feature2 values
    f1_f2_combos = list(itertools.product(f1_values, f2_values))
    enrichment_scores = [[f1, f2, *compute_enrichment(annotated_data, feature1, f1, feature2, f2, threshold)]
                         for f1, f2 in f1_f2_combos]
    enrichment_scores = pd.DataFrame(enrichment_scores, columns=['F1', 'F2', 'p_val_res', 'p_val_sen'])

    return enrichment_scores
