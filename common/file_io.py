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
import argparse


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
                file_list += generate_file_list('/'.join(file_path,p), pattern)
        elif os.path.isfile(file_path):
            if pattern:
                match = None
                try:
                    pattern = re.compile(pattern)
                    match = pattern.search(file_path)
                except re.error:
                    print('Invalid regular expression: ',pattern)
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
    row_labels = [''.join('R',i) for i in range(len(data))]

    if ext == '.json':
        num_cols = 1
        col_labels = [col_labels] if isinstance(col_labels, str) else []
    else:
        # Split each row of data and get row labels if available
        data = [row.split() if sep is None else row.split(sep) for row in data]
        if has_index:
            # Get row labels
            row_labels = [row[skip_cols] if len(row) > skip_cols else ''.join('R',i) for i, row in enumerate(data)]

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
            col_labels = [''.join('C',i) for i in range(max_cols)]

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


def main(file):
    assert isinstance(file, str)
    data, metadata = load_data(file, skip_rows='#')
    print(json.dumps(data))
    return json.dumps(data)


if __name__ == '__main__':
    # Parse command-line inputs
    load_parser = argparse.ArgumentParser()

    # File IO arguments
    load_parser.add_argument('--source', help='File to load')
    load_args = load_parser.parse_args()

    main(load_args.source)
