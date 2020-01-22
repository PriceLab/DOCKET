#!/bin/env perl
$|=1;
use strict;
my $lphbin = "/users/gglusman/proj/LPH/data-fingerprints/bin";
use lib "/users/gglusman/proj/LPH/data-fingerprints/bin";
use LIBLPH;
use XML::Simple qw(:strict);
use FindBin qw($Bin);
use lib $Bin;


my $LPH = new LIBLPH;
my $normalize = 1;
my $L = 2000;
$LPH->{'L'} = $L;
my $decimals = 3;

my($infile, $file_format, $outdir) = @ARGV;
## sanity checks on infile and outdir
die unless $infile && $outdir;
mkdir $outdir, 0755;

## determine format
$file_format ||= determine_format($infile);

## reformat if needed

my $info;
if ($file_format eq 'xml') {
	$info = read_xml($infile);
} elsif ($file_format eq 'table') {
	$info = read_tabular($infile, 1, 0, 0, 1, 1, 1); # 1 header line, default delimiter, id in column 0, skip 1 column
} elsif ($file_format eq 'rtable') {
	$info = read_tabular($infile, 1, ' ', 0, 1, 1, 1); # 1 header line, space-delimited, id in column 0, skip 1 column
} elsif ($file_format eq 'lol') {
	$info = read_lol($infile, 0, 0, 0, 2, 1, 1); # 0 header lines, default delimiter, id in column 0, skip 2 columns
} elsif ($file_format eq 'xyz') {
	$info = read_xyz($infile, 1, ',', 1, 1); # 1 header line, comma-delimited
}

my @rowids = sort {$a<=>$b || $a cmp $b} keys %{$info->{'rowwise'}};
my @colids = sort {$a<=>$b || $a cmp $b} keys %{$info->{'colwise'}};

#print "colwise\t";
#evaluate_types($info->{'colwise'});
#print "rowwise\t";
#evaluate_types($info->{'rowwise'});

#print join("\t", "Headers", scalar @{$info->{'headers'}[0]}), "\n";
print join("\t", "Rows", $info->{'rows'}, scalar keys %{$info->{'rowwise'}}), "\n"; # if the two numbers differ, there are duplicate ids, or rows don't correspond to rows one-to-one
print join("\t", "Cols", scalar keys %{$info->{'colwise'}}), "\n";

if (0) { # show distribution of columns observed per line
	print "Column distribution:\n";
	my $colHist = $info->{'colhist'};
	foreach my $i (0..$#$colHist) {
		print join("\t", $i, $colHist->[$i]), "\n" if defined $colHist->[$i];
	}
}
if (0) { # show type votes from BDQC_lite
	my $votes = $info->{'votes'};
	foreach my $col (0..$#$votes) {
		print join("\t", $col, $info->{'headers'}[0][$col], %{$votes->[$col]}), "\n";
	}
}

# rowwise fingerprints
my $row_fp_file = "$outdir/row_fp.raw";
unless (-e $row_fp_file) {
	print "computing row fingerprints\n";
	compute_fp($info->{'rowwise'}, $row_fp_file);
}
unless (-e "$outdir/row_fp.id") {
	print "serializing row fingerprints\n";
	`$lphbin/serializeLPH.pl $outdir/row_fp $L 1 1 $row_fp_file`;
}
unless (-e "$outdir/row_fp.aaa.gz") {
	print "comparing row fingerprints\n";
	`$lphbin/searchLPHs.pl $outdir/row_fp 0 1000000 $outdir/row_fp.aaa.hist | gzip -c > $outdir/row_fp.aaa.gz`;
}
unless (-e "$outdir/row_fp.pca.gz") {
	print "PCA on row fingerprints\n";
	`python3 $Bin/pca.py $outdir/row_fp.raw --L $L | gzip -c > $outdir/row_fp.pca.gz`;
}
unless (-e "$outdir/row_fp.pc1_pc2.png") {
	print "Plotting PCA on row fingerprints\n";
	`python3 $Bin/plotpca.py $outdir/row_fp.pca.gz  $outdir/row_fp.pc1_pc2.png`;
}


