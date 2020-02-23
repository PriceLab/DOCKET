import numpy as np


def get_cluster_membership(linkage_table, labels):
    nrows, _ = linkage_table.shape
    cluster_members = {}
    for i, _ in enumerate(linkage_table):
        id1, id2 = linkage_table[i, 0:2].astype(int)

        # Get membership of current clusters
        id1_list = labels[[id1]].tolist() if str(id1) not in list(cluster_members.keys()) \
            else cluster_members[str(id1)]['parent']
        id2_list = labels[[id2]].tolist() if str(id2) not in list(cluster_members.keys()) \
            else cluster_members[str(id2)]['parent']

        # Store new cluster
        cluster_members[str(nrows + i + 1)] = {
            'child1': id1_list,
            'child2': id2_list,
            'parent': sorted(id1_list + id2_list)}

    # Store labels instead of numerical indexes
    #for k, v in cluster_members.items():
    #    cluster_members[k] = labels[v].tolist()

    # Reverse cluster order and rename starting from str(0)
    old_labels = list(cluster_members.keys())
    old_labels.reverse()
    cluster_members = {str(i): cluster_members[label] for i, label in enumerate(old_labels)}

    return cluster_members
