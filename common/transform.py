# -----------------------------------------------------------------------------
# transform.py
# Transform data loaded from file into a format that is ready for analysis
# and summary (first use load_data, defined in load.py)
#
# Last updated: 1/31/20
#
# Naming conventions:
# https://www.python.org/dev/peps/pep-0008/#prescriptive-naming-conventions
# -----------------------------------------------------------------------------

import common.utilities as utilities
import common.json2fp as json2fp


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

    # If converting to json by column, rows must be the same lengths
    if by_col:
        if pad_rows is False:
            # Notify that pad_rows will be ignored and data will be padded
            print('\nWarning: When converting by column, rows must be padded.')
            print('Padding rows to size of longest row...')

        # Pad rows to size of longest row
        pad_size = max([len(row) for row in data])
        data = pad_tabular_data(data, pad_size, pad_value='')

        # Transpose data
        level1_labels = col_labels
        level2_labels = row_labels
        data = [[data[i][j] for i in range(len(level2_labels))] for j in range(len(level1_labels))]

    else:  # Convert to json by row
        if pad_rows:
            # Pad rows to size of longest row
            pad_size = max([len(row) for row in data])
            data = pad_tabular_data(data, pad_size, pad_value='')

    second_level = [{k: v for k, v in list(zip(level2_labels, row))} for row in data]
    json_data = {level1_labels[i]: d for i, d in enumerate(second_level)}

    return json_data


# -------------------------------------------------------------------------
# encode_fp
# Encode data as fingerprint vectors. Data are expected in a tabular json
# format (dictionary of dictionaries). See description of tabular2json
# function for details.
#
# -------------------------------------------------------------------------
def encode_fp(data_in, length):
    # Check that data is in proper format
    assert isinstance(data_in, dict)
    for k, v in data_in.items():
        assert isinstance(v, dict)

    # Check that length is an int or can be converted to an int
    assert utilities.is_integer(length)

    # Calculate fingerprints
    fp_data = {}
    dfp = json2fp.DataFingerprint(**{'length': int(length)})
    for label, data in data_in.items():
        dfp.recurse_structure(data)
        fp_data[label] = dfp.fp
        dfp.reset()

    return fp_data
