import numpy as np
import pandas as pd


# Load data and remove low-information columns
# config: Series containing file information (path, separator, etc)
# filter_frac: Remove columns for which fraction of missing values is >= 1 - filter_frac
def load_and_eliminate(config, filter_frac=0.2, base_dir=None):
    # Get file load parameters
    path, sep, index_col, header = config
    path = path if base_dir is None else f'{base_dir}/{path}'
    sep = ',' if pd.isnull(sep) else sep
    index_col = None if pd.isnull(index_col) else index_col
    header = None if pd.isnull(header) else header

    # Load data
    data = pd.read_csv(path, sep=sep, index_col=index_col, header=header)
    nrows, ncols = data.shape

    # Get information to be used in eliminating low-information columns
    unique_value_counts = np.array([len(data[col].unique()) for col in data.columns])
    null_counts = np.array([sum(data[col].isnull()) for col in data.columns])

    # Eliminate low-information columns
    keep_condition = np.array(unique_value_counts > 1) & np.array(null_counts < nrows * (1 - filter_frac))
    keep_columns = data.columns[keep_condition]
    data = data[keep_columns]

    return data


# Load data sets, eliminate low-information columns, merge and reindex (if index values are not all unique)
def load_and_merge_datasets(io_config, base_dir=None):
    # Load data sets, eliminating low-information columns
    file_ids = io_config.columns
    datasets = {}
    for file_id in file_ids:
        data = load_and_eliminate(io_config[file_id], base_dir=base_dir)
        datasets[file_id] = data

    # Merge data sets
    data = datasets[file_ids[0]]
    for file_id in file_ids[1:]:
        data = data.merge(datasets[file_id], how='left', left_index=True, right_index=True)

    idx = data.index
    idx_cnts = idx.value_counts()[idx.unique()]  # Retain original ordering
    if len(idx_cnts) < len(idx):
        # Convenience function for generating unique index ids
        def generate_unique_ids(id_, count):
            new_ids = list(zip([id_]*count, list(range(count))))
            return [f'{id1}.{id2}' for id1, id2 in new_ids]

        new_index = [generate_unique_ids(id_, cnt) if cnt > 1 else [id_] for id_, cnt in zip(idx_cnts.index, idx_cnts)]
        new_index = [idx for sublist in new_index for idx in sublist]
        data.index = new_index

    return data


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

    print(df_numeric.shape)
    print(df_object.shape)
    print(df.shape)

    # Sum of dimensions of the split dataframes must equal the dimensions of the original dataframe
    assert(df_numeric.shape[0] == df_object.shape[0] == df.shape[0])
    assert(df_numeric.shape[1] + df_object.shape[1] == df.shape[1])

    return df_numeric, df_object
