import os
import sys
sys.path.append('..')
import docket

print("\nAvailable in docket namespace:")
docket_ns = [s for s in dir(docket) if not s.startswith('__')]
for s in docket_ns:
    print(f'-- {s}')

print("\nAvailable in docket.dfp namespace:")
docket_dfp_ns = [s for s in dir(docket.dfp) if not s.startswith('__')]
for s in docket_dfp_ns:
    print(f'-- {s}')

docket_params = {
    'files': './data/sample/hello_docket/hello_docket_full.txt',
    'pattern': '.txt',
    'skip_rows': 2,
    'skip_cols': 2,
    'has_header': False,
    'has_index': False
}

dm1 = docket.DocketMaker(**docket_params)

for file_root, mdata in dm1.file_metadata.items():
    # Get contents of metadata
    file_type = mdata['file_type']
    file_path = mdata['file_path']
    num_rows = mdata['num_rows']
    num_cols = mdata['num_cols']

    # Print summary of metadata
    print(f'\n----- File: {file_root}{file_type} -----')
    print(f'File path: {file_path}')
    print(f'Number of rows: {num_rows}')
    print(f'Number of cols (set): {set(num_cols)}')
    print('Skipped lines:')
    for row in mdata['skipped_lines']:
        print(row)
    print('Data sample:')
    for i, row in enumerate()

print('done')
