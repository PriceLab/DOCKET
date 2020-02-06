import json
import argparse
import common.load as load
import common.transform as transform


def main(file, comment='//', rows_out='rows_out.json', cols_out='cols_out.json'):
    assert isinstance(file, str)
    data, metadata = load.load_data(file, skip_rows=comment)

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
    parser.add_argument('--comment', help='File to load', default='//')
    parser.add_argument('--rows_out', help='Output file for row data', default='rows_out.json')
    parser.add_argument('--cols_out', help='Output file for column data', default='cols_out.json')
    args = parser.parse_args()

    main(args.source, args.comment, args.rows_out, args.cols_out)
