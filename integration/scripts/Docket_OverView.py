#!/usr/bin/env python
# coding: utf-8

import matplotlib.pyplot as plt
import pandas as pd
import scipy
import numpy as np
import math
from scipy import stats
import statsmodels.stats.multitest as multi
import scipy.stats as stats

###Giving the PCA file, select the principle components for visulize. 
def pca_plot(File_PCA, pca_sele1, pca_sele2):
    import pandas as pd
    import matplotlib.pyplot as plt
    import plotly.express as px
    pca = pd.read_table(File_PCA,header=None)  
    colnames = ['object']
    for i in range(1,pca.shape[1]):
        colnames.append('PC'+str(i))

    pca.columns = colnames
    pca.index = pca['object']
    plt.figure(figsize = (4,4),dpi = 300)
    fig = px.scatter(pca, pca_sele1, pca_sele2, hover_data=['object'])
    fig.show()

#### Measuring factor difference between two groups

def cohen_dist(vec1, vec2):
    M1 = np.mean(vec1)
    N1 = len(vec1)
    M2 = np.mean(vec2)
    N2 = len(vec2)
    SD_pooled = np.sqrt(
                        (np.square(np.std(vec1)) * (N1 - 1) 
                        + np.square(np.std(vec2)) * (N2 - 1)) 
                        / (N1 + N2 -2)
                       )
    d = (M1 - M2) / SD_pooled
    return(d)


def feature_association_category(data_for_test, columns):
    df_result_category = pd.DataFrame()
    item1_list=[]
    group_A_list=[]
    group_notA_list = []
    item2_list=[]
    group_B_list=[]
    A_B_list=[]
    A_notB_list=[]
    notA_B_list=[]
    notA_notB_list=[]
    p_list=[]
    odds_list=[]
    Label = []
    category_list = []
    for item in columns:
        
        if str(data_for_test.loc[:,item].dtypes) == 'object' or str(data_for_test.loc[:,item].dtypes) == 'category' or str(data_for_test.loc[:,item].dtypes) == 'bool' or str(data_for_test.loc[:,item].dtypes) == 'int64':
            category_list.append(item)
        elif str(data_for_test.loc[:,item].dtypes) == 'int64' and len(set(data_for_test.loc[:,item])) < 5:
            category_list.append(item)
    
    for item1 in category_list:
        category_1 = set(data_for_test[item1])
        #print(category_1)
        if (len(category_1) < 10):
            for item2 in category_list:
                if item1 != item2:
                    category_2 = set(data_for_test[item2])
                    if(len(category_2)) < 10:
                        
                        for group_A in category_1:
                            if isinstance(group_A, float) == False :
                                if isinstance(group_A, bool) == True: 
                                    group_A == True
                                    group_not_A = False
                                #if isinstance(group_A, int) == True:    
                                else:
                                    group_A = set([group_A])
                                    #print(group_A)
                                    group_not_A  = (category_1 - (group_A))
                                    #print(group_not_A)
                                df_A = data_for_test.loc[data_for_test[item1].isin(group_A)]
                                df_notA = data_for_test.loc[data_for_test[item1].isin(group_not_A)]
                                #print(group_A)
                                #print(group_not_A)


                                for group_B in category_2:
                                    if isinstance(group_B, float) == False :
                                        if isinstance(group_B, bool) == True: 
                                            group_B == True
                                            group_not_B = False

                                        else:
                                            group_B = set([group_B])
                                            group_not_B = (category_2 - (group_B))

                                        A_B = df_A.loc[df_A[item2].isin(group_B)].shape[0]

                                        A_notB = df_A.loc[df_A[item2].isin(group_not_B)].shape[0]
                                        notA_B = df_notA.loc[df_notA[item2].isin(group_B)].shape[0]

                                        notA_notB = df_notA.loc[df_notA[item2].isin(group_not_B)].shape[0]
                                        #print([[A_B, A_notB], [notA_B, notA_notB]])
                                        oddsratio, pvalue = scipy.stats.fisher_exact([[A_B, A_notB], [notA_B, notA_notB]], alternative='two-sided')
                                        #print(pvalue)
                                        if pvalue < 0.05 :
                                            item1_list.append(item1)
                                            group_A_list.append(group_A)

                                            item2_list.append(item2)
                                            group_B_list.append(group_B)
                                            A_B_list.append(A_B)
                                            A_notB_list.append(A_notB)
                                            notA_B_list.append(notA_B)
                                            notA_notB_list.append(notA_notB)
                                            p_list.append(pvalue)
                                            odds_list.append(oddsratio)

                                            if np.isinf(oddsratio):
                                                Label.append("OverRepresented")
                                            elif oddsratio > 1:
                                                Label.append("OverRepresented")
                                            elif  oddsratio < 1:
                                                Label.append("UnderRepresented")

                               
    df_result_category = pd.DataFrame({
        'FactorA':item1_list, 'CategoryA':group_A_list, 
        'FactorB':item2_list, 'CategoryB':group_B_list,
        "A_B":A_B_list, 'A_notB':A_notB_list,
        "notA_B":notA_B_list, 'notA_notB':notA_notB_list,
        'pvalue':p_list,'oddsratio':odds_list,
        'Label':Label
    })    

    return(df_result_category)




