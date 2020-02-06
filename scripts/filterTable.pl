#!/bin/env perl
$|=1;
use strict;

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
