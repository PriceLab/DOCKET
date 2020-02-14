#!/bin/env python3

import argparse
import common.file_io as io


def main(file, out='hist_out.json'):
    assert isinstance(file, str)

    # Load data from .json or .json.gz file
    data = io.load_json(file)

    # Convenience function to collapse dict values to counts
    def collapse_unique(dict_):
        assert isinstance(dict_, dict)
        val_list = [val.lower() for val in dict_.values()]
        val_counts = {s: val_list.count(s) for s in set(val_list)}
        return val_counts

    data_counts = {k: collapse_unique(v) for k, v in data.items()}

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
