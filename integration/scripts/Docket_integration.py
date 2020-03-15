import matplotlib.pyplot as plt
import pandas as pd
import scipy
import numpy as np
import math
import plotly
import plotly.express as px
from scipy import stats
import statsmodels.stats.multitest as multi

import scipy.stats as stats


def matrix_comp(Mut_mat, drug_matrix):
    col_names_A = list(Mut_mat.columns.values)
    col_names_B = list(drug_matrix.columns.values)

    row_names_A = list(Mut_mat.index.values)
    row_names_B = list(drug_matrix.index.values)

    jacard_cof_r2r = len(set(row_names_A).intersection(
        set(row_names_B))) / len(set(row_names_A + row_names_B))
    jacard_cof_c2c = len(set(col_names_A).intersection(
        set(col_names_B))) / len(set(col_names_A + col_names_B))

    jacard_cof_r2c = len(set(row_names_A).intersection(
        set(col_names_B))) / len(set(row_names_A + col_names_B))
    jacard_cof_c2r = len(set(col_names_A).intersection(
        set(row_names_B))) / len(set(col_names_A + row_names_B))

    if jacard_cof_r2r == 1:
        print("Row names are identical!")
    elif jacard_cof_r2r > 0:
        print("Part of the objects in rows are identical!")
    if jacard_cof_c2c == 1:
        print("Col names are identical!")
    elif jacard_cof_c2c > 0:
        print("Part of the objects in col are identical!")

    if jacard_cof_r2c == 1:
        print("Rownames in A and Colnames in B are identical!")
    elif jacard_cof_r2c > 0:
        print("Rownames in A and Colnames in B show similarity!")

    if jacard_cof_c2r == 1:
        print("Colnames in A and Rownames in B are identical!")
    elif jacard_cof_c2r > 0:
        print("Colnames in A and Rownames in B show similarity!")

    return([jacard_cof_r2r, jacard_cof_c2c, jacard_cof_r2c, jacard_cof_c2r])


def merge_matrix(Mut_mat, drug_matrix, direction_for_merge1, direction_for_merge2):
    import pandas as pd
    if direction_for_merge1 == 'Col':
        Mut_mat = Mut_mat.transpose()
        Label1_for_merge = 'Row'
    elif direction_for_merge1 == 'Row':
        Label1_for_merge = 'Row'
    else:
        print("Incorrect label!")
    if direction_for_merge1 == 'Col':
        drug_matrix = drug_matrix.transpose()
        Label2_for_merge = 'Row'
    elif direction_for_merge2 == 'Row':
        Label2_for_merge = 'Row'
    else:
        print("Incorrect label!")
    result = pd.DataFrame()
    if Label2_for_merge == 'Row' and Label2_for_merge == 'Row':
        result = pd.merge(Mut_mat, drug_matrix, left_index=True,
                          right_index=True, how='inner')
    return(result)


def Integration_category_numeric(Merged_mat, genelist_input, druglist_input):
    genelist = []
    pvalue_list = []
    FDR_list = []
    SE_list = []
    result = pd.DataFrame()
    drug_list_used = []
    Druglist = druglist_input

    for Drug in Druglist:
        if Drug in list(Merged_mat.columns.values):
            for Gene in genelist_input:
                if Gene in (Merged_mat.columns.values):
                    temp = Merged_mat[[Gene, Drug]]
                    D_wt = temp.loc[temp[Gene] == 0][Drug].values
                    D_wt_new = []
                    D_mut_new = []
                    for i in D_wt:
                        if math.isnan(i) == False:
                            D_wt_new.append(i)

                    D_mut = temp.loc[temp[Gene] > 0][Drug].values
                    for i in D_mut:
                        if math.isnan(i) == False:
                            D_mut_new.append(i)

                    if len(D_mut_new) > 2 and len(D_wt_new) > 2:
                        Sci_test = stats.ttest_ind(
                            D_mut_new, D_wt_new, axis=0, equal_var=True)
                        pvalue = Sci_test[1]

                        Size_effect = (
                            np.mean(D_mut_new) - np.mean(D_wt_new))/(np.std(D_mut_new + D_wt_new))
                        genelist.append(Gene)
                        pvalue_list.append(pvalue)
                        SE_list.append(Size_effect)
                        drug_list_used.append(Drug)

    result['F1'] = genelist
    result['F2'] = drug_list_used
    result['p'] = pvalue_list
    result['SE'] = SE_list
    FDR_List_table = multi.multipletests(
        pvalue_list, alpha=0.05, method='fdr_bh', is_sorted=False)
    FDR_list = pd.to_numeric(list(FDR_List_table[1]))
    result['FDR'] = FDR_list

    x_lim = 1.5
    result_sen = result.loc[result['FDR'] < 0.05].loc[result['SE'] < 0]
    result_res = result.loc[result['FDR'] < 0.05].loc[result['SE'] > 0]
    # result_sen.to_csv(input_data2['Output_SEN_File1'])
    # result_res.to_csv(input_data2['Output_RES_File2'])
    import plotly
    import plotly.express as px
    result['-logP'] = -np.log(result['p'])
    fig = px.scatter(result, "SE", "-logP",
                     hover_data=['F1', 'F2'], color="F1")
    fig.show()

    #fig = px.scatter(result, "SE", "-logP", hover_data=['F1','F2'],color="F2")
    # fig.show()

    return(result)


