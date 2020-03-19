import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from cyjupyter import Cytoscape


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


def load_enrichment_results(file, min_frac_diff=None, p_val_cutoff=None):
    # Load enrichment results
    data = pd.read_table(file, index_col=0, dtype={'cluster_id': str})

    # Optionally filter enrichment results on fraction difference and/or significance (p-value)
    data = filter_enrichment_results(data, min_frac_diff, p_val_cutoff)

    # Set multi-index with cluster group as level 1 and cluster number as level 2
    new_index = np.array([s.split('.') for s in data.cluster_id])
    data['clust_level'] = new_index[:, 0]
    data['clust_id'] = new_index[:, 1]
    data = data.set_index(['clust_level', 'clust_id'])
    data.drop(['cluster_id'], axis=1, inplace=True)

    return data.sort_index()


def filter_enrichment_results(data, min_frac_diff=None, p_val_cutoff=None):
    # Optionally, filter on p-value cutoff
    if p_val_cutoff is not None:
        f1 = data['quantile'].values < p_val_cutoff
        f2 = data['quantile'].values > 1. - p_val_cutoff
        data = data.loc[np.logical_or(f1, f2)]

    # Optionally, filter on difference between total fraction and cluster fraction
    if min_frac_diff is not None:
        f = abs(data['total_fraction'] - data['attr_value_fraction']) > min_frac_diff
        data = data.loc[f]

    return data


def generate_graph_visualization(data, annotate='Drug_Name'):
    # Convenience function for generating node and edge lists
    def create_nodes_and_edge(gene_label, drug_label, edge_value, idx):
        gene_node = {'data': {'id': gene_label, 'color': 'yellow', 'shape': 'ellipse'}}
        drug_node = {'data': {'id': drug_label, 'color': 'grey', 'shape': 'rectangle'}}
        edge_color = 'red' if edge_value >= 0 else 'black'
        edge = {'data': {'id': f'edge{idx}', 'source': gene_label, 'target': drug_label, 'type': edge_color}}
        return gene_node, drug_node, edge

    # Generate node and edge lists
    nodes_and_edges = [create_nodes_and_edge(f1, data[annotate].iloc[i], data['SE'].iloc[i], i)
                       for i, f1 in enumerate(data['F1'])]
    nodes_and_edges = pd.DataFrame(nodes_and_edges, columns=['genes', 'drugs', 'edges'])
    nodes_list = list(nodes_and_edges.genes) + list(nodes_and_edges.drugs)
    edges_list = list(nodes_and_edges.edges)

    # Specify styles for nodes and edges
    cy_style = [{'selector': 'node',
                 'style': {'background-color': 'data(color)',
                           'label': 'data(id)',
                           'width': 12,
                           'height': 12,
                           'shape': 'data(shape)',
                           'color': 'grey',
                           'font-weight': 400,
                           'text-halign': 'middle',
                           'text-valign': 'bottom',
                           'font-size': 6,
                           'size': 3}},
                {'selector': 'edge',
                 'style': {'width': 1,
                           'line-color': 'data(type)',
                           'target-arrow-color': '#37474F',
                           'target-arrow-shape': 'triangle'}}]

    # Create and return graph
    cy_data = {'elements': {'nodes': nodes_list, 'edges': edges_list}}
    return Cytoscape(data=cy_data, visual_style=cy_style, background='#FFFFFF')
