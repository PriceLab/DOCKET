#!/bin/env python3

import json
import argparse
import common.load as load
import common.transform as transform
import common.utilities as utilities


def main(file, comment=None, sep=None,
         has_header=False, has_index=False,
         skip_rows=0, skip_cols=0,
         rows_out='rows_out.json', cols_out='cols_out.json'):
    assert isinstance(file, str)
    skip_or_comment = comment if (comment is not None) else skip_rows
    data, metadata = load.load_data(file,
                                    skip_rows=skip_or_comment, skip_cols=skip_cols,
                                    sep=sep, has_index=has_index, has_header=has_header)

    # Get row and column labels
    row_labels = metadata['row_labels']
    col_labels = metadata['col_labels']

    # Get data row-wise and column-wise in json format
    rowwise_data = transform.tabular2json(data, row_labels, col_labels, by_col=False, pad_rows=True)
    colwise_data = transform.tabular2json(data, row_labels, col_labels, by_col=True, pad_rows=True)

    with open(rows_out, 'w') as f1:
        f1.write(json.dumps(rowwise_data))

    with open(cols_out, 'w') as f2:
        f2.write(json.dumps(colwise_data))

    return rowwise_data, colwise_data


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='File to load')
    parser.add_argument('--comment', help='File to load', default=None)
    parser.add_argument('--sep', help='Delimiter to use', default=None)
    parser.add_argument('--has_header', help='True if file contains a header row', default=False)
    parser.add_argument('--has_index', help='True if file contains an index columns', default=False)
    parser.add_argument('--skip_rows', help='Number of rows to skip', default=0)
    parser.add_argument('--skip_cols', help='Number of columns to skip', default=0)
    parser.add_argument('--rows_out', help='Output file for row data', default='rows_data.json')
    parser.add_argument('--cols_out', help='Output file for column data', default='cols_data.json')
    args = parser.parse_args()

    main(args.source,
         comment=args.comment,
         sep=None if args.sep is None else bytes(args.sep, "utf-8").decode("unicode_escape"),
         has_header=utilities.str2bool(args.has_header),
         has_index=utilities.str2bool(args.has_index),
         skip_rows=int(args.skip_rows) if utilities.is_integer(args.skip_rows) else args.skip_rows,
         skip_cols=int(args.skip_cols) if utilities.is_integer(args.skip_cols) else 0,
         rows_out=args.rows_out,
         cols_out=args.cols_out)
