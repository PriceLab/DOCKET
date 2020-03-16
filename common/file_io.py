# -----------------------------------------------------------------------------
# file_io.py
# functions for reading and writing files in various formats (e.g. json, txt, gz)
#
# last updated: 2/13/20
# -----------------------------------------------------------------------------

import os
import re
import gzip
import json
import pandas as pd


# -------------------------------------------------------------------------
# generate_file_list
# From a file path, folder path, or a list of file and/or folder paths
# generate a list of files to be loaded, optionally filtering by a
# specified pattern (will load only files with matching pattern)
#
# -------------------------------------------------------------------------
def generate_file_list(file_path, pattern=None):
    file_list = []
    if isinstance(file_path, list):
        # Loop over items of list
        for p in file_path:
            # Append file paths to list
            file_list += generate_file_list(p, pattern)
    elif isinstance(file_path, str):
        # Recurse into folders
        if os.path.isdir(file_path):
            for p in os.listdir(file_path):
                file_list += generate_file_list(f'{file_path}/{p}', pattern)
        elif os.path.isfile(file_path):
            if pattern:
                match = None
                try:
                    pattern = re.compile(pattern)
                    match = pattern.search(file_path)
                except re.error:
                    print(f'Invalid regular expression: {pattern}')
                if match:
                    file_list.append(file_path)
            else:
                file_list.append(file_path)
    return file_list


# -------------------------------------------------------------------------
# load_json
# Load json data from .json or .json.gz file
#
# -------------------------------------------------------------------------
def load_json(file):
    if file.split('.')[-1] == 'gz':
        with gzip.GzipFile(file, 'r') as f:
            data = json.loads(f.read().decode('utf-8'))
    else:
        with open(file, 'r') as f:
            data = json.loads(f.read())
    return data


# -------------------------------------------------------------------------
# write_json
# Write json data to .json or .json.gz file format
#
# -------------------------------------------------------------------------
def write_json(data, out_file):
    if out_file.split('.')[-1] == 'gz':
        with gzip.GzipFile(out_file, 'w') as f:
            f.write(json.dumps(data).encode('utf-8'))
    else:
        with open(out_file, 'w') as f:
            f.write(json.dumps(data))


# Load (or generate) configuration for file I/O (supports 1 or more input files). If there are more than 2 input files,
# user can specify paths and file I/O settings for additional files in the configuration file located at config_path.
def load_io_config(file1_path=None, file2_path=None, base_dir=None, config_path=None, config_base_dir=None):
    assert isinstance(file1_path, str) or isinstance(file2_path, str) or isinstance(config_path, str)

    # Specify full list of file load settings
    index = ['path', 'sep', 'index_col', 'header', 'comment']
    default_settings = [None, '\t', 0, 0, None]

    # Load or generate file I/O configuration
    config = {}
    # Get file1 path, if provided
    if isinstance(file1_path, str):
        file1_path = file1_path if base_dir is None else f'{base_dir}/{file1_path}'
        config["f1"] = {"path": file1_path}

    # Get file2 path, if provided
    if isinstance(file2_path, str):
        file2_path = file2_path if base_dir is None else f'{base_dir}/{file2_path}'
        config["f2"] = {"path": file2_path}

    # Initialize default file I/O settings
    for _, f_config in config.items():
        for k, v in zip(index, default_settings):
            if k == "path":
                continue
            else:
                f_config[k] = v

    # Get additional settings from file I/O configuration file, if provided
    if isinstance(config_path, str):
        # Prepend base directory path, if provided, and load the configuration file
        config_path = config_path if config_base_dir is None else f'{config_base_dir}/{config_path}'
        loaded_config = load_json(config_path)

        # Get default file I/O settings, if available
        if "default" in list(loaded_config.keys()):
            defaults = loaded_config["default"]
            del loaded_config["default"]
        else:
            defaults = {}

        # Merge loaded configuration with existing
        existing_file_list = list(config.keys())

        # Add new files to config list and set file I/O settings for new and existing files
        for f_id, f_config in loaded_config.items():
            if f_id not in existing_file_list:
                # Create an entry for new file
                config[f_id] = {"path": None}

            # Get file path, if provided
            if "path" in list(f_config.keys()):
                f_path = f_config["path"]
                config[f_id]["path"] = f_path if base_dir is None else f'{base_dir}/{f_path}'

            # Set file I/O settings
            for k, v in zip(index, default_settings):
                if k == "path":
                    continue
                elif k in list(f_config.keys()):
                    config[f_id][k] = f_config[k]
                elif k in list(defaults.keys()):
                    config[f_id][k] = defaults[k]
                else:
                    config[f_id][k] = v

    # Load information about files to read and preprocess
    config = pd.DataFrame(config, index=index)

    return config


