#!/bin/env python3
import sys
import sys, argparse
from annoy import AnnoyIndex

parser=argparse.ArgumentParser()
parser.add_argument('--index', help='Index file')
parser.add_argument('--names', help='Names file')
parser.add_argument('--L', help='Fingerprint length')
parser.add_argument('--k', help='Number of neighbors')
args=parser.parse_args()

k = int(args.k)+1

a = AnnoyIndex(int(args.L))
a.load(args.index)

names = []
with open(args.names, 'r') as f:
    for line in f:
        parts = line.rstrip("\n\n").split(".")
        names.append(parts[0])

n = len(names)

for q in range(0,n):
    nn = a.get_nns_by_item(q, k)
    print("\t".join([names[i] for i in nn]))