def enrichment_forSignificance_res(result_annotate, label_1, value_1, label_2, value_2, p_threshold):
    x = result_annotate.loc[result_annotate[label_1] == value_1]
    x_res = x.loc[x['SE'] > 0]
    x_res_EGFR_signal = x_res.loc[x_res[label_2] == value_2]
    x_res_EGFR_signal_sig = x_res_EGFR_signal.loc[x_res_EGFR_signal['p'] < p_threshold]
    x_res_nonEGFR_signal = x_res.loc[x_res[label_2] != value_2]
    x_res_nonEGFR_signal_sig = x_res_nonEGFR_signal.loc[x_res_nonEGFR_signal['p'] < p_threshold]
    list_fortest = [[x_res_EGFR_signal_sig.shape[0], x_res_EGFR_signal.shape[0] - x_res_EGFR_signal_sig.shape[0]],
                    [x_res_nonEGFR_signal_sig.shape[0], (x_res_nonEGFR_signal.shape[0] - x_res_nonEGFR_signal_sig.shape[0])]]
    oddsratio, pvalue = stats.fisher_exact(list_fortest, alternative='greater')
    return(pvalue)


def enrichment_forSignificance_sen(result_annotate, label_1, value_1, label_2, value_2, p_threshold):
    x = result_annotate.loc[result_annotate[label_1] == value_1]
    x_res = x.loc[x['SE'] < 0]
    x_res_EGFR_signal = x_res.loc[x_res[label_2] == value_2]
    x_res_EGFR_signal_sig = x_res_EGFR_signal.loc[x_res_EGFR_signal['p'] < p_threshold]
    x_res_nonEGFR_signal = x_res.loc[x_res[label_2] != value_2]
    x_res_nonEGFR_signal_sig = x_res_nonEGFR_signal.loc[x_res_nonEGFR_signal['p'] < p_threshold]
    list_fortest = [[x_res_EGFR_signal_sig.shape[0], x_res_EGFR_signal.shape[0] - x_res_EGFR_signal_sig.shape[0]],
                    [x_res_nonEGFR_signal_sig.shape[0], (x_res_nonEGFR_signal.shape[0] - x_res_nonEGFR_signal_sig.shape[0])]]
    oddsratio, pvalue = stats.fisher_exact(list_fortest, alternative='greater')
    return(pvalue)


def enrichment_forSignificance_sen_all(result_annotate, F1, F2, p_threshold):
    gene_list = []
    mol_action_list = []
    p_list = []
    for gene in list(set(result_annotate[F1])):
        for mol_action in list(set(result_annotate[F2])):
            p = enrichment_forSignificance_sen(
                result_annotate, F1, gene, F2, mol_action, p_threshold)
            if p < p_threshold:
                p_list.append(p)
                gene_list.append(gene)
                mol_action_list.append(mol_action)

    result = pd.DataFrame(
        {'Gene': gene_list, 'mol_action': mol_action_list, 'p': p_list})
    return(result)


def enrichment_forSignificance_res_all(result_annotate, F1, F2, p_threshold):
    gene_list = []
    mol_action_list = []
    p_list = []
    for gene in list(set(result_annotate[F1])):
        for mol_action in list(set(result_annotate[F2])):
            p = enrichment_forSignificance_res(
                result_annotate, F1, gene, F2, mol_action, p_threshold)
            if p < p_threshold:
                p_list.append(p)
                gene_list.append(gene)
                mol_action_list.append(mol_action)

    result = pd.DataFrame(
        {'Gene': gene_list, 'mol_action': mol_action_list, 'p': p_list})
    return(result)


def Annotation_feature(result, obj_id, Drug_annotation, list_forAnnotate, for_plot_F1, for_plot_F2, for_plot_x, for_plot_y):
    temp = list(result[obj_id].values)
    temp_new_id = []
    Annotation_list = []
    for i in temp:
        temp_new_id.append(i)
        Annotation_list.append(
            Drug_annotation.loc[Drug_annotation[list_forAnnotate[0]] == i][list_forAnnotate[1]].values[0])

    result[list_forAnnotate[1]] = Annotation_list

    import plotly.express as px

    fig = px.scatter(result, for_plot_x, for_plot_y, hover_data=[
                     for_plot_F1, for_plot_F2, list_forAnnotate[1]], color=list_forAnnotate[1])
    fig.show()
    return(result)


