#!/usr/bin/env python
# coding: utf-8

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