# Load data from a file based on specified configuration (assumes that load_io_config has been called)
def load_file_data_from_config(config):
    path, sep, index_col, header, comment = config

    if path is None:
        print('Error: Null file path provided! Cannot load file.')
        return None

    # Set file load parameters
    sep = '\t' if pd.isnull(sep) else sep
    index_col = None if pd.isnull(index_col) else index_col
    header = None if pd.isnull(header) else header
    comment = None if pd.isnull(comment) else comment

    # Load data
    data = pd.read_csv(path, sep=sep, index_col=index_col, header=header, comment=comment)

    # For duplicate index values, drop all but the first row
    data = data.loc[~data.index.duplicated(keep='first')]

    return data


# Load data from a files based on specified configuration (assumes that load_io_config has been called)
def load_datasets_from_config(io_config):
    # Load data sets, eliminating low-information columns
    file_ids = io_config.columns
    datasets = {}
    for file_id in file_ids:
        data = load_file_data_from_config(io_config[file_id])
        datasets[file_id] = data

    # Merge data sets
    data = datasets[file_ids[0]]
    for file_id in file_ids[1:]:
        data = data.merge(datasets[file_id], how='outer', left_index=True, right_index=True,
                          sort=True, suffixes=('_1', '_2'))

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


# -------------------------------------------------------------------------
# load_data
# Load data from the specified file path.
#
# -------------------------------------------------------------------------
def load_data(file_path, sep=None, skip_rows=None, skip_cols=0, has_header=False, has_index=False):
    assert(isinstance(file_path, str))

    # Get file extension
    name, ext = os.path.splitext(file_path)

    # Unzip, if necessary
    if ext == '.gz':
        # data ends up in binary format
        with gzip.open(file_path, 'r') as f:
            data = f.read()

        # Now get the file type
        name, ext = os.path.splitext(name)

    # Otherwise, read file contents in binary format
    else:
        with open(file_path, 'rb') as f:
            data = f.read()

    # Read binary data with expected file format
    data = json.loads(data) if ext == '.json' else data.decode()

    # Split on line endings for convenience in subsequent processing
    data = data.split('\n')

    # Separate out skipped rows
    if isinstance(skip_rows, str):
        skipped_lines = [row for row in data if row.startswith(skip_rows)]
        data = [row for row in data if not row.startswith(skip_rows)]
    elif isinstance(skip_rows, int):
        skipped_lines = data[:skip_rows]
        data = data[skip_rows:]
    else:
        skipped_lines = []

    # Save column labels, if available
    col_labels = data[0] if has_header and len(data) > 0 else ''

    # Override specified separator if csv
    if ext == '.csv':
        sep = ','

    # Get data rows
    if has_header:
        data = data[1:]

    # Generate default row labels
    row_labels = [f'R{i}' for i in range(len(data))]

    if ext == '.json':
        num_cols = 1
        col_labels = [col_labels] if isinstance(col_labels, str) else []
    else:
        # Split each row of data and get row labels if available
        data = [row.split() if sep is None else row.split(sep) for row in data]
        if has_index:
            # Get row labels
            row_labels = [row[skip_cols] if len(row) > skip_cols else f'R{i}' for i, row in enumerate(data)]

        # Get data to the right of skipped columns
        data = [row[skip_cols+1:] if has_index else row[skip_cols:] for row in data]

        # Get number of items in each row
        num_cols = [len(row) for row in data]
        max_cols = max(num_cols) if len(num_cols) > 0 else 0

        # Generate column labels
        col_labels = col_labels.split() if sep is None else col_labels.split(sep)
        if has_header and len(col_labels) > max_cols:
            col_labels = col_labels[-max_cols:]
        else:
            col_labels = [f'C{i}' for i in range(max_cols)]

    # Generate metadata
    metadata = dict()
    metadata['file_path'] = file_path
    metadata['file_type'] = ext
    metadata['num_rows'] = len(data)
    metadata['num_cols'] = num_cols
    metadata['row_labels'] = row_labels
    metadata['col_labels'] = col_labels
    metadata['skipped_lines'] = skipped_lines

    return data, metadata
