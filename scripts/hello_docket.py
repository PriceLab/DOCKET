import sys
import argparse
import numpy as np
from sklearn.cluster import AgglomerativeClustering

sys.path.append('.')
sys.path.append('..')
import docket
from docket.plugins.fingerprint import json2fp

parser = argparse.ArgumentParser()

# File IO arguments
parser.add_argument('--files', help='Input file')
parser.add_argument('--out', help='Outfile base', default='output')

# Fingerprint arguments
parser.add_argument('--L', help='Fingerprint length', default=100)
parser.add_argument('--norm', help='Normalize', default=0)

# File processing arguments
parser.add_argument('--skip_rows', help='Rows to skip before reading data', default='#')
parser.add_argument('--skip_cols', help='Columns to skip before reading data', default=0)
parser.add_argument('--has_index', help='True if there are row labels', default=False)
parser.add_argument('--has_header', help='True if there are column labels', default=False)

args = parser.parse_args()


# skip_rows can be an int (indicating number of skipped lines) or a
# str (specifying a comment character for rows to skip)
def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


docket_params = {
    'files': args.files,
    'skip_rows': int(args.skip_rows) if is_integer(args.skip_rows) else args.skip_rows,
    'skip_cols': int(args.skip_cols),
    'has_header': str(args.has_header).lower() in ('true', '1'),
    'has_index': str(args.has_index).lower() in ('true', '1')
}

dm1 = docket.DocketMaker(**docket_params)
data = dm1.file_data

for label, mdata in dm1.file_metadata.items():
    # Get contents of metadata
    file_type = mdata['file_type']
    file_path = mdata['file_path']
    num_rows = mdata['num_rows']
    num_cols = mdata['num_cols']

    # Print summary of metadata
    print(f'\n----- File: {label}{file_type} -----')
    print(f'\nFile path: {file_path}')
    print(f'Number of rows: {num_rows}')
    print(f'Number of cols (set): {set(num_cols)}')

    # Convert tabular to json
    current_data = data[label]
    current_data = [[val.lower() for val in row] for row in current_data]
    json_data = docket.transform.tabular2json(current_data, mdata['row_labels'], mdata['col_labels'])

    # Get original data (for later use)
    level1_headers = list(json_data.keys())
    level2_headers = list(json_data[level1_headers[0]].keys())
    original_data = [[v for k, v in json_data[header].items()] for header in level1_headers]

    # Convenience function for generating fingerprints
    def encode_fp(encoder, data_sets):
        encodings = {}
        for data_label, data_ in data_sets.items():
            encoder.recurse_structure(data_)
            encodings[data_label] = encoder.fp
            encoder.reset()
        return encodings

    # Calculate fingerprints
    fp1 = json2fp.DataFingerprint(**{'length': int(args.L)})
    fingerprints = encode_fp(fp1, json_data)

    # Convert to numpy array for analysis
    fp_array = np.array([data for _, data in fingerprints.items()])

    # Perform hierarchical clustering
    cluster = AgglomerativeClustering(n_clusters=5, affinity='euclidean', linkage='ward')
    cluster.fit_predict(fp_array)

    # Sort according to label and write to output
    sort_idx = np.argsort(cluster.labels_)
    for i in sort_idx:
        print(f'{level1_headers[i]}: ' + ' '.join(original_data[i]))

print('\ndone')
