import numpy as np
import pandas as pd


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
def tabular2json(data, row_labels, col_labels, by_col=False, pad_rows=False):
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


# Convenience function to apply string-related preprocessing steps
def string_preprocess(value, to_lower, replace_ws):
    value = value.lower() if to_lower else value
    value = value if replace_ws is None else replace_ws.join(value.split())
    return value


# Convenience function to collapse dict values to counts
def collapse_unique(key, value, based_on=None, lower=False, replace_ws=None, collapse_singletons=False):
    assert isinstance(value, dict)
    if based_on is not None:
        assert isinstance(based_on, dict)

    # Get list of values for which to get counts
    candidate_values = list(set(value.values()) if based_on is None else set(based_on[key].keys()))
    candidate_values = [string_preprocess(val, lower, replace_ws) for val in candidate_values]
    candidate_values.sort()

    # Get list of value counts
    val_list = [string_preprocess(val, lower, replace_ws) for val in list(value.values())]
    val_counts = [val_list.count(s) for s in candidate_values]

    if collapse_singletons:
        val_counts = {s: val_counts[i] for i, s in enumerate(candidate_values) if val_counts[i] > 1}
        len_diff = len(candidate_values) - len(val_counts)
        if len_diff > 0:
            key_other = string_preprocess(key, lower, replace_ws)
            val_counts[f'{key_other}.other'] = len_diff
    else:
        other_count = 0 if based_on is None else int(len(val_list) - np.array(val_counts).sum())
        val_counts = {s: val_counts[i] for i, s in enumerate(candidate_values)}
        if other_count > 0:
            key_other = string_preprocess(key, lower, replace_ws)
            val_counts[f'{key_other}.other'] = other_count

    return val_counts


# Generate a dictionary of value occurrence counts
def generate_occurrence_counts(data, based_on=None, to_lower=False,
                               replace_whitespace=None, collapse_singletons=False):
    assert(isinstance(data, dict))

    # Generate occurrence counts
    def collapse_fnc(k, v): return collapse_unique(k, v, based_on, to_lower, replace_whitespace, collapse_singletons)
    counts = {k: collapse_fnc(k, v) for k, v in data.items()}

    return counts


# Convenience function to convert string to lowercase and replace spaces with a specified character
def string_process(input_val, replace_char='-'):
    input_val = str(input_val)
    input_val = input_val.lower()
    input_val = replace_char.join(input_val.split())
    return input_val


# Convenience function to sample a random value from a normal distribution with specified mean and std
def random_norm_sample(mean, std, min_, max_):
    samp = np.random.normal(mean, std)
    while samp < min_ or samp > max_:
        samp = np.random.normal(mean, std)
    return samp


# Remove low-information columns from a dataframe
# data: Pandas dataframe
# filter_frac: Remove columns for which fraction of missing values is >= 1 - filter_frac
def eliminate_low_information_columns(data, filter_frac=None):
    filter_frac = 0.0 if filter_frac is None else filter_frac

    # Get dimensions of the data
    nrows, ncols = data.shape

    # Get information to be used in eliminating low-information columns
    unique_value_counts = np.array([len(data[col].unique()) for col in data.columns])
    null_counts = np.array([sum(data[col].isnull()) for col in data.columns])

    # Eliminate low-information columns
    keep_condition = np.array(unique_value_counts > 1) & np.array(null_counts < nrows * (1 - filter_frac))
    keep_columns = data.columns[keep_condition]
    data = data[keep_columns]

    return data


# Fill missing numerical values, convert string values to lowercase and replace spaces
# Then, split the dataset into numerical data to use for clustering and categorical (string) data
# to use for enrichment calculations
def preprocess_and_split(df, frac_threshold=0.01, fill_na=True):
    # Get dimensions of the data
    nrows, ncols = df.shape

    # Loop over columns and do the following:
    #  - Convert low-unique-value columns to string type
    #  - Make all strings lowercase and replace spaces with hyphens
    #  - Fill missing numerical values with randomly sampled values based on mean and sd of non-missing values
    for col in df.columns:
        # Get current column and number of null values in the column
        current_col = df[col]
        na_count = current_col.isnull().sum()

        if len(df[col].unique()) < nrows * frac_threshold:
            # Treat column as categorical (convert to string type)
            df[col] = df[col].astype(str)

        if df[col].dtype == 'object':
            # Convert to lowercase and replace spaces with hyphens
            df[col] = df[col].apply(string_process)
        elif fill_na and na_count > 0:
            # Fill missing numerical values with randomly sampled values (based on mean and std of non-missing values)
            stats = df[col].describe()
            mean, std, min_, max_ = stats['mean'], stats['std'], stats['min'], stats['max']
            df[col] = df[col].apply(lambda x: random_norm_sample(mean, std, min_, max_) if pd.isnull(x) else x)

    # Split into numeric and object dataframes
    df_numeric = df.select_dtypes('number')
    df_object = df.select_dtypes('object')

    # Sum of dimensions of the split dataframes must equal the dimensions of the original dataframe
    assert(df_numeric.shape[0] == df_object.shape[0] == df.shape[0])
    assert(df_numeric.shape[1] + df_object.shape[1] == df.shape[1])

    return df_numeric, df_object
