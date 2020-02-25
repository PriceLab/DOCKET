#!/bin/env perl
$|=1;
use strict;

#This script is used in the DOCKET pipeline to filter out fingerprints that have too few triples, by setting $column to 1 and specifying the minimal number of triples to accept.
my($infile, $column, $minvalue) = @ARGV;

if ($infile =~ /\.gz$/) {
	open INF, "gunzip -c $infile |";
} else {
	open INF, $infile;
}

while (<INF>) {
	my(@v) = split /\t/, $_, $column+1;
	if ($v[$column] >= $minvalue) {
		print;
	}
}
close INF;
