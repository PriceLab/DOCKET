#!/bin/env python3

import argparse

import common.file_io as io
import common.maker as make
import common.utilities as util


def main(file, length=100, out='fp_out.json'):
    assert isinstance(file, str)

    # Load data from .json or .json.gz file
    data = io.load_json(file)

    # Calculate fingerprints
    data_fp = make.encode_fp(data, length)

    # Convert numpy arrays to lists for conversion to json
    data_fp = {k: v.tolist() for k, v in data_fp.items()}

    # Write data to .json or .json.gz file format
    io.write_json(data_fp, out)

    return data_fp


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='File to load')
    parser.add_argument('--L', help='Length of fingerprints', default=100)
    parser.add_argument('--out', help='Output file for fingerprint results', default='fp_out.json')
    args = parser.parse_args()

    main(args.source,
         length=int(args.L) if util.is_integer(args.L) else 100,
         out=args.out)
