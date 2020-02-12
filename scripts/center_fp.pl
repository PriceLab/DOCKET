#!/bin/env perl
$|=1;
use strict;

my(@data, @ids, @statements, $L);

while (<>) {
	chomp;
	my($id, $statements, @v) = split /\t/;
	$L ||= scalar @v;
	push @ids, $id;
	push @statements, $statements;
	#normalize each fingerprint:
	my($avg, $std) = avgstd(\@v);
	@v = map {($v[$_]-$avg)/$std} (0..$#v);
	push @data, \@v;
}

#center and scale each column:
foreach my $i (0..$#{$data[0]}) {
	my @v = map {$data[$_][$i]} (0..$#data);
	my($avg, $std) = avgstd(\@v);
	$data[$_][$i] = ($data[$_][$i]-$avg)/$std foreach (0..$#data);
}

foreach my $i (0..$#data) {
	print join("\t", $ids[$i], $statements[$i], map {sprintf("%.3f", $data[$i][$_])} (0..$L-1)), "\n";
}



sub avgstd {
	my($values) = @_;
	my($sum, $devsqsum);

	my $n = scalar @$values;
	return unless $n>1;
	foreach (@$values) { $sum += $_ }
	my $avg = $sum / $n;
	foreach (@$values) { $devsqsum += ($_-$avg)**2 }
	my $std = sqrt($devsqsum/($n-1));
	return $avg, $std;
}