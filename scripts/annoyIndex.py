#!/bin/env python3
import sys, argparse
from annoy import AnnoyIndex
import re
import statistics

parser=argparse.ArgumentParser()
parser.add_argument('--file', help='Input file')
parser.add_argument('--out', help='Outfile base')
parser.add_argument('--L', help='Fingerprint length')
parser.add_argument('--norm', help='Normalize')
args=parser.parse_args()

a = AnnoyIndex(int(args.L))
i = 0
names = []

with open(args.file, 'r') as f:
	for line in f:
		id, statements, *v = line.split("\t")
		id = re.sub('.json.gz', '', id)
		id = re.sub('\.', '|', id)
		names.append(id)
		v = [float(j) for j in v]
		if args.norm:
		    avg = statistics.mean(v)
		    std = statistics.stdev(v)
		    v = [(j-avg)/std for j in v]
		a.add_item(i, v)
		i = i+1

a.build(-1)
a.save(args.out + '.tree')

with open(args.out + '.names', 'w') as f:
	for item in names:
		f.write("%s\n" % item)
