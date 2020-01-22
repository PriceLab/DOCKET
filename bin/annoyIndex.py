#!/bin/env python3
import sys, argparse
from annoy import AnnoyIndex
import re

parser=argparse.ArgumentParser()
parser.add_argument('--file', help='Input file')
parser.add_argument('--out', help='Outfile base')
parser.add_argument('--L', help='Fingerprint length')
args=parser.parse_args()

a = AnnoyIndex(int(args.L))
i = 0
names = []

with open(args.file, 'r') as f:
	for line in f:
		id, statements, *v = line.split("\t")
		id = re.sub('.json.gz', '', id)
		id = re.sub('\.', '|', id)
		a.add_item(i, [float(j) for j in v])
		names.append(id)
		i = i+1

a.build(-1)
a.save(args.out + '.tree')

with open(args.out + '.names', 'w') as f:
	for item in names:
		f.write("%s\n" % item)
