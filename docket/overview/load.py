# -----------------------------------------------------------------------------
# load.py
# read one or more files into a format ready to transform and analyze
#
# last updated: 1/28/20
#
# naming conventions:
# https://www.python.org/dev/peps/pep-0008/#prescriptive-naming-conventions
# -----------------------------------------------------------------------------

import os
import re
import gzip
import json


# -------------------------------------------------------------------------
# generate_file_list
# From a file path, folder path, or a list of file and/or folder paths
# generate a list of files to be loaded, optionally filtering by a
# specified pattern (will load only files with matching pattern)
#
# -------------------------------------------------------------------------
def generate_file_list(path, pattern=None):
    file_list = []
    if isinstance(path, list):
        # Loop over items of list
        for p in path:
            # Append file paths to list
            file_list += generate_file_list(p, pattern)
    elif isinstance(path, str):
        # Recurse into folders
        if os.path.isdir(path):
            for p in os.listdir(path):
                file_list += generate_file_list(f'{path}/{p}', pattern)
        elif os.path.isfile(path):
            if pattern:
                match = None
                try:
                    pattern = re.compile(pattern)
                    match = pattern.search(path)
                except re.error:
                    print(f'Invalid regular expression: {pattern}')
                if match:
                    file_list.append(path)
            else:
                file_list.append(path)
    return file_list


# -------------------------------------------------------------------------
# load_data
# Load data from all files in the provided file list. To generate a file
# list (for which the existence of all files has been confirmed) from a
# mixed list of file and folder paths, first use generate_file_list
#
# -------------------------------------------------------------------------
def load_data(file_list, sep=None, skip_rows=0, skip_cols=0, has_header=False, has_index=False):
    if file_list is None:
        print("Invalid file provided")
        return None

    # Make sure the input is a list
    if isinstance(file_list, str):
        file_list = [file_list]

    # Load file data and generate metadata
    file_data = {}
    file_metadata = {}
    for file in file_list:
        # Get file extension
        name, ext = os.path.splitext(file)

        # Unzip, if necessary
        if ext == '.gz':
            # data ends up in binary format
            with gzip.open(file, 'r') as f:
                data = f.read()

            # Now get the file type
            name, ext = os.path.splitext(name)

        # Otherwise, read file contents in binary format
        else:
            with open(file, 'rb') as f:
                data = f.read()

        # Get root of file name
        name_root = os.path.basename(name)

        # Read binary data with expected file format
        data = json.loads(data) if ext == '.json' else data.decode()

        # Split on line endings for convenience in subsequent processing
        data = data.split('\n')

        # Save skipped lines and save column labels, if available
        skipped_lines = data[:skip_rows]
        col_labels = data[skip_rows] if has_header and len(data) > skip_rows else ''

        # Override specified separator if csv
        if ext == '.csv':
            sep = ','

        # Get data rows (i.e. non-skipped and non-header rows)
        data = data[skip_rows+1:] if has_header else data[skip_rows:]

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
            if has_header:
                col_labels = col_labels.split() if sep is None else col_labels.split(sep)
                diff = max_cols-len(col_labels)
                col_labels = [f'C{i}' if i < diff else col_labels[i-max(0, diff)] for i in range(max_cols)]
            else:
                col_labels = [f'C{i}' for i in range(max_cols)]

        # Generate metadata
        metadata = dict()
        metadata['file_path'] = file
        metadata['file_type'] = ext
        metadata['num_rows'] = len(data)
        metadata['num_cols'] = num_cols
        metadata['row_labels'] = row_labels
        metadata['col_labels'] = col_labels
        metadata['skipped_lines'] = skipped_lines

        file_data[name_root] = data
        file_metadata[name_root] = metadata

    return file_data, file_metadata
