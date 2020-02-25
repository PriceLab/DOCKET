# -----------------------------------------------------------------------------
# maker.py
# read one or more files and generate a docket containing vector encodings
# (e.g. data fingerprints) of the file(s) for rapid comparison
#
# last updated: 1/29/20
#
# naming conventions:
# https://www.python.org/dev/peps/pep-0008/#prescriptive-naming-conventions
# -----------------------------------------------------------------------------

import os
import common.file_io as io
import common.preprocess as preprocess
import common.utilities as utilities
from datafingerprint import DataFingerprint


class DocketMaker:
    def __init__(self, **kwargs):
        self.files = None
        self.file_pattern = None
        self.strings = None
        # Parameters for handling file loading
        self.sep = None
        self.skip_rows = 0   # Number of rows to skip when loading
        self.skip_cols = 0   # Number of columns to skip when loading
        self.has_header = False  # True if there is a header line (following skipped rows)
        self.has_index = False   # True if there is an index column (following skipped columns)
        # Generated upon initialization
        self.file_list = None
        self.file_data = None
        self.file_metadata = None
        self.encodings = None
        self.initialize(**kwargs)

    # Define initialization outside of __init__ so that DocketMaker can be reinitialized, if desired
    def initialize(self, **kwargs):
        # Input file path list
        self.files = kwargs['files'] if 'files' in kwargs else None
        # Pattern to filter files
        self.file_pattern = kwargs['pattern'] if 'pattern' in kwargs else None
        # TO DO: Support passing of strings in addition to reading files
        self.strings = kwargs['strings'] if 'strings' in kwargs else None
        # Parameters for handling file loading
        self.sep = kwargs['sep'] if 'sep' in kwargs else None
        self.skip_rows = kwargs['skip_rows'] if 'skip_rows' in kwargs else 0
        self.skip_cols = kwargs['skip_cols'] if 'skip_cols' in kwargs else 0
        self.has_header = kwargs['has_header'] if 'has_header' in kwargs else False
        self.has_index = kwargs['has_index'] if 'has_index' in kwargs else False
        # Generate filtered (if specified) file list
        self.file_list = io.generate_file_list(self.files, self.file_pattern) if 'files' in kwargs else None
        # Load file data and generate file metadata
        self.file_data, self.file_metadata = self.load_data(self.file_list,
                                                            sep=self.sep,
                                                            skip_rows=self.skip_rows,
                                                            skip_cols=self.skip_cols,
                                                            has_header=self.has_header,
                                                            has_index=self.has_index)

    # Load data for multiple files
    def load_data(self, file_list, sep=None, skip_rows=None, skip_cols=0, has_header=False, has_index=False):
        file_data = {}
        file_metadata = {}
        for file in file_list:
            data, metadata = io.load_data(file, sep, skip_rows, skip_cols, has_header, has_index)
            # Get file name root
            name, _ = os.path.splitext(metadata['file_path'])
            label = os.path.basename(name)

            # Store file data and metadata
            file_data[label] = data
            file_metadata[label] = metadata

        return file_data, file_metadata

    # Return data set labels
    def data_labels(self):
        return list(self.file_data.keys())

    # Print specified number of rows (default: 5) of a specified data set label
    def print_data_summary(self, label, max_rows=5):
        if label not in self.data_labels():
            print(f'Data label \'{label}\' does not exist.')
            return

        for i, row in enumerate(self.file_data[label]):
            if i >= max_rows:
                break
            print('\t'.join(row))

    # Ensure that all rows in data (for a specified label) are the same length by padding
    def pad_rows(self, label, pad_size=None, pad_value=None):
        if label not in self.data_labels():
            print(f'Data label \'{label}\' does not exist.')
            return

        data = self.file_data[label]
        self.file_data[label] = preprocess.pad_tabular_data(data, pad_size, pad_value)


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
    dfp = DataFingerprint(**{'length': int(length)})
    for label, data in data_in.items():
        dfp.recurse_structure(data)
        fp_data[label] = dfp.fp
        dfp.reset()

    return fp_data
