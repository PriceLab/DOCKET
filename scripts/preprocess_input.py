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
         config_base_directory=None):

    # Load configuration for I/O (or automatically generate if not provided as an input)
    io_config = io.load_io_config(file1_path=file1, file2_path=file2, base_dir=base_directory,
                                  config_path=configuration_file, config_base_dir=config_base_directory)

    # Load and merge datasets
    data = io.load_datasets_from_config(io_config)

    # Filter out low-information columns
    data = preprocess.eliminate_low_information_columns(data, 0.01)

    # Identify, separate, and save numeric and categorical columns. Numeric data will be used for clustering
    # and categorical (attribute) data will be used for enrichment analysis. Note that categorical data is
    # saved as occurrence counts (in json format)
    data_numeric, data_object = preprocess.preprocess_and_split(data, fill_na=True)

    # Save numeric data to file in row-wise and column-wise formats
    data_numeric.to_csv('rows_numeric_data.txt.gz', sep='\t', header=False)  # Row-wise
    data_numeric.T.to_csv('cols_numeric_data.txt.gz', sep='\t', header=False)  # Column-wise

    # Save categorical (attribute) data
    data_object.to_json('cols_attribute_data.json.gz', orient='columns')

    # Save counts of value occurrences (in json format)
    data_object = preprocess.tabular2json(data_object.values, data_object.index, data_object.columns,
                                          by_col=True, pad_rows=False)
    data_object = preprocess.generate_occurrence_counts(data_object)
    io.write_json(data_object, 'cols_attribute_counts.json.gz')


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
         config_base_directory=args.base_dir)
