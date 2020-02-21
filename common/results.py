import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_scatter_projections(data, labels):
    c1, c2, c3, c4 = data
    c1lab, c2lab, c3lab, c4lab = labels
    size = 10

    fig = plt.figure(figsize=(12, 8))
    cm = plt.cm.get_cmap('brg')
    ax1 = fig.add_subplot(221, projection='3d')
    ax1.scatter(c1, c2, c3, zdir='z', c=c4, marker='o', s=size, depthshade=False, cmap=cm, alpha=0.2)
    ax1.set_xlabel(c1lab)
    ax1.set_ylabel(c2lab)
    ax1.set_zlabel(c3lab)

    ax2 = plt.subplot(222)
    plt.scatter(c2, c3, s=size, c=c4, cmap=cm, alpha=0.2)
    ax2.set_xlabel(c2lab)
    ax2.set_ylabel(c3lab)

    ax3 = plt.subplot(223)
    plt.scatter(c1, c3, s=size, c=c4, cmap=cm, alpha=0.2)
    ax3.set_xlabel(c1lab)
    ax3.set_ylabel(c3lab)

    ax4 = plt.subplot(224)
    plt.scatter(c1, c2, s=size, c=c4, cmap=cm, alpha=0.2)
    ax4.set_xlabel(c1lab)
    ax4.set_ylabel(c2lab)

    plt.show()


def load_enrichment_results(file, min_frac_diff=0.2, p_val_cutoff=0.01):
    # Load and filter data
    data = pd.read_table(file, index_col=0, dtype={'cluster_id': str})
    data = filter_enrichment_results(data, min_frac_diff, p_val_cutoff)

    # Set multi-index with cluster group as level 1 and cluster number as level 2
    new_index = np.array([s.split('.') for s in data.cluster_id])
    data['clust_level'] = new_index[:, 0]
    data['clust_id'] = new_index[:, 1]
    data = data.set_index(['clust_level', 'clust_id'])
    data.drop(['cluster_id'], axis=1, inplace=True)

    return data.sort_index()


def filter_enrichment_results(data, min_frac_diff=0.2, p_val_cutoff=0.01):
    # Filter on p-value cutoff
    f1 = data['quantile'].values < p_val_cutoff
    f2 = data['quantile'].values > 1. - p_val_cutoff
    data = data.loc[np.logical_or(f1, f2)]

    # Filter on difference between total fraction and cluster fraction
    f = abs(data['total_fraction'] - data['attr_value_fraction']) > min_frac_diff
    data = data.loc[f]

    return data
