#!/bin/env perl
$|=1;
use strict;
use JSON;

my($infile, $outfile, $docket_title) = @ARGV;
unless ($infile) {
	print "Usage: build_compare_table <path to infile>\n";
	exit;
}


# get info on correlations
my($headers, $data) = read_table($infile);

# output
open OUTF, ">$outfile";
print_header("DOCKET compare");
print_section("DOCKET Compare for $docket_title");

print OUTF "<hr>\n";
print_table($data, 'table', 'numcorr', "Associations", $headers, {});


print OUTF qq(
<script src="https://code.jquery.com/jquery-3.4.1.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" crossorigin="anonymous"></script>
<script type="text/javascript" src="https://cdn.datatables.net/v/dt/dt-1.10.20/r-2.2.3/datatables.min.js"></script>
  <script>
    const config_num = {
     "language": {
        "search": "&#128269;",
        "searchPlaceholder": "search data"
      },
      "autoWidth": true,
      "order": [
        [3, "desc"]
      ]
    }
    
    \$(document).ready(function () {
      \$('#numcorr').DataTable(config_num);
    });
  </script>
  );

print_footer();
close OUTF;




#########################
sub print_header {
	my($title) = @_;
	
	print OUTF "<!doctype html public \"-//w3c//dtd html 4.0 transitional//en\">\n";
	print OUTF "<html>\n<head>\n";
	print OUTF "  <title>$title</title>\n" if $title;

	print OUTF qq(
  <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.20/css/jquery.dataTables.css">
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
  <link href="/css/style.css" rel="stylesheet" type="text/css">
  <style>
    .row {
      margin-bottom: 25px;
    }
  </style>
);
	
	
	print OUTF "</head>\n<body>\n";
}

sub print_footer {
	print OUTF "</body>\n</html>\n";
}

sub print_section {
	my($heading, $content) = @_;
	
	print OUTF "  <h2>$heading</h2>\n";
	if (ref($content) eq 'ARRAY') {
		print_block($_) foreach @$content;
	} elsif (ref($content) eq 'HASH') {
		foreach my $blockname (sort keys %$content) {
			print OUTF "    <h3>$blockname</h3>\n";
			print_block($content->{$blockname});
		}
	}
}

sub print_block {
	my($bl) = @_;
	
	if (ref($bl) eq 'ARRAY') {
		my($what, $format) = @$bl;
		if ($format eq 'table') {
			print_table(@$bl);
		}
	} elsif (ref($bl) eq 'HASH') {
		
	} else {
		print OUTF "$bl<br>\n";
	}
}

sub print_table {
	my($what, $format, $table_id, $table_title, $headers, $replace) = @_;
	
	my(@columns, $body);
	
	if (ref($what) eq 'HASH') {
		my @keys = sort keys %$what;
		my %cols;
		while (my($key, $v) = each %$what) {
			$cols{$_}++ foreach keys %$v;
		}
		my @cols = sort keys %cols;
		@columns = ('Column name', map {$replace->{$_} || $_} @cols);
		foreach my $key (@keys) {
			$body .= "<tr><td>$key</td><td>";
			$body .= join("</td><td>", map {$what->{$key}{$_} || " "} @cols);
		}
	} elsif (ref($what) eq 'ARRAY') {
		my @cols = @$headers;
		@columns = map {$replace->{$_} || $_} @cols;
		my $shown;
		foreach my $line (@$what) {
			$body .= "<tr><td>";
			$body .= join("</td><td>", @$line);
		}
	}
	
	print OUTF qq(
            <div class="sorted-table__header">
              <div class="sorted-table__container">
                <h2>$table_title</h2>
              </div>
              );
	
	
	print OUTF qq(<table id="$table_id" class="display compact responsive" border>\n);
	print OUTF qq(<thead><tr><th class="text--gray">);
	print OUTF join("</th><th class=\"text--gray\">", @columns);
	print OUTF "</th></tr></thead>\n";
	#print OUTF qq(<thead class="total_row"></thead>\n);
	print OUTF "<tbody>$body</tbody>\n";
	print OUTF "</table>\n";
	print OUTF "</div>\n";

}

sub read_table {
	my($file) = @_;
	my(@headers, @table);
	
	if ($file =~ /\.gz$/) {
		open F, "gunzip -c $file |";
	} else {
		open F, $file;
	}
	while (<F>) {
		next if /^#/;
		chomp;
		@headers = split /\t/;
		last;
	}
	while (<F>) {
		next if /^#/;
		chomp;
		my(@v) = split /\t/;
		push @table, \@v;
	}
	
	close F;
	return \@headers, \@table;
}




sub read_json {
	my($file) = @_;
	my $json;
	open J, "gunzip -c $file |";
	while (<J>) {
		chomp;
		$json .= $_;
	}
	close J;
	return decode_json($json);
}


sub looks_like_a_docket {
	my($dir) = @_;
	
	return 1 if
		-d $dir && 
		-d "$dir/analyses" && 
		-d "$dir/fingerprints" && 
		-d "$dir/comparisons" && 
		-d "$dir/visualizations";
}

