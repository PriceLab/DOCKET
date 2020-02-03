#!/local/bin/perl
$|=1;
use strict;
use JSON;

my($storeddata, $direction, $outdir) = @ARGV;

my $outfile = "$outdir/${direction}_hist.json";
exit if -s "$outfile.gz";

my $json;
open DATA, "gunzip -c $storeddata.gz |";
while (<DATA>) {
	chomp;
	$json .= $_;
}
close DATA;
my $data = decode_json($json);
my $ch = compute_content_histogram($data);

open HIST, ">$outfile";
print HIST to_json($ch);
close HIST;
`gzip -f $outfile`;


sub compute_content_histogram {
	my($what) = @_;
	my %hist;
	
	while (my($id, $ref) = each %$what) {
		$hist{$id}{$_}++ foreach values %$ref; ## modify to get rid of surrounding quotes, trimming numerical resolution, other cleanups
	}
	return \%hist;
}