if (0) { ### THIS COULD BE VERY SLOW
unless (-e "$outdir/col_sp.aaa.gz") {
	print "comparing columns by Spearman correlation\n";
	#`$lphbin/searchLPHs.pl $outdir/col_fp 0 1000000 $outdir/col_fp.aaa.hist | gzip -c > $outdir/col_fp.aaa.gz`;
	correlate_all_spearman($info->{'colwise'}, "$outdir/col_sp.aaa", \@colids, \@rowids);
	`sort -k3rn $outdir/col_sp.aaa | gzip -c > $outdir/col_sp.aaa.gz`;
	#`unlink $outdir/col_sp.aaa`;
}
}

# colwise fingerprints
my $col_fp_file = "$outdir/col_fp.raw";
unless (-e $col_fp_file) {
	print "computing col fingerprints\n";
	compute_fp($info->{'colwise'}, $col_fp_file);
}
unless (-e "$outdir/col_fp.id") {
	print "serializing col fingerprints\n";
	`$lphbin/serializeLPH.pl $outdir/col_fp $L 1 1 $col_fp_file`;
}
unless (-e "$outdir/col_fp.aaa.gz") {
	print "comparing col fingerprints\n";
	`$lphbin/searchLPHs.pl $outdir/col_fp 0 1000000 $outdir/col_fp.aaa.hist | gzip -c > $outdir/col_fp.aaa.gz`;
}
unless (-e "$outdir/col_fp.pca.gz") {
	print "PCA on col fingerprints\n";
	`python3 $Bin/pca.py $outdir/col_fp.raw --L $L | gzip -c > $outdir/col_fp.pca.gz`;
}
unless (-e "$outdir/col_fp.pc1_pc2.png") {
	print "Plotting PCA on col fingerprints\n";
	`python3 $Bin/plotpca.py $outdir/col_fp.pca.gz  $outdir/col_fp.pc1_pc2.png`;
}

# column-wise content histogram fingerprints
my $col_chf_file = "$outdir/col_chf.norm";
unless (-e $col_chf_file) {
	print "computing col content histogram fingerprints\n";
	compute_chf($info->{'colwise'}, $col_chf_file);
}
unless (-e "$outdir/col_chf.id") {
	print "serializing col content histogram fingerprints\n";
	`$lphbin/serializeLPH.pl $outdir/col_chf $L 1 0 $col_chf_file`;
}
unless (-e "$outdir/col_chf.aaa.gz") {
	print "comparing col content histogram fingerprints\n";
	`$lphbin/searchLPHs.pl $outdir/col_chf 0 1000000 $outdir/col_chf.aaa.hist | gzip -c > $outdir/col_chf.aaa.gz`;
}







########
sub determine_format {
	my($file) = @_;
	
	my $test = `file $file`;
	return 'xml' if $test =~ /: XML/;
	
	return '?';
}

sub evaluate_types {
	my($what) = @_;
	
	my(%allNil, %type, %mixed);
	while (my($id1, $cargo) = each %$what) {
		my(%votes, $n);
		while (my($id2, $v) = each %$cargo) {
			my $type = test_type($v);
			#print join("\t", $id2, $type, $v), "\n" if $id1 eq 'population.height';
			$votes{$type}++;
			$n++;
		}
		if ($votes{'nil'} == $n) {
			$allNil{$id1}++;
			next;
		}
		delete $votes{'nil'};
		
		my @sorted = sort {$votes{$b}<=>$votes{$a}} keys %votes;
		if (scalar keys %votes == 1) {
			$type{$id1} = $sorted[0];
			if ($sorted[0] eq 'num') {
				#my @values = values %$cargo;
				#my($avg, $std) = avgstd(\@values);
				#print join("\t", $id1, $avg, $std), "\n";
			}
			
		} else {
			$mixed{$id1} = \@sorted;
			#print join("\t", $id1, $n, $votes{$sorted[0]}, %votes), "\n";
		}
	}
	#return \%type, \%mixed, \%allNil;
	print join("\t", scalar keys %type, scalar keys %mixed, scalar keys %allNil), "\n";
}


