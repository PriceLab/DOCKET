#!/bin/env python3

import argparse
import common.file_io as io
import common.preprocess as preprocess


def main(file, out='hist_out.json'):
    assert isinstance(file, str)

    # Load data from .json or .json.gz file
    data = io.load_json(file)

    # Generate "histogram" of occurrence counts as a dictionary
    data_counts = preprocess.generate_occurrence_counts(data, to_lower=True,
                                                        replace_whitespace='-', collapse_singletons=True)

    # Write data to .json or .json.gz file format
    io.write_json(data_counts, out)

    return data_counts


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='File to load')
    parser.add_argument('--out', help='Output file for histogram data', default='hist_out.json')
    args = parser.parse_args()

    main(args.source, args.out)
