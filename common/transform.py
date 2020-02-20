# -----------------------------------------------------------------------------
# transform.py
# Transform data loaded from file into a format that is ready for analysis
# and summary (first use load_data, defined in file_io.py)
#
# Last updated: 1/31/20
#
# Naming conventions:
# https://www.python.org/dev/peps/pep-0008/#prescriptive-naming-conventions
# -----------------------------------------------------------------------------
import numpy as np


# -------------------------------------------------------------------------
# pad_tabular_data
# Make sure rows of tabular data all contain the same number of items.
# Data are expected as a list of lists. If pad_size is None, pad all rows to
# the size of the one with the most items. If pad_value is None, pad rows
# with 0. (float).
#
# -------------------------------------------------------------------------
def pad_tabular_data(data, pad_size=None, pad_value=None):
    # Default pad size is length of longest row
    if pad_size is None:
        pad_size = max([len(row) for row in data])

    # Default pad value is zero
    if pad_value is None:
        pad_value = 0.

    # Utility function to pad a single row
    def pad_row(row, size, value):
        return row + [value] * (size - len(row))

    data = [pad_row(row, pad_size, pad_value) for row in data]
    return data


# -------------------------------------------------------------------------
# tabular2json
# Convert tabular (list of lists) data to json (dictionary of dictionaries).
# If by_row is True, first-level keys in the resulting dictionary are row
# labels and second-level keys are column labels. Otherwise, this is
# reversed (first-level keys are column labels and second-level keys are
# row labels)
#
# -------------------------------------------------------------------------
def tabular2json(data, row_labels, col_labels, by_col=False, pad_rows=True):
    # json will have level 1 and level 2 labels
    level1_labels = row_labels
    level2_labels = col_labels

    if isinstance(data, np.ndarray):
        data = data.astype(str).tolist()

    if pad_rows:
        # Pad rows to size of longest row
        pad_size = max([len(row) for row in data])
        data = pad_tabular_data(data, pad_size, pad_value='')

    # If converting to json by column, data must be transposed
    if by_col:
        # Must not proceed if rows are different lengths
        if len(set([len(row) for row in data])) > 1:
            print('Warning: Rows are different lengths! Cannot convert to JSON column-wise.')
            return {}

        level1_labels = col_labels
        level2_labels = row_labels
        data = [[data[i][j] for i in range(len(level2_labels))] for j in range(len(level1_labels))]

    second_level = [{str(k): v for k, v in list(zip(level2_labels, data[i]))} for i in range(len(level1_labels))]
    json_data = {str(level1_labels[i]): d for i, d in enumerate(second_level)}

    return json_data


# Generate a dictionary of value occurrence counts
def generate_occurrence_counts(data):
    assert(isinstance(data, dict))

    # Convenience function to collapse dict values to counts
    def collapse_unique(dict_):
        assert isinstance(dict_, dict)
        val_list = [val.lower() for val in dict_.values()]
        val_counts = {s: val_list.count(s) for s in set(val_list)}
        return val_counts

    return {k: collapse_unique(v) for k, v in data.items()}