def feature_association_category_numerical(data_for_test, columns):
    df_result_category = pd.DataFrame()
    item1_list=[]
    group_A_list=[]
    group_notA_list = []
    item2_list=[]
    p_list=[]
    se_list=[]

    category_list = []
    for item in columns:
        category_list.append(item)

    for item2 in category_list:
        if str(data_for_test.loc[:,item2].dtypes) == 'int64' or str(data_for_test.loc[:,item2].dtypes) == 'float64':  
            if len( set(data_for_test[item2])) > 10:
                print(item2)

                for item1 in category_list:
                    if item1 != item2:
                        category_1 = set(data_for_test[item1])
                        for group_A in category_1:
                            if isinstance(group_A, float) == False  and isinstance(group_A, int) == False:
                            #if type(group_A) != float and type(group_A) != int: 
                                if isinstance(group_A, bool) == True:
                                #if type(group_A) == bool:
                                    group_A == True
                                    group_not_A = False
                                else:
                                    group_A = group_A
                                    group_not_A  = (category_1 - set(group_A))


                                df_A = data_for_test.loc[data_for_test[item1].isin([group_A])]
                                df_notA = data_for_test.loc[data_for_test[item1].isin([group_not_A])]


                                array_A = df_A.loc[:,item2].values
                                array_A = array_A[~np.isnan(array_A)]

                                array_B = df_notA.loc[:,item2].values
                                
                                array_B = array_B[~np.isnan(array_B)]
                                
                                if len(array_A) > 5 and len(set(array_A))>1:
                                    if  len(array_B) > 5 and len(set(array_B))>1:
                                        #print(array_A)

                                        #print(array_B)
                                        stat,pvalue = (scipy.stats.mannwhitneyu(array_A, array_B))
                                        se = cohen_dist(array_A, array_B)
                                        if pvalue < 0.05:
                                            item1_list.append(item1)
                                            group_A_list.append(group_A)
                                            if type(group_not_A) == bool:
                                                group_notA_list.append(group_not_A)
                                            else:
                                                group_notA_list.append(','.join(group_not_A))
                                            item2_list.append(item2)

                                            p_list.append(pvalue)
                                            se_list.append(se)


    df_result_category = pd.DataFrame({
            'FactorA':item1_list, 'CategoryA':group_A_list, 'CategroyB':group_notA_list,
            'FactorB':item2_list, 
            'pvalue':p_list,'SE':se_list
        })    

    return(df_result_category)

def feature_association_numeric_numeric(data_for_test, columns):
    df_result_category = pd.DataFrame()
    item1_list=[]
    group_A_list=[]
    item2_list=[]
    group_B_list=[]
    A_B_list=[]
    A_notB_list=[]
    notA_B_list=[]
    notA_notB_list=[]
    p_list=[]
    odds_list=[]

    category_list = []
    for item in columns:
        category_list.append(item)

    for item2 in category_list:
        if str(data_for_test.loc[:,item2].dtypes) == 'int64' or str(data_for_test.loc[:,item2].dtypes) == 'float64':  
            if len( set(data_for_test[item2])) > 10:
                
                for item1 in category_list:
                    if item1 != item2:
                        if str(data_for_test.loc[:,item1].dtypes) == 'int64' or str(data_for_test.loc[:,item1].dtypes) == 'float64':  
                    
                            array_A = data_for_test[item1].values
                    
                            array_B = data_for_test[item2].values
                            
                            temp_df = pd.DataFrame({'A':array_A, 'B':array_B })
                            temp_df = temp_df.dropna()
                        
                            if len(array_A) > 5 and len(set(array_A))>1:
                                if  len(array_B) > 5 and len(set(array_B))>1:
                                    rho, pval = scipy.stats.spearmanr(temp_df['A'].values, temp_df['B'].values)
                                    if pval <= 0.05:
                                        item1_list.append(item1)
                                        item2_list.append(item2)
                                        p_list.append(pval)
                                        odds_list.append(rho)

    df_result_category = pd.DataFrame({
            'FactorA':item1_list, 
            'FactorB':item2_list, 
            'pvalue':p_list,
            'rho':odds_list
        })    

    return(df_result_category)