def merge_data(input_data):
    Data_WES = pd.read_csv(input_data['Data_file1'])
    Data_DR = pd.read_csv(input_data['Data_file2'])
    Mut_mat = generate_mutation_matrix(
        Data_WES, 
        input_data['Common_index'][0], 
        input_data['Features_1'], 
        input_data['Label_1']
    )
    drug_matrix = generate_countious_matrix(
        Data_DR, input_data['Common_index'][1], input_data['Features_2'][0], input_data['Features_2'][1], input_data['Label_2'])
    Merged_mat = pd.merge(Mut_mat, drug_matrix,
                          left_index=True, right_index=True, how='inner')
    return(Merged_mat)


def get_features(input_data, File_select):
    if File_select == 'Mut':
        Data = pd.read_csv(input_data['Data_file1'])
        Mut_mat = generate_mutation_matrix(
            Data,
            input_data['Common_index'][0],
            input_data['Features_1'],
            input_data['Label_1'],
        )
        featurelist = list(Mut_mat.columns.values)
    elif File_select == 'Con':  # It means continous valuables
        Data_DR = pd.read_csv(input_data['Data_file2'])
        drug_matrix = generate_countious_matrix(
            Data_DR, input_data['Common_index'][1], input_data['Features_2'][0], input_data['Features_2'][1], input_data['Label_2'])
        featurelist = list(drug_matrix.columns.values)
    return(featurelist)


def Integration_mutation_drugResponse(Merged_mat, input_data1, input_data2):
    genelist = []
    pvalue_list = []
    FDR_list = []
    SE_list = []
    result = pd.DataFrame()
    drug_list_used = []
    Druglist = input_data2['Druglist']
    if len(Druglist) == 0:
        print("The number of Factors selected is zero. Use all features for analysis!")
        Druglist = get_features(input_data1, 'Con')
    else:
        Druglist = input_data2['Druglist']

    for Drug in Druglist:
        for Gene in input_data2['Genelist']:
            #Gene = 'Geneset6'
            temp = Merged_mat[[Gene, Drug]]
            D_wt = temp.loc[temp[Gene] == 0][Drug].values
            D_wt_new = []
            D_mut_new = []
            for i in D_wt:
                if math.isnan(i) == False:
                    D_wt_new.append(i)

            D_mut = temp.loc[temp[Gene] > 0][Drug].values
            for i in D_mut:
                if math.isnan(i) == False:
                    D_mut_new.append(i)

            if len(D_mut_new) > 3 and len(D_wt_new) > 3:
                Sci_test = stats.ttest_ind(
                    D_mut_new, D_wt_new, axis=0, equal_var=True)
                pvalue = Sci_test[1]

                Size_effect = (np.mean(D_mut_new) - np.mean(D_wt_new)
                               )/(np.std(D_mut_new + D_wt_new))
                genelist.append(Gene)
                pvalue_list.append(pvalue)
                SE_list.append(Size_effect)
                drug_list_used.append(Drug)

    result['F1'] = genelist
    result['F2'] = drug_list_used
    result['p'] = pvalue_list
    result['SE'] = SE_list
    FDR_List_table = multi.multipletests(
        pvalue_list, alpha=0.05, method='fdr_bh', is_sorted=False)
    FDR_list = pd.to_numeric(list(FDR_List_table[1]))
    result['FDR'] = FDR_list

    x_lim = 1.5
    result_sen = result.loc[result['FDR'] < 0.05].loc[result['SE'] < 0]
    result_res = result.loc[result['FDR'] < 0.05].loc[result['SE'] > 0]
    result_sen.to_csv(input_data2['Output_SEN_File1'])
    result_res.to_csv(input_data2['Output_RES_File2'])

    #import plotly.express as px
    #result['-logP'] = -np.log(result['p'])
    #fig = px.scatter(result, "SE", "-logP", hover_data=['F1','F2'],color="F1")
    # fig.show()

    #fig = px.scatter(result, "SE", "-logP", hover_data=['F1','F2'],color="F2")
    # fig.show()

    return(result)

