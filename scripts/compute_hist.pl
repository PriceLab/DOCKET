#!/bin/env perl
$|=1;
use strict;
use JSON;

my($storeddata, $hist_outfile, $types_outfile, $decimals) = @ARGV;
my $json;
open DATA, "gunzip -c $storeddata |";
while (<DATA>) {
	chomp;
	$json .= $_;
}
close DATA;
my $data = decode_json($json);
my($ch, $types) = compute_content_histogram($data);
foreach (keys %$ch) {
	$types->{$_}{'values'} = scalar keys %{$ch->{$_}};
}

open TYPES, ">$types_outfile";
print TYPES to_json($types, {pretty=>1});
close TYPES;

open HIST, ">$hist_outfile";
print HIST to_json($ch, {pretty=>1});
close HIST;


sub compute_content_histogram {
	my($what) = @_;
	my(%hist, %types);

	while (my($id, $ref) = each %$what) {
		$id = $1 if $id =~ /^\"(.+)\"$/;
		foreach my $value (values %$ref) {
			#next unless $value;
			if (ref $value eq 'ARRAY') {
				foreach my $v (@{$value}) {
					## modify to get rid of surrounding quotes, trimming numerical resolution, other cleanups
					$value = $1 if $value =~ /^\"(.+)\"$/;
					if (isnumeric($v)) {
						$types{$id}{'NUM'}++;
						if ($decimals && $v =~ /\./) {
							$value = sprintf("%.${decimals}f", $v);
						}
					} elsif ($v eq '') {
						$types{$id}{'NULL'}++;
					} else {
						$types{$id}{'STR'}++;
					}
					
					$hist{$id}{$v}++ if $v;
				}
			} else {
				## modify to get rid of surrounding quotes, trimming numerical resolution, other cleanups
				$value = $1 if $value =~ /^\"(.+)\"$/;
				if (isnumeric($value)) {
					$types{$id}{'NUM'}++;
					if ($decimals && $value =~ /\./) {
						$value = sprintf("%.${decimals}f", $value);
					}
				} elsif ($value eq '' || $value eq 'NA') {
					$types{$id}{'NULL'}++;
				} else {
					$types{$id}{'STR'}++;
				}
				
				$hist{$id}{$value}++;
			}
		}
	}
	return \%hist, \%types;
}

sub isnumeric ($) {
        no warnings;
        my $v = $_[0];
        $v =~ s/0+$// if $v =~ /\.\d*?0+/;
        $v =~ s/\.$//;
        if (substr($v,0,1) eq '.') {
                return "0$v" eq $v+0;
        } elsif ($v =~ /^([\-\+])\.(.+)/) {
                return "${1}0.$2" eq $v+0;
        } else {
                return $v eq $v+0;
        }
}
