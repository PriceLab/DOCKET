import matplotlib.pyplot as plt
import pandas as pd
import scipy
import numpy as np
import math

from scipy import stats 
import statsmodels.stats.multitest as multi

def merge_data(input_data):
    Data_WES = pd.read_csv(input_data['Data_file1'])
    Data_DR = pd.read_csv(input_data['Data_file2'])
    Mut_mat = generate_mutation_matrix(Data_WES,input_data['Common_index'][0],input_data['Features_1'], input_data['Label_1'])
    drug_matrix = generate_countious_matrix(Data_DR, input_data['Common_index'][1],input_data['Features_2'][0] , input_data['Features_2'][1], input_data['Label_2'])
    Merged_mat = pd.merge(Mut_mat,drug_matrix, left_index=True, right_index=True, how='inner')
    return(Merged_mat)

def get_features(input_data, File_select):
    if File_select == 'Mut':
        Data = pd.read_csv(input_data['Data_file1'])
        Mut_mat = generate_mutation_matrix(Data_WES,input_data['Common_index'][0],input_data['Features_1'])
        featurelist = list(Mut_mat.columns.values)
    elif File_select == 'Con': ##It means continous valuables
        Data_DR = pd.read_csv(input_data['Data_file2'])
        drug_matrix = generate_countious_matrix(Data_DR, input_data['Common_index'][1],input_data['Features_2'][0] , input_data['Features_2'][1], input_data['Label_2'])
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
            temp = Merged_mat[[Gene,Drug]]
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
                Sci_test = stats.ttest_ind(D_mut_new, D_wt_new, axis=0, equal_var=True)
                pvalue = Sci_test[1]

                Size_effect = (np.mean(D_mut_new) - np.mean(D_wt_new) )/(np.std(D_mut_new + D_wt_new))
                genelist.append(Gene)
                pvalue_list.append(pvalue)
                SE_list.append(Size_effect)
                drug_list_used.append(Drug)

    result['F1'] = genelist
    result['F2'] = drug_list_used
    result['p'] = pvalue_list
    result['SE'] = SE_list
    FDR_List_table = multi.multipletests(pvalue_list, alpha = 0.05, method = 'fdr_bh', is_sorted = False)
    FDR_list = pd.to_numeric(list(FDR_List_table[1]))
    result['FDR'] = FDR_list
    
    x_lim = 1.5
    result_sen = result.loc[result['FDR'] <0.05].loc[result['SE'] <0]
    result_res = result.loc[result['FDR'] <0.05].loc[result['SE'] >0]
    result_sen.to_csv(input_data2['Output_SEN_File1'])
    result_res.to_csv(input_data2['Output_RES_File2'])
    
    import plotly.express as px
    result['-logP'] = -np.log(result['p'])
    fig = px.scatter(result, "SE", "-logP", hover_data=['F1','F2'],color="F1")
    fig.show()
    
    fig = px.scatter(result, "SE", "-logP", hover_data=['F1','F2'],color="F2")
    fig.show()
    
    return(result)

#def generate_countious_matrix(BeatAML_drugResponse_matrix, sample_column, inhibitor_column, ic50_column):
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
    sample_list =  list(set(AML_Expr[sample_column]))
    df_list = []
    for sample in sample_list:
        df_temp = AML_Expr.loc[AML_Expr[sample_column] == sample][[Feature_column,value_column]]
        df_temp.index = df_temp[Feature_column]
        df_list.append(df_temp[value_column])
    result = pd.concat(df_list, axis=1, sort=True)
    result.columns = sample_list
    #result.index = list(result.index.values)
    result = result.transpose()
    temp_col = list(result.columns.values)
    new_col = []
    for i in temp_col:
        new_col.append(str(i)+'_'+label_forTable)
    result.columns = new_col
    return(result)

def generate_mutation_matrix(TCGA_mut_selected, sample_column, gene_column, label_forTable):
    sample_list = list(set(TCGA_mut_selected[sample_column]))
    Gene_list = list(set(TCGA_mut_selected[gene_column]))
    dic_patient_mut = {}
    dic_patient_mut_standard = {}
    for sample in sample_list:
        temp = []
        dic_patient_mut[sample] = set(list(TCGA_mut_selected.loc[TCGA_mut_selected[sample_column] == sample ][gene_column].values))
        for Gene in Gene_list:
            if Gene in dic_patient_mut[sample]:
                temp.append(1)
            else:
                temp.append(0)
        dic_patient_mut_standard[sample] = temp

    Gene_mut_matrix = pd.DataFrame.from_dict(dic_patient_mut_standard, orient='index')
    Gene_mut_matrix.columns = Gene_list 
    temp_col = list(Gene_mut_matrix.columns.values)
    new_col = []
    for i in temp_col:
        new_col.append(str(i)+'_'+label_forTable)
    Gene_mut_matrix.columns = new_col   
    return(Gene_mut_matrix)