# def generate_countious_matrix(BeatAML_drugResponse_matrix, sample_column, inhibitor_column, ic50_column):
#    sample_list = list(set(BeatAML_drugResponse_matrix[sample_column]))
#    Gene_list = list(set(BeatAML_drugResponse_matrix[inhibitor_column]))
#    dic_patient_mut = {}
#    dic_patient_mut_standard = {}
#    for sample in sample_list:
#        temp = []
#        dic_patient_mut[sample] = set(list(BeatAML_drugResponse_matrix.loc[BeatAML_drugResponse_matrix[sample_column] == sample ][inhibitor_column].values))
#        for Gene in Gene_list:
#            if Gene in dic_patient_mut[sample]:
#                x = BeatAML_drugResponse_matrix.loc[BeatAML_drugResponse_matrix[sample_column] == sample]
#                x = x.loc[x[inhibitor_column] == Gene][ic50_column].values[0]
#                temp.append(x)
#            else:
#                temp.append('NA')
#        dic_patient_mut_standard[sample] = temp
#
#    Gene_mut_matrix = pd.DataFrame.from_dict(dic_patient_mut_standard, orient='index')
#    Gene_mut_matrix.columns = Gene_list
#    return(Gene_mut_matrix)


def generate_countious_matrix(AML_Expr, sample_column, Feature_column, value_column, label_forTable):
    sample_list = list(set(AML_Expr[sample_column]))
    df_list = []
    for sample in sample_list:
        df_temp = AML_Expr.loc[AML_Expr[sample_column]
                               == sample][[Feature_column, value_column]]
        df_temp.index = df_temp[Feature_column]
        df_list.append(df_temp[value_column])
    result = pd.concat(df_list, axis=1, sort=True)
    result.columns = sample_list
    #result.index = list(result.index.values)
    result = result.transpose()
    temp_col = list(result.columns.values)
    new_col = []
    if label_forTable != '':
        for i in temp_col:
            new_col.append(str(i)+'_'+label_forTable)
        result.columns = new_col
    return(result)


def generate_mutation_matrix(TCGA_mut_selected, sample_column, gene_column, label_forTable):
    """
    Paramter
    ========
        TCGA_mut_selected:
        sample_column:
        gene_column:
        label_forTable:
    """
    sample_list = list(set(TCGA_mut_selected[sample_column]))
    Gene_list = list(set(TCGA_mut_selected[gene_column]))
    dic_patient_mut = {}
    dic_patient_mut_standard = {}
    for sample in sample_list:
        temp = []
        dic_patient_mut[sample] = set(list(
            TCGA_mut_selected.loc[TCGA_mut_selected[sample_column] == sample][gene_column].values))
        for Gene in Gene_list:
            if Gene in dic_patient_mut[sample]:
                temp.append(1)
            else:
                temp.append(0)
        dic_patient_mut_standard[sample] = temp

    Gene_mut_matrix = pd.DataFrame.from_dict(
        dic_patient_mut_standard, orient='index')
    Gene_mut_matrix.columns = Gene_list
    temp_col = list(Gene_mut_matrix.columns.values)
    new_col = []
    if label_forTable != '':
        for i in temp_col:
            new_col.append(str(i)+'_'+label_forTable)
        Gene_mut_matrix.columns = new_col
    return(Gene_mut_matrix)



def cytoscape_plot(x, F1, F2,Edge, types):
    from cyjupyter import Cytoscape
    import json

    nodes_list = []
    edges_list = []

    if types == 'category':
        ID1_list = []
        ID2_list = []
        for i in range(0, x.shape[0]):
            ID1_list.append( str(x[F1].values[i]) )
            ID2_list.append( str(x[F2].values[i]) )
            
        x['ID1'] = ID1_list
        x['ID2'] = ID2_list

        for i in range(0, x.shape[0]):
            nodes_list.append({'data':{'id':x['ID1'].values[i], 
                                       'color':'yellow', 
                                       'shape':'ellipse'}} )
            
            nodes_list.append({'data':{'id':x['ID2'].values[i], 
                                       'color':'grey', 
                                       'shape':'rectangle'}} )
            
            if x[Edge].values[i] > 0 :
                edges_list.append({'data':{'id': 'edge'+str(i),
                                           'source': x['ID1'].values[i],
                                           'target': x['ID2'].values[i], 
                                           'type': 'red'}})
                
            elif x[Edge].values[i]  < 0:
                edges_list.append({'data':{'id': 'edge'+str(i),
                                           'source': x['ID1'].values[i],
                                           'target': x['ID2'].values[i], 
                                           'type': 'black'}})

    my_cy = {'elements':{'nodes':nodes_list,'edges':edges_list}}

    mystyle = [{
            'selector': 'node',
            'style': {
                'background-color': 'data(color)',
                'label': 'data(id)',
                'width': 12,
                'height': 12,
                'shape':'data(shape)',
                'color': 'grey',
                'font-weight': 400,
                'text-halign': 'middle',
                'text-valign': 'bottom',
                'font-size': 6,
                'size':3
            }},
            {
            'selector': 'edge',
            'style': {
                'width': 1,
                'line-color': 'data(type)',
                'target-arrow-color': '#37474F',
                'target-arrow-shape': 'triangle'}
            }]
    cy = Cytoscape(data = my_cy, visual_style = mystyle,  background =('#FFFFFF'))
    return(cy)
