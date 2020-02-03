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
# Encode data as fingerprint vectors. First use load_data, defined in
# load.py. Then, pass data and metadata to this function. If by_row is
# True, encode the rows as fingerprints. Otherwise, encode the columns.
#
# -------------------------------------------------------------------------
def encode_fp(data, metadata, by_col=False, pad_rows=True):
    # Data and metadata are required to proceed
    if data is None or metadata is None:
        return {}

    # For .json files, data should be joined
    file_type = metadata['file_type']
    if file_type == '.json':
        json_data = '\n'.join(data)
    # For tabular, make sure rows have same number of items (pad, if necessary)
    else:
        col_labels = metadata['col_labels']

        # Pad rows to have same number of items as column labels list
        data = pad_tabular_data(data, pad_value='')

    # Transform tabular data to json
    json_data = tabular2json(data, metadata['row_labels'], metadata['col_labels'], by_col, pad_rows)

    # TO-DO: CALL FINGERPRINT FUNCTION

    return json_data
