#!/bin/env python3

import argparse
import common.file_io as io
import common.preprocess as preprocess


# Accepts 1 or 2 files directly as arguments (optionally) and also provides option to read in a file I/O configuration
# file that (1) may contain additional file input paths (for import) and (2) may contain file import details (such as
# separator, index column, presence or absence of a header row, comment character, etc). If two or more files are
# specified, they will automatically be merged (union). Also, for now, if there are rows with duplicate ids, import the
# first and ignore the others. Note that if output paths are provided for row-wise and column-wise json-formatted data,
# then the imported and merged data will be written to the specified output files.
def main(file1=None,
         file2=None,
         base_directory=None,
         configuration_file=None,
         config_base_directory=None,
         file_out='input_data.txt.gz',
         row_wise_out=None,
         col_wise_out=None):

    # Load configuration for I/O (or automatically generate if not provided as an input)
    io_config = io.load_io_config(file1_path=file1, file2_path=file2, base_dir=base_directory,
                                  config_path=configuration_file, config_base_dir=config_base_directory)

    # Load and merge datasets
    data = io.load_datasets_from_config(io_config)

    # Get data row-wise and column-wise in json format
    if row_wise_out is not None:
        row_wise_data = preprocess.tabular2json(data, data.index, data.columns, by_col=False)
        io.write_json(row_wise_data, row_wise_out)

    if col_wise_out is not None:
        col_wise_data = preprocess.tabular2json(data, data.index, data.columns, by_col=True)
        io.write_json(col_wise_data, col_wise_out)

    # Write merged data sets to output
    data.to_csv(file_out, sep='\t', index=True, header=True)

    return data


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--file1', help='Data file to load', default=None)
    parser.add_argument('--file2', help='Data file to load', default=None)
    parser.add_argument('--base_dir', help='Base directory for file import', default=None)
    parser.add_argument('--config_file', help='Configuration file to load', default=None)
    parser.add_argument('--config_base_dir', help='Base directory for configuration file', default=None)
    parser.add_argument('--file_out', help='imported data', default='merged_data.txt.gz')
    parser.add_argument('--row_wise_out', help='imported data in row-wise json format', default=None)
    parser.add_argument('--col_wise_out', help='imported data in column-wise json format', default=None)
    args = parser.parse_args()

    main(file1=args.file1,
         file2=args.file2,
         base_directory=args.base_dir,
         configuration_file=args.config_file,
         config_base_directory=args.base_dir,
         file_out=args.file_out,
         row_wise_out=args.row_wise_out,
         col_wise_out=args.col_wise_out)
