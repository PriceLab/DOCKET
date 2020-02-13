#!/bin/env python3

import json
import gzip
import argparse


def main(file, out='hist_out.json'):
    assert isinstance(file, str)

    # Load data
    if file.split('.')[-1] == 'gz':
        with gzip.GzipFile(file, 'r') as f:
            data = json.loads(f.read().decode())
    else:
        with open(file, 'r') as f:
            data = json.loads(f.read())

    # Convenience function to collapse dict values to counts
    def collapse_unique(dict_):
        assert isinstance(dict_, dict)
        val_list = [val.lower() for val in dict_.values()]
        val_counts = {s: val_list.count(s) for s in set(val_list)}
        return val_counts

    data_counts = {k: collapse_unique(v) for k, v in data.items()}

    # Write data to json file
    if out.split('.')[-1] == 'gz':
        with gzip.GzipFile(out, 'w') as f:
            f.write(json.dumps(data_counts).encode('utf-8'))
    else:
        with open(out, 'w') as f:
            f.write(json.dumps(data_counts))

    return data_counts


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='File to load')
    parser.add_argument('--out', help='Output file for histogram data', default='hist_out.json')
    args = parser.parse_args()

    main(args.source, args.out)
