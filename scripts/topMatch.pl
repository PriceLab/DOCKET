#!/bin/env perl
$|=1;
use strict;

my(%qseen, %tseen);
while (<>) {
	chomp;
	my($q, $t, $c) = split /\t/;
	next if $qseen{$q};
	next if $tseen{$t};
	print "$_\n";
	$qseen{$q}++;
	$tseen{$t}++;
}
