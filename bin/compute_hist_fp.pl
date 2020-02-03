#!/local/bin/perl
$|=1;
use strict;
use JSON;
use lib "/users/gglusman/proj/LPH/data-fingerprints/bin";
use LIBLPH;
my $lphbin = "/users/gglusman/proj/LPH/data-fingerprints/bin";

my($storeddata, $direction, $L, $outdir) = @ARGV;
$L ||= 50;
my $decimals = 3;
my $normalize;

my $outfile = "$outdir/${direction}_hist_fp";
exit if -s "$outfile.raw.gz";

my $json;
open DATA, "gunzip -c $storeddata.gz |";
while (<DATA>) {
	chomp;
	$json .= $_;
}
close DATA;
my $data = decode_json($json);

my $CHF = new LIBLPH;
$CHF->{'L'} = $L;

open OF, ">$outfile.raw";
foreach my $id (sort {$a<=>$b || $a cmp $b} keys %$data) {
	$CHF->resetFingerprint();
	$CHF->recurseStructure($data->{$id});
	next unless $CHF->{'statements'};
	my $fp;
	if ($normalize) {
		$fp = $CHF->normalize();
	} else {
		$fp = $CHF->{'fp'};
	}
	my @v;                                               
	push @v, @{$fp->{$_}} foreach sort {$a<=>$b} keys %$fp;
	$id =~ s/[^A-Z0-9_\.\-\=,\+\*:;\@\^\`\|\~]+//gi;
	print OF join("\t", $id, $CHF->{'statements'}, map {sprintf("%.${decimals}f", $_)} @v), "\n";
}
close OF;

`$lphbin/serializeLPH.pl $outfile $L 1 1 $outfile.raw`;
`gzip -f $outfile.raw`;
