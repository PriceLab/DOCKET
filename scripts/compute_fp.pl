#!/bin/env perl
$|=1;
use strict;
use JSON;
use LIBLPH;

my($storeddata, $L) = @ARGV;
$L ||= 100;
my $decimals = 3;
my $normalize;


my $json;
if ($storeddata =~ /\.gz$/) {
	open DATA, "gunzip -c $storeddata |";
} elsif (-e "$storeddata.gz") {
	open DATA, "gunzip -c $storeddata.gz |";
} else {
	open DATA, $storeddata;
}
while (<DATA>) {
	chomp;
	$json .= $_;
}
close DATA;
my $data = decode_json($json);

my $FP = new LIBLPH;
$FP->{'L'} = $L;

foreach my $id (sort {$a<=>$b || $a cmp $b} keys %$data) {
	$FP->resetFingerprint();
	$FP->recurseStructure($data->{$id});
	next unless $FP->{'statements'};
	my $fp;
	if ($normalize) {
		$fp = $FP->normalize();
	} else {
		$fp = $FP->{'fp'};
	}
	my @v;
	push @v, @{$fp->{$_}} foreach sort {$a<=>$b} keys %$fp;
	$id =~ s/[^A-Z0-9_\.\-\=,\+\*:;\@\^\`\|\~]+//gi;
	print join("\t", $id, $FP->{'statements'}, map {sprintf("%.${decimals}f", $_)} @v), "\n";
}
