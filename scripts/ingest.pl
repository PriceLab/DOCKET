#!/bin/env perl
$|=1;
use strict;
use JSON;

my($infile, $file_format, $skipDuplicates) = @ARGV;
die unless $infile;

my $gzipped;
if ($infile =~ /\.gz$/) {
	$gzipped = 1;
	`cp $infile original_data.gz`;
} else {
	`gzip -c $infile > original_data.gz`;
}

my $info;
if ($file_format eq 'xml') {
	$info = read_xml($infile);
} elsif ($file_format eq 'table') {
	$info = read_tabular($infile, 1, 0, 0, 0); # 1 header line, default delimiter, id in column 0, skip 0 columns
} elsif ($file_format eq 'pandas') {
	$info = read_tabular($infile, 1, ',', 0, 0); # 1 header line, comma-delimited, id in column 0, skip 0 columns
} elsif ($file_format eq 'rtable') {
	$info = read_tabular($infile, 1, ' ', 0, 1); # 1 header line, space-delimited, id in column 0, skip 1 column
} elsif ($file_format eq 'lol') { #list of lists
	$info = read_lol($infile, 0, 0, 0, 2); # 0 header lines, default delimiter, id in column 0, skip 2 columns
} elsif ($file_format eq 'xyz') { #triples
	$info = read_xyz($infile, 1, ','); # 1 header line, comma-delimited
}

open ROWS, ">rows_data.json";
print ROWS to_json($info->{'rowwise'}, {pretty=>1});
close ROWS;

open COLS, ">cols_data.json";
print COLS to_json($info->{'colwise'}, {pretty=>1});
close COLS;

open CLEAN, ">cleaned_data.txt";
my @headers = @{$info->{'colnames'}};
print CLEAN join("\t", @headers), "\n";
foreach my $row (@{$info->{'rownames'}}) {
	my $ri = $info->{'rowwise'}{$row};
	print CLEAN join("\t", map {$ri->{$headers[$_]} // 'NA'} (0..$#headers)), "\n";
}
close CLEAN;

`gzip -f rows_data.json cols_data.json cleaned_data.txt`;

########
sub read_tabular {
	my($infile, $headerLines, $delimiter, $idcol, $skipcols) = @_;
	my(@headers, @colnames, @rownames, @colHist, $rows, %colwise, %rowwise, $id);
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
	
	$headers[0][0] ||= 'id'; ## to patch up pandas format with an empty field - but should pay attention to $idcol

	while (<INF>) {
		next if /^#/;
		chomp;
		s/\r//g;
		my(@v) = split $delimiter;

		unless (@colnames) {
			if (defined $headers[0]) {
				@colnames = @{$headers[0]};
				unshift @colnames, "id" if scalar @v == 1+scalar @colnames;
				### if scalar @v != scalar @colnames, there will be trouble
			} else {
				# make up names like col_0, col_1...
				@colnames = map {"col_$_"} (0..$#v);
			}
		}
		
		$id = $v[$idcol];
		next if $skipDuplicates && defined $rowwise{$id};
		push @rownames, $id;
		
		$colHist[scalar @v]++;
		$rows++;
		foreach my $col ($skipcols..$#colnames) {
			my $v = $v[$col];
			next unless $v || length($v);
			$colwise{$colnames[$col]}{$id} = $rowwise{$id}{$colnames[$col]} = $v;
		}
	}
	close INF;
	return {
		'headers'  => \@headers,
		'colnames' => \@colnames,
		'rownames' => \@rownames,
		'colhist'  => \@colHist,
		'rows'     => $rows,
		'colwise'  => \%colwise,
		'rowwise'  => \%rowwise
	};
}

sub read_lol { # list of lists
	my($infile, $headerLines, $delimiter, $idcol, $skipcols) = @_;
	my(@headers, @colnames, @rownames, @colHist, $rows, %colwise, %rowwise, $id);
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
		my(@v) = split $delimiter;
		push @headers, \@v;
	}

	while (<INF>) {
		next if /^#/;
		chomp;
		my(@v) = split $delimiter;
		$colHist[scalar @v]++;
		$rows++;
		$id = $v[$idcol];
		push @rownames, $id;
		foreach my $col ($skipcols..$#v) {
			my $v = $v[$col];
			$colwise{$v}{$id} = $rowwise{$id}{$v} = 1;
		}
	}
	close INF;
	my @colnames = sort keys %colwise;
	return {
		'headers'  => \@headers,
		'colnames' => \@colnames,
		'rownames' => \@rownames,
		'colhist'  => \@colHist,
		'rows'     => $rows,
		'colwise'  => \%colwise,
		'rowwise'  => \%rowwise
	};
}

sub read_xyz { # row-col-value triples
	my($infile, $headerLines, $delimiter) = @_;
	my(@headers, @colnames, @rownames, @colHist, $rows, %colwise, %rowwise, $id, $attr, $v);
	my(%seenid, %seenattr);
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
		my(@v) = split $delimiter;
		push @headers, \@v;
	}

	while (<INF>) {
		next if /^#/;
		chomp;
		my(@v) = split $delimiter;
		$colHist[scalar @v]++;
		$rows++;
		($id, $attr, $v) = @v;
		push @rownames, $id unless $seenid{$id};
		$seenid{$id}++;
		push @colnames, $attr unless $seenattr{$id};
		$seenattr{$attr}++;
		$colwise{$attr}{$id} = $rowwise{$id}{$attr} = $v;
	}
	close INF;
	return {
		'headers'  => \@headers,
		'colnames' => \@colnames,
		'rownames' => \@rownames,
		'colhist'  => \@colHist,
		'rows'     => $rows,
		'colwise'  => \%colwise,
		'rowwise'  => \%rowwise
	};
}

sub read_xml { ###unfinished
	my($infile, $idcol) = @_;
	my(@headers, @colHist, $rows, @votes, %colwise, %rowwise, $id);

	my $content = XMLin($infile, ForceArray => 0, KeyAttr => 1);
	$content = $content->{'GENESET'}; ### specific
	print join("\t", %{$content->{'GENESET'}[0]}), "\n";

	#####
	exit;
	####
	
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

