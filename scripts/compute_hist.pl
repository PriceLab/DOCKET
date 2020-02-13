#!/bin/env perl
$|=1;
use strict;
use JSON;

my($storeddata) = @ARGV;

my $json;
open DATA, "gunzip -c $storeddata |";
while (<DATA>) {
	chomp;
	$json .= $_;
}
close DATA;
my $data = decode_json($json);
my $ch = compute_content_histogram($data);
print to_json($ch, {pretty=>1});


sub compute_content_histogram {
	my($what) = @_;
	my %hist;

	while (my($id, $ref) = each %$what) {
		foreach my $value (values %$ref) {
			next unless $value;
			if (ref $value eq 'ARRAY') {
				foreach (@{$value}) {
					## modify to get rid of surrounding quotes, trimming numerical resolution, other cleanups
					$hist{$id}{$_}++ if $_;
				}
			} else {
				## modify to get rid of surrounding quotes, trimming numerical resolution, other cleanups
				$hist{$id}{$value}++;
			}
		}
	}
	return \%hist;
}
