#!/local/bin/perl
$|=1;
use strict;
use GD;
use JSON;
use Scalar::Util qw(looks_like_number);

my($docket, $sortCols, $sortRows) = @ARGV;
my $ch = readJson("$docket/data/cols_hist.json.gz");
my $rt = readJson("$docket/data/rows_types.json.gz");
my(@data, @type, @col_nulls, @row_nulls);

open DATA, "gunzip -c $docket/data/original_data.gz |";
while (<DATA>) {
	next if /^#/;
	last;
}
chomp;
my @headers = split /\t/;
foreach my $i (0..$#headers) {
	$headers[$i] = $1 if $headers[$i] =~ /^\"(.+)\"$/;
}
my $j;
while (<DATA>) {
	next if /^#/;
	chomp;
	next unless $_;
	my @v = split /\t/;
	push @data, \@v;
	foreach my $i (0..$#headers) {
		my $v = $v[$i];
		my $t;
		$v = $1 if $v =~ /^\"(.+)\"$/;
		if (length($v)==0 || $v =~ /^(NA|NULL)$/i) {
			$t = 'null';
			$col_nulls[$i]++;
			$row_nulls[$j]++;
		} else {
			$t = looks_like_number($v) ? 'num' : 'str';
		}
		$type[$j][$i] = $t;
	}
	$j++;
}
close DATA;
my $rows = scalar @data;

#my @types = map {datatype($ch->{$headers[$_]})} (0..$#headers);

my(%imColour, $background, $useBlackBackground, @idColor, $xmargin, $ymargin);
$xmargin = $ymargin = 10;
my $xscale = 1;
my $yscale = 1;
my $width = scalar @headers;
my $height = $rows;
my %typeColor = qw/num blue str red mixed grey/;

my $im = new GD::Image($width+2*$xmargin,$height+2*$ymargin);
$im->interlaced('true');
DefineColours($im, 1);

#foreach my $i (0..$#headers) {
#	frect($im, $i,0,$i,$height, $typeColor{$types[$i]});
#}

my(@sortedRows, @sortedCols);
if ($sortCols eq 'nulls') {
 	@sortedCols = sort {$col_nulls[$a]<=>$col_nulls[$b]} (0..$#headers);
} else {
	@sortedCols = (0..$#headers);
}
if ($sortRows eq 'nulls') {
	@sortedRows = sort {$row_nulls[$a]<=>$row_nulls[$b]} (0..$rows-1);
} else {
	@sortedRows = (0..$#data);
}

foreach my $j (0..$#sortedRows) {
	my $row = $sortedRows[$j];
	#my $rowdata = $data[$row];
	foreach my $i (0..$#sortedCols) {
		my $col = $sortedCols[$i];
		my $t = $type[$row][$col];
		if ($t eq 'null') {
			frect($im, $i, $j, $i, $j, 'white');
		} else {
			frect($im, $i, $j, $i, $j, $typeColor{$t});
		}
	}
}

open (PNG,">$docket/visualizations/data_overview.png") || warn "Couldn't write png file: $!\n";
print PNG $im->png;
close PNG;


########
sub datatype {
	my($what) = @_;
	my($num, $str);
	while (my($key) = each %$what) {
		next unless $key;
		next if $key eq 'NA';
		if (looks_like_number($key)) {
			$num++;
		} else {
			$str++;
		}
	}
	return 'num' unless $str;
	return 'str' unless $num;
	return 'mixed';
}

sub readJson {
	my($file) = @_;

	my $json;
	if ($file =~ /\.gz$/) {
		open CT, "gunzip -c $file |";
	} else {
		open CT, $file;
	}
	while (<CT>) {
		chomp;
		$json .= $_;
	}
	close CT;
	return decode_json($json);
}

sub DefineColours {
	my($im, $strong)=@_;
	my(%cd, $col, @values, $i, $id, $intn);
	
	%cd = (
	'blue' => [0,0,255],
	'red' => [255,0,0],
	'green' => [0,255,0],
	'yellow' => [255,255,0],
	'magenta' => [255,0,255],
	'cyan' => [0,255,255],
	'brown' => [166,126,62],
	'orange' => [255,140,0],
	'salmon' => [250,128,114],
	'pink' => [255,105,180],
	'grey' => [150,150,150],
	);
	
	if ($useBlackBackground) {
		$imColour{'black'} = $im->colorAllocate(0,0,0);       
		$imColour{'white'} = $im->colorAllocate(255,255,255);
		$background = 'black';
	} else {
		$imColour{'white'} = $im->colorAllocate(255,255,255);
		$imColour{'black'} = $im->colorAllocate(0,0,0);       
		$background = 'white';
	}
	
	
	foreach $col (keys %cd) {
		@values = @{$cd{$col}};
		$imColour{$col} = $im->colorAllocate(@values);
		next if $col eq 'brown';
		foreach $i (0..2) {
			$values[$i] ||= 180;
		}
		$imColour{"light$col"} = $im->colorAllocate(@values);
	}
	$imColour{'lightred'} = $im->colorAllocate(240,128,128);
	$imColour{'lightpink'} = $im->colorAllocate(255,192,203);
	$imColour{'lightbrown'} = $im->colorAllocate(220,200,120);
	$imColour{'lightorange'} = $im->colorAllocate(255,220,160);
	
	#for ($id=100;$id>0;$id-=5) {
		#	$intn = (100-$id)/100*150;
		#	$idColor[$id] = $im->colorAllocate($intn, $intn, $intn);
	#}
	
	foreach $id (reverse(0..100)) {
		$intn = (100-$id)/100*255;
		$idColor[$id] = $im->colorAllocate($intn, $intn, 255);
	}
}

sub frect { #filled rectangles
	my ($im, $x1, $y1, $x2, $y2, $colour) = @_;
	
	($x1, $x2) = ($x2, $x1) if $x2<$x1;
	($y1, $y2) = ($y2, $y1) if $y2<$y1;
	my @ends = (int($x1+$xmargin), int($y1+$ymargin), int($x2+$xmargin), int($y2+$ymargin));
	$im->filledRectangle(@ends, $imColour{$colour});
	return @ends;
}
