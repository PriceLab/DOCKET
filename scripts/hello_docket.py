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
print('')
for f in dm1.file_list:
    print(f)

print('done')