sub compute_fp {
	my($what, $where) = @_;
	
	open OF, ">$where";
	foreach my $id (sort {$a<=>$b || $a cmp $b} keys %$what) {
		$LPH->resetFingerprint();
		$LPH->recurseStructure($what->{$id});
		next unless $LPH->{'statements'};
		my $fp;
		if ($normalize) {
			$fp = $LPH->normalize();
		} else {
			$fp = $LPH->{'fp'};
		}
		my @v;                                               
		push @v, @{$fp->{$_}} foreach sort {$a<=>$b} keys %$fp;
		$id =~ s/[^A-Z0-9_\.\-\=,\+\*:;\@\^\`\|\~]+//gi;
		print OF join("\t", $id, $LPH->{'statements'}, map {sprintf("%.${decimals}f", $_)} @v), "\n";
	}
	close OF;
}

sub compute_chf {
	my($what, $where) = @_;
	
	my $CHF = new LIBLPH;
	my $normalize = 1;
	my $L = 50;
	$CHF->{'L'} = $L;
	
	open OF, ">$where";
	foreach my $id (sort {$a<=>$b || $a cmp $b} keys %$what) {
		my %hist;
		$hist{$_}++ foreach values %{$what->{$id}};
		
		$CHF->resetFingerprint();
		$CHF->recurseStructure(\%hist);
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
}

sub correlate_all_pearson {
	my($what, $where, $ids, $oids) = @_;
	
	open OF, ">$where";
	my(%avg, %std, %v);
	foreach my $id (@$ids) {
		my @v = map {$what->{$id}{$_}} @$oids;
		$v{$id} = \@v;
		my($avg, $std) = avgstd(\@v);
		$avg{$id} = $avg;
		$std{$id} = $std;
	}
	
	foreach my $i (0..$#$ids-1) {
		my $id1 = $ids->[$i];
		#$id1 =~ s/[^A-Z0-9_\.\-\=,\+\*:;\@\^\`\|\~]+//gi;
		foreach my $j ($i+1..$#$ids) {
			my $id2 = $ids->[$j];
			my $c = correlation($v{$id1}, $v{$id2}, $avg{$id1}, $std{$id1}, $avg{$id2}, $std{$id2});
			print OF join("\t", $id1, $id2, sprintf("%.6f", $c),
				#correlation(ranks($what->{$id1}), ranks($what->{$id2}))
				), "\n";
		}
	}
	close OF;
}

sub correlate_all_spearman {
	my($what, $where, $ids, $oids) = @_;
	
	open OF, ">$where";
	my(%avg, %std, %v);
	foreach my $id (@$ids) {
		my @v = map {$what->{$id}{$_}} @$oids;
		$v{$id} = ranks(\@v);
		my($avg, $std) = avgstd($v{$id});
		$avg{$id} = $avg;
		$std{$id} = $std;
	}
	
	foreach my $i (0..$#$ids-1) {
		my $id1 = $ids->[$i];
		#$id1 =~ s/[^A-Z0-9_\.\-\=,\+\*:;\@\^\`\|\~]+//gi;
		foreach my $j ($i+1..$#$ids) {
			my $id2 = $ids->[$j];
			my $c = correlation($v{$id1}, $v{$id2}, $avg{$id1}, $std{$id1}, $avg{$id2}, $std{$id2});
			print OF join("\t", $id1, $id2, sprintf("%.6f", $c),
				#correlation(ranks($what->{$id1}), ranks($what->{$id2}))
				), "\n";
		}
	}
	close OF;
}

sub read_tabular {
	my($infile, $headerLines, $delimiter, $idcol, $skipcols, $storeColwise, $storeRowwise) = @_;
	my(@headers, @names, @colHist, $rows, %colwise, %rowwise, $id);
	$delimiter ||= "\t";
	
	if ($infile =~ /\.gz$/) {
		open INF, "gunzip -c $infile |";
	} else {
		open INF, $infile;
	}
	
	foreach my $i (1..$headerLines) {
		$_ = <INF>;
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
			$colwise{$names[$col]}{$id} = $v if $storeColwise;
			$rowwise{$id}{$names[$col]} = $v if $storeRowwise;
		}
	}
	close INF;
	my %ret = ('headers', \@headers, 'colhist', \@colHist, 'rows', $rows);
	$ret{'colwise'} = \%colwise if $storeColwise;
	$ret{'rowwise'} = \%rowwise if $storeRowwise;
	return \%ret;
}

sub read_lol { # list of lists
	my($infile, $headerLines, $delimiter, $idcol, $skipcols, $storeColwise, $storeRowwise) = @_;
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
			$colwise{$v}{$id} = 1 if $storeColwise;
			$rowwise{$id}{$v} = 1 if $storeRowwise;
		}
	}
	close INF;
	my %ret = ('headers', \@headers, 'colhist', \@colHist, 'rows', $rows);
	$ret{'colwise'} = \%colwise if $storeColwise;
	$ret{'rowwise'} = \%rowwise if $storeRowwise;
	return \%ret;
}

sub read_xyz { # row-col-value triples
	my($infile, $headerLines, $delimiter, $storeColwise, $storeRowwise) = @_;
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
		$colwise{$attr}{$id} = $v if $storeColwise;
		$rowwise{$id}{$attr} = $v if $storeRowwise;
	}
	close INF;
	my %ret = ('headers', \@headers, 'colhist', \@colHist, 'rows', $rows);
	$ret{'colwise'} = \%colwise if $storeColwise;
	$ret{'rowwise'} = \%rowwise if $storeRowwise;
	return \%ret;
}

sub read_xml {
	my($infile, $idcol, $storeColwise, $storeRowwise) = @_;
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
			$colwise{$headers[0][$col]}{$id} = $v if $storeColwise;
			$rowwise{$id}{$headers[0][$col]} = $v if $storeRowwise;
		}
	}
	
	close INF;
	my %ret = ('headers', \@headers, 'colhist', \@colHist, 'rows', $rows);
	$ret{'colwise'} = \%colwise if $storeColwise;
	$ret{'rowwise'} = \%rowwise if $storeRowwise;
	return \%ret;
}

sub test_type {
	my($v) = @_;
	
	my $type = 'str';
	if (!$v) {
		$type = 'nil';
	} elsif (isnumeric($v)) {
		$type = 'num';
	} elsif ($v =~ /^(TRUE|FALSE)$/i) {
		$type = 'bool';
	}
	return $type;
}

sub correlation {
	my($set1ref, $set2ref, $avg1, $std1, $avg2, $std2) = @_;
	my($n, $i, $corr);

	$n = scalar @{$set1ref};
	return unless $n && ($n == scalar @{$set2ref});
	($avg1, $std1) = avgstd($set1ref) unless $std1;
	($avg2, $std2) = avgstd($set2ref) unless $std2;
	return -2 unless $std1 && $std2;
	foreach $i (0..$n-1) {
		$corr += ($$set1ref[$i]-$avg1)*($$set2ref[$i]-$avg2);
	}
	return $corr/($n-1)/$std1/$std2;
}

sub ranks {
	my($v) = @_;

	my @ranks;
	my $i;
	foreach (sort {$v->[$a] <=> $v->[$b] || (int(rand(2))*2-1)} (0..$#$v)) { $ranks[$_] = $i++ }
	return \@ranks;
}

sub avgstd {
	my($values) = @_;
	my($sum, $devsqsum);

	my $n = scalar @$values;
	return unless $n>1;
	foreach (@$values) { $sum += $_ }
	my $avg = $sum / $n;
	foreach (@$values) { $devsqsum += ($_-$avg)**2 }
	my $std = sqrt($devsqsum/($n-1));
	return $avg, $std;
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
	
	# simplistic version, which fails for representations like .2, -.5:
	#return $_[1] eq ($_[1]+0);
}