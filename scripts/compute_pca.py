#!/bin/env python3

import argparse
import pandas as pd
from sklearn.decomposition import PCA
import common.file_io as io
import common.utilities as util


def main(file, out='pca_out.json', n_comp=10):
    assert isinstance(file, str)

    # Load fingerprint data from .json or .json.gz file
    data = pd.read_json(file)

    # Use column headers as labels
    labels = data.columns

    # Get data as numpy array and transpose
    values = data.values.transpose()

    # Perform PCA
    pca = PCA(n_components=min(n_comp, min(values.shape)))
    weights = pca.fit_transform(values)

    # Write PCA results to .json or .json.gz file format
    data_out = {k: v.tolist() for k, v in zip(labels, weights)}
    io.write_json(data_out, out)

    return data_out


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='File to load')
    parser.add_argument('--out', help='Output file for PCA results', default='pca_out.json')
    parser.add_argument('--n_comp', help='Number of PCA components', default=10)
    args = parser.parse_args()

    main(args.source,
         out=args.out,
         n_comp=int(args.n_comp) if util.is_integer(args.n_comp) else 10)
