#!/local/bin/perl
$|=1;
use strict;
use JSON;

my($storeddata, $outfile) = @ARGV;
exit if -s $outfile;

my $json;
open DATA, "gunzip -c $storeddata.gz |";
while (<DATA>) {
	chomp;
	$json .= $_;
}
close DATA;
my $data = decode_json($json);
my $ch = compute_content_histogram($data);
print to_json($ch);


sub compute_content_histogram {
	my($what) = @_;
	my %hist;
	
	while (my($id, $ref) = each %$what) {
		$hist{$id}{$_}++ foreach values %$ref; ## modify to get rid of surrounding quotes, trimming numerical resolution, other cleanups
	}
	return \%hist;
}
