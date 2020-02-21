#!/bin/env python3

import argparse
import common.file_io as io
import common.preprocess as preprocess
import common.transform as transform
import common.utilities as util


def main(file=None,
         file_configuration=None,
         base_directory=None,
         fill_na=True,
         rows_data='rows_numeric_data.txt.gz',
         cols_data='cols_numeric_data.txt.gz',
         attr_data='cols_attribute_data.json.gz',
         attr_counts='cols_attribute_counts.json.gz'):

    assert isinstance(file, str) or isinstance(file_configuration, str)

    # Load configuration for I/O
    io_config = io.load_io_config(file_path=file, config_path=file_configuration, base_dir=base_directory)

    # Load data sets, eliminating low-information columns
    data = preprocess.load_and_merge_datasets(io_config, base_directory)

    # Identify, separate, and save numeric and categorical columns. Numeric data will be used for clustering
    # and categorical (attribute) data will be used for enrichment analysis. Note that categorical data is
    # saved as occurrence counts (in json format)
    data_numeric, data_object = preprocess.preprocess_and_split(data, fill_na=fill_na)

    # Save numeric data to file in row-wise and column-wise formats
    data_numeric.to_csv(rows_data, sep='\t', header=False)  # Row-wise
    data_numeric.T.to_csv(cols_data, sep='\t', header=False)  # Column-wise

    # Save categorical (attribute) data
    data_object.to_json(attr_data, orient='columns')

    # Save counts of value occurrences (in json format)
    data_object = transform.tabular2json(data_object.values, data_object.index, data_object.columns,
                                         by_col=True, pad_rows=False)
    data_object = transform.generate_occurrence_counts(data_object)
    io.write_json(data_object, attr_counts)


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--file', help='Data file to load', default=None)
    parser.add_argument('--file_config', help='Configuration file to load', default=None)
    parser.add_argument('--base_dir', help='Base directory', default=None)
    parser.add_argument('--fill_na', help='If true, fill missing numeric values', default=False)
    parser.add_argument('--rows_data', help='Row-wise numeric data output file', default='rows_numeric_data.json.gz')
    parser.add_argument('--cols_data', help='Column-wise numeric data output file', default='cols_numeric_data.json.gz')
    parser.add_argument('--attr_data', help='Column-wise attribute data output file', default='cols_attribute_data.json.gz')
    parser.add_argument('--attr_counts', help='Column-wise attribute value counts (histogram) output file', default='cols_attribute_counts.json.gz')
    args = parser.parse_args()

    main(file=args.file,
         file_configuration=args.file_config,
         base_directory=args.base_dir,
         fill_na=util.str2bool(args.fill_na),
         rows_data=args.rows_data,
         cols_data=args.cols_data,
         attr_data=args.attr_data,
         attr_counts=args.attr_counts)
