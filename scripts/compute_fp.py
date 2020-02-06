import json
import argparse

import common.transform as transform


def main(file, length=100, out='fp_out.json'):
    assert isinstance(file, str)

    with open(file, 'r') as fin:
        json_data = json.loads(fin.read())

    # Calculate fingerprints
    data_fp = transform.encode_fp(json_data, length)

    # Convert numpy arrays to lists for conversion to json
    data_fp = {k: v.tolist() for k, v in data_fp.items()}

    with open(out, 'w') as fout:
        fout.write(json.dumps(data_fp))

    return data_fp


if __name__ == '__main__':
    # Parse command-line inputs
    parser = argparse.ArgumentParser()

    # File IO arguments
    parser.add_argument('--source', help='File to load')
    parser.add_argument('--L', help='Length of fingerprints', default=100)
    parser.add_argument('--out', help='Output file for fingerprint results', default='fp_out.json')
    args = parser.parse_args()

    main(args.source, args.L, args.out)
