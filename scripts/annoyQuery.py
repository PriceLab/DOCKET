#!/bin/env python3
import sys
import sys, argparse
from annoy import AnnoyIndex

parser=argparse.ArgumentParser()
parser.add_argument('--index', help='Index file base')
parser.add_argument('--L', help='Fingerprint length')
parser.add_argument('--query', help='Query number')
parser.add_argument('--k', help='Number of neighbors')
args=parser.parse_args()

a = AnnoyIndex(int(args.L))
a.load(args.index + '.tree')

names = []
with open(args.index + '.names', 'r') as f:
    for line in f:
	    names.append(line.rstrip("\n\r"))

nn = a.get_nns_by_item(int(args.query), int(args.k))
print([names[i] for i in nn])

