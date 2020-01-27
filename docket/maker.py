# -----------------------------------------------------------------------------
# maker.py
# read one or more files and generate a docket containing vector encodings
# (e.g. data fingerprints) of the file(s) for rapid comparison
#
# last updated: 1/27/20
#
# naming conventions:
# https://www.python.org/dev/peps/pep-0008/#prescriptive-naming-conventions
# -----------------------------------------------------------------------------

import json
import docket.overview.load as load
import docket.overview.encode as encode


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
        self.file_list = load.generate_file_list(self.files, self.file_pattern) if 'files' in kwargs else None
        # Load file data and generate file metadata
        self.file_data, self.file_metadata = load.load_data(self.file_list,
                                                            sep=self.sep,
                                                            skip_rows=self.skip_rows,
                                                            skip_cols=self.skip_cols,
                                                            has_header=self.has_header,
                                                            has_index=self.has_index)
        # Generate file encodings (e.g. fingerprints)
        self.encodings = {}
