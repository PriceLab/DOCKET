#!/bin/env python3

import gzip
import json
import argparse
import pandas as pd
import common.transform as transform


def main(file, sep=None, comment=None,
         rows_out='rows_out.json.gz', cols_out='cols_out.json.gz'):
    assert isinstance(file, str)

    # Read data as a data frame
    data = pd.read_csv(file, sep=sep, index_col=0)

    # Get row and column labels
    row_labels = list(data.index)
    col_labels = list(data.columns)

    # Convert to list of lists for subsequent processing
    data = data.values

    # Get data row-wise and column-wise in json format
    rowwise_data = transform.tabular2json(data, row_labels, col_labels, by_col=False, pad_rows=False)
    colwise_data = transform.tabular2json(data, row_labels, col_labels, by_col=True, pad_rows=True)

    # Write row-wise json
    if rows_out.split('.')[-1] == 'gz':
        with gzip.GzipFile(rows_out, 'w') as f:
            f.write(json.dumps(rowwise_data).encode('utf-8'))
    else:
        with open(rows_out, 'w') as f:
            f.write(json.dumps(rowwise_data))

    # Write column-wise json
    if cols_out.split('.')[-1] == 'gz':
        with gzip.GzipFile(cols_out, 'w') as f:
            f.write(json.dumps(colwise_data).encode('utf-8'))
    else:
        with open(cols_out, 'w') as f:
            f.write(json.dumps(colwise_data))

    return rowwise_data, colwise_data


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--infile', help='File to load')
    parser.add_argument('--sep', help='Delimiter to use', default=None)
    parser.add_argument('--comment', help='Comment line character', default=None)
    parser.add_argument('--rows_out', help='Output file for row data', default='rows_out.json.gz')
    parser.add_argument('--cols_out', help='Output file for column data', default='cols_out.json.gz')
    args = parser.parse_args()

    main(args.infile,
         sep=None if args.sep is None else bytes(args.sep, "utf-8").decode("unicode_escape"),
         comment=args.comment,
         rows_out=args.rows_out,
         cols_out=args.cols_out)
