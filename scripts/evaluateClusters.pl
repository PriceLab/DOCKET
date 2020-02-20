#!/usr/bin/env perl
$|=1;
use strict;

my($clusters, $aaa) = @ARGV;

open CL, "gunzip -c $clusters |";
$_ = <CL>;
chomp;
my(undef, @ids) = split /\t/;
my %cluster;
while (<CL>) {
	chomp;
	next unless $_;
	my($clusters, %c);
	my($cutoff, @cl) = split /\t/;
	foreach my $i (0..$#ids) {
		$c{$ids[$i]} = $cl[$i];
		$clusters = $cl[$i] if $cl[$i]>$clusters;
		#print join("\t", $i, $ids[$i], $cl[$i]), "\n";
	}
	$cluster{$clusters} = \%c;
	last if $clusters>500;
}
close CL;

my(%count, %sum);
open AAA, "gunzip -c $aaa |";
while (<AAA>) {
	chomp;
	my($q, $t, $c) = split /\t/;
	foreach my $n (keys %cluster) {
		my $clq = $cluster{$n}{$q};
		my $clt = $cluster{$n}{$t};
		
		### hack since the code computing hierarchical clusters mangles some identifiers:
		unless ($clq) {
			$q =~ s/^0+//;
			$clq = $cluster{$n}{$q};
		}
		unless ($clt) {
			$t =~ s/^0+//;
			$clt = $cluster{$n}{$t};
		}
		
		$count{$n}[$clq eq $clt]++;
		$sum{$n}[$clq eq $clt]+=(1-$c);
		#print join("\t", $q, $t, $n, $clq, $clt), "\n";
	}
}
close AAA;

foreach my $n (sort {$a<=>$b} keys %count) {
	next unless $count{$n}[0] && $count{$n}[1];
	print join("\t", $n, $sum{$n}[0]/$count{$n}[0], $sum{$n}[1]/$count{$n}[1]), "\n";
}
