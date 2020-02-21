#!/bin/env python3

import argparse
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import common.utilities as util


def main(file, out='cols_data_pca.pca.gz', n_comp=20):
    assert isinstance(file, str)

    # Load data on which to compute pca
    data = pd.read_table(file, index_col=0, header=None)

    # Use data index as labels
    labels = data.index

    # Get data as numpy array
    values = data.values

    # Normalize data and perform PCA
    values = StandardScaler().fit_transform(values)
    pca = PCA(n_components=min(n_comp, min(values.shape)))
    weights = pca.fit_transform(values)

    # Write PCA results to tabular file format
    data_out_df = pd.DataFrame({k: v.tolist() for k, v in zip(labels, weights)})
    data_out_df = data_out_df.T
    data_out_df.to_csv(out, sep='\t', header=False)

    return data_out_df


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='File to load')
    parser.add_argument('--out', help='Output file for PCA results', default='cols_data_pca.pca.gz')
    parser.add_argument('--n_comp', help='Number of PCA components', default=20)
    args = parser.parse_args()

    main(args.source,
         out=args.out,
         n_comp=int(args.n_comp) if util.is_integer(args.n_comp) else 10)
