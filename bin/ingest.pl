#!/local/bin/perl
$|=1;
use strict;
use JSON;

my($infile, $file_format, $outdir) = @ARGV;
die unless $infile && $outdir;
mkdir $outdir, 0755;

exit if -s "$outdir/rows_data.json.gz" && -s "$outdir/cols_data.json.gz";

$file_format ||= determine_format($infile);
my $info;
if ($file_format eq 'xml') {
	$info = read_xml($infile);
} elsif ($file_format eq 'table') {
	$info = read_tabular($infile, 1, 0, 0, 1); # 1 header line, default delimiter, id in column 0, skip 1 column
} elsif ($file_format eq 'rtable') {
	$info = read_tabular($infile, 1, ' ', 0, 1); # 1 header line, space-delimited, id in column 0, skip 1 column
} elsif ($file_format eq 'lol') {
	$info = read_lol($infile, 0, 0, 0, 2); # 0 header lines, default delimiter, id in column 0, skip 2 columns
} elsif ($file_format eq 'xyz') {
	$info = read_xyz($infile, 1, ','); # 1 header line, comma-delimited
}

open ROWS, ">$outdir/rows_data.json";
print ROWS to_json($info->{'rowwise'});
close ROWS;

open COLS, ">$outdir/cols_data.json";
print COLS to_json($info->{'colwise'});
close COLS;

`gzip -f $outdir/rows_data.json $outdir/cols_data.json`;

########
sub determine_format { ###unfinished
	my($file) = @_;
	
	my $test = `file $file`;
	return 'xml' if $test =~ /: XML/;
	
	return '?';
}


sub read_tabular {
	my($infile, $headerLines, $delimiter, $idcol, $skipcols) = @_;
	my(@headers, @names, @colHist, $rows, %colwise, %rowwise, $id);
	$delimiter ||= "\t";
	
	if ($infile =~ /\.gz$/) {
		open INF, "gunzip -c $infile |";
	} else {
		open INF, $infile;
	}
	
	foreach my $i (1..$headerLines) {
		while (<INF>) {
			next if /^#/;
			last;
		}
		chomp;
		s/\r//g;
		my(@v) = split $delimiter;
		push @headers, \@v;
	}
	
	while (<INF>) {
		chomp;
		s/\r//g;
		my(@v) = split $delimiter;
		
		unless (@names) {
			if (defined $headers[0]) {
				@names = @{$headers[0]};
				unshift @names, "id" if scalar @v == 1+scalar @names;
				### if scalar @v != scalar @names, there will be trouble
			} else {
				# make up names like col_0, col_1...
				@names = map {"col_$_"} (0..$#v);
			}
		}
		
		$colHist[scalar @v]++;
		$rows++;
		$id = $v[$idcol];
		foreach my $col ($skipcols..$#v) {
			my $v = $v[$col];
			$colwise{$names[$col]}{$id} = $rowwise{$id}{$names[$col]} = $v;
		}
	}
	close INF;
	return {
		'headers' => \@headers,
		'colhist' => \@colHist,
		'rows'    => $rows,
		'colwise' => \%colwise,
		'rowwise' => \%rowwise
	};
}

sub read_lol { # list of lists
	my($infile, $headerLines, $delimiter, $idcol, $skipcols) = @_;
	my(@headers, @colHist, $rows, %colwise, %rowwise, $id);
	$delimiter ||= "\t";
	
	if ($infile =~ /\.gz$/) {
		open INF, "gunzip -c $infile |";
	} else {
		open INF, $infile;
	}
	
	foreach my $i (1..$headerLines) {
		$_ = <INF>;
		chomp;
		my(@v) = split $delimiter;
		push @headers, \@v;
	}
	
	while (<INF>) {
		chomp;
		my(@v) = split $delimiter;
		$colHist[scalar @v]++;
		$rows++;
		$id = $v[$idcol];
		foreach my $col ($skipcols..$#v) {
			my $v = $v[$col];
			$colwise{$v}{$id} = $rowwise{$id}{$v} = 1;
		}
	}
	close INF;
	return {
		'headers' => \@headers,
		'colhist' => \@colHist,
		'rows'    => $rows,
		'colwise' => \%colwise,
		'rowwise' => \%rowwise
	};
}

sub read_xyz { # row-col-value triples
	my($infile, $headerLines, $delimiter) = @_;
	my(@headers, @colHist, $rows, %colwise, %rowwise, $id, $attr, $v);
	$delimiter ||= "\t";
	
	if ($infile =~ /\.gz$/) {
		open INF, "gunzip -c $infile |";
	} else {
		open INF, $infile;
	}
	
	foreach my $i (1..$headerLines) {
		$_ = <INF>;
		chomp;
		my(@v) = split $delimiter;
		push @headers, \@v;
	}
	
	while (<INF>) {
		chomp;
		my(@v) = split $delimiter;
		$colHist[scalar @v]++;
		$rows++;
		($id, $attr, $v) = @v;
		$colwise{$attr}{$id} = $rowwise{$id}{$attr} = $v;
	}
	close INF;
	return {
		'headers' => \@headers,
		'colhist' => \@colHist,
		'rows'    => $rows,
		'colwise' => \%colwise,
		'rowwise' => \%rowwise
	};
}

sub read_xml { ###unfinished
	my($infile, $idcol) = @_;
	my(@headers, @colHist, $rows, @votes, %colwise, %rowwise, $id);
	
	my $content = XMLin($infile, ForceArray => 0, KeyAttr => 1);
	$content = $content->{'GENESET'}; ### specific
	print join("\t", %{$content->{'GENESET'}[0]}), "\n";
	
	exit;
	while (<INF>) {
		chomp;
		my(@v) = split;
		$colHist[scalar @v]++;
		$rows++;
		$id = $v[$idcol];
		foreach my $col (0..$#v) {
			my $v = $v[$col];
			$colwise{$headers[0][$col]}{$id} = $rowwise{$id}{$headers[0][$col]} = $v;
		}
	}
	
	close INF;
	return {
		'headers' => \@headers,
		'colhist' => \@colHist,
		'rows'    => $rows,
		'colwise' => \%colwise,
		'rowwise' => \%rowwise
	};
}

