import numpy as np


# Convenience function to determine if count is in proper range
def in_range(val, total, frac):
    value_in_range = frac * total <= val <= (1 - frac) * total
    return value_in_range


# For a single attribute and associated value counts, generate a list of only those attribute values
# for which the occurrence counts meet specified criteria
def filter_attr_values(attribute, value_counts, fraction=0.05):
    # Shorten variable names for concise list comprehensions
    attr = attribute
    vcnt = value_counts
    f = fraction

    # Total count of occurrence values
    tot = sum(np.array(list(vcnt.values())))

    # Convenience function to replace spaces in string
    def repl(input_string):
        return '-'.join(input_string.split())

    flatten = [(f'{attr}', f'{repl(k)}', v, v/tot) for k, v in vcnt.items() if in_range(v, tot, f)]

    return flatten


# For a dictionary of attributes (each with occurrence counts of associated values), generate a list
# of all attributes/values for which the occurrence counts meet specified criteria
def get_attributes_for_enrichment(occurrence_counts, filter_fraction=0.05):
    # Shorten variable names for concise list comprehensions
    f = filter_fraction

    # Filter for attributes with sufficient occurrence counts
    keep_attributes = [filter_attr_values(attr, cnts, f) for attr, cnts in occurrence_counts.items()]

    # Flatten list of lists to a single list
    keep_attributes = [item for sublist in keep_attributes for item in sublist]

    return keep_attributes


# Convenience function to create cluster identifier (string) from cluster group, cluster id, and cluster member count
def to_cluster_id(cl_group, cl_id, cl_member_cnt):
    str_id = f'{cl_group}.{cl_id}.{cl_member_cnt}'
    return str_id


# Convenience function to parse cluster group, cluster id, and cluster member count from cluster identifier (string)
def parse_cluster_id(str_id):
    cl_group, cl_id, cl_member_count = str_id.split('.')
    cl_group = int(cl_group)
    cl_id = int(cl_id)
    cl_member_count = int(cl_member_count)
    return cl_group, cl_id, cl_member_count


# Convenience function to remove clusters that occur more than once in cluster list
def remove_repeat_clusters(clusters_, cluster_data_):
    cluster_data_ = np.array(cluster_data_)
    indexes = np.array(list(range(cluster_data_.shape[1])))

    items_to_remove = []
    cl_ids_parsed = [parse_cluster_id(cl) for cl in clusters_]
    for i, (cl_grp1, cl_id1, cnt1) in enumerate(cl_ids_parsed):
        for cl_grp2, cl_id2, cnt2 in cl_ids_parsed[i + 1:]:
            cl = to_cluster_id(cl_grp2, cl_id2, cnt2)
            if cl not in items_to_remove and cnt1 == cnt2:
                set1 = set(indexes[np.array(cluster_data_[cl_grp1]) == cl_id1])
                set2 = set(indexes[np.array(cluster_data_[cl_grp2]) == cl_id2])
                if set1 == set2:
                    items_to_remove.append(cl)

    return [id_ for id_ in clusters_ if id_ not in items_to_remove]


# Get attribute value occurrence counts and fractions for each cluster
def get_cluster_attribute_fractions(attr_data, attr_values, cl_assignments, clusters):
    # Convert values to string
    attr_data = attr_data.astype(str)
    attr_values = attr_values.astype(str)

    # Get occurrence fractions for attribute values
    occurrence_counts = {}
    occurrence_fractions = {}
    for cl in clusters:
        # Parse/split components of cluster ids (convert to int)
        cl_id, cl_label, cnt = parse_cluster_id(cl)
        cluster_data = attr_data.loc[np.array(cl_assignments[cl_id]) == cl_label]
        assert(len(cluster_data) == cnt)

        val_counts = cluster_data.value_counts()
        assert(sum(val_counts) == cnt)
        occurrence_counts[cl] = val_counts[attr_values]
        occurrence_fractions[cl] = val_counts[attr_values] / sum(val_counts)

    return occurrence_counts, occurrence_fractions


# Resample (with replacement) to get distribution of occurrence fractions
def get_resample_fractions(cluster_id, attr_data, attr_vals, num_resample):
    i, cl, cnt = parse_cluster_id(cluster_id)

    # Convert values to string
    attr_data = attr_data.astype(str)
    attr_vals = attr_vals.astype(str)

    # Convenience function to get a single sample with replacement
    def sample(data, size, vals):
        counts = data.sample(size, replace=True).value_counts()
        fractions = counts / sum(counts)
        return fractions[vals].tolist()

    resample_fractions = np.array([sample(attr_data, cnt, attr_vals) for _ in range(num_resample)])
    resample_fractions = {v: resample_fractions[:, i] for i, v in enumerate(attr_vals)}

    return resample_fractions


# Find the ordered index position of a specified value in an array of values
def get_sorted_position(value, array_of_values):
    arr = np.array(array_of_values)
    arr.sort()
    idx_pos = np.searchsorted(arr, value)
    return idx_pos
