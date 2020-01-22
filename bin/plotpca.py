import sys, argparse
import numpy as np
#from scipy import stats
#from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

parser=argparse.ArgumentParser()
parser.add_argument('infile', nargs='?', default=sys.stdin, help='File with PCA values')
parser.add_argument('outfile', nargs='?', default=sys.stdin, help='Where to save the plot')
parser.add_argument('--components', help='Number of components', default=10)
parser.add_argument('--c1', help='First component (x axis)', default=0)
parser.add_argument('--c2', help='Second component (y axis)', default=1)
args=parser.parse_args()
infile = args.infile
outfile = args.outfile
c = int(args.components)
c1 = int(args.c1)
c2 = int(args.c2)

# read PCA
names = np.genfromtxt(fname = infile, dtype='str', usecols = range(0, 1))
Y = np.genfromtxt(fname = infile, dtype='float', usecols = range(1, c+1))

# plot
tp = np.array(Y).transpose()
plt.figure()
plt.scatter(tp[c1],tp[c2],color='black',marker='.',s=1)
plt.savefig(outfile)
