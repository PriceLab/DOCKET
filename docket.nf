#!/usr/bin/env nextflow
dbin = "$baseDir/bin"
lphbin = "/users/gglusman/proj/LPH/data-fingerprints/bin"

/* parameter defaults */
params.infile = 'test_data.txt'
params.format = 'table'
params.docket = 'test_data.docket'
params.L = 2000
params.histL = 50
params.minTriples = 10

/* interpret parameters */
input = file(params.infile)
format = params.format
docket = file(params.docket)
L = params.L
histL = params.histL


/* SECTION: preparation */
process ingest_file {
	/* read the file, store contents as row-wise and column-wise json */
	publishDir docket, mode: 'copy'
	output:
		file 'cols_data.json.gz' into colsdata
		file 'rows_data.json.gz' into rowsdata
	"""
	${dbin}/ingest.pl $input $format
	"""
}
/* END SECTION: preparation */



/* SECTION: column histogram pipeline */
process column_histograms {
	/* column-wise histograms of observed values */
	publishDir docket, mode: 'copy'
	input: file cd from colsdata
	output: file 'cols_hist.json.gz' into colshist
	"""
	$dbin/compute_hist.pl $cd | gzip -c > cols_hist.json.gz
	"""
}
process compute_col_hist_fingerprints {
	/* compute and serialize fingerprints of column-wise histograms of observed values */
	publishDir docket, mode: 'copy'
	input: file ch from colshist
	output: file 'cols_hist_fp.raw.gz' into colshistfp
	output: file 'cols_hist_fp.fp' into colshistfpser
	"""
	$dbin/compute_fp.pl $ch $histL | gzip -c > cols_hist_fp.raw.gz
	$lphbin/serializeLPH.pl cols_hist_fp $histL 1 1 cols_hist_fp.raw.gz
	"""
}
process PCA_col_hist_fingerprints {
	/* compute PCA on fingerprints of column histograms */
	publishDir docket, mode: 'copy'
	input: file chfp from colshistfp
	output: file 'cols_hist_fp.pca.gz' into colshistfppca
	"""
	$dbin/pca.py $chfp --L $histL | gzip -c > cols_hist_fp.pca.gz
	"""
}
process plot_PCA_col_hist_fingerprints {
	/* plot PC1-PC2 on fingerprints of column histograms */
	publishDir docket, mode: 'copy'
	input: file chfp from colshistfppca
	output: file 'cols_hist_fp.pc1_pc2.pdf'
	"""
	$dbin/plotpca.py $chfp cols_hist_fp.pc1_pc2.pdf
	"""
}
process compare_col_hist_fingerprints {
	/* compare fingerprints of column-wise histograms of observed values */
	publishDir docket, mode: 'copy'
	input: file chf from colshistfpser
	output: file 'cols_hist_fp.aaa.gz' into chfaaa
	output: file 'cols_hist_fp.aaa.hist' into chfaaahist
	"""
	$lphbin/searchLPHs.pl $chf 0 1000000 cols_hist_fp.aaa.hist | gzip -c > cols_hist_fp.aaa.gz
	"""
}
process index_col_hist_fingerprints {
	/* index fingerprints of column-wise histograms, using annoy */
	publishDir docket, mode: 'copy'
	input: file chf from colshistfp
	output: file 'cols_hist_fp.tree' into colshistfpindex
	output: file 'cols_hist_fp.names' into colshistfpnames
	"""
	$dbin/annoyIndexGz.py --file $chf --L $histL --norm 1 --out cols_hist_fp
	"""
}
process KNN_col_hist_fingerprints {
	/* find k nearest neighbors of column-wise histograms, using annoy */
	publishDir docket, mode: 'copy'
	input: file chfi from colshistfpindex
	input: file chfn from colshistfpnames
	output: file 'cols_hist_fp.knn.gz'
	"""
	$dbin/annoyQueryAll.py --index $chfi --names $chfn --L $histL --k 100 | gzip -c > cols_hist_fp.knn.gz
	"""
}
/* END SECTION: column histogram pipeline */



/* SECTION: row histogram pipeline */
process row_histograms {
	/* row-wise histograms of observed values */
	publishDir docket, mode: 'copy'
	input: file rd from rowsdata
	output: file 'rows_hist.json.gz' into rowshist
	"""
	$dbin/compute_hist.pl $rd | gzip -c > rows_hist.json.gz
	"""
}
/* END SECTION: row histogram pipeline */



/* SECTION: row analysis pipeline */
process compute_row_fingerprints {
	/* row-wise fingerprints */
	publishDir docket, mode: 'copy'
	input: file rd from rowsdata
	output: file 'rows_allfp.raw.gz' into rowsallfp
	"""
	$dbin/compute_fp.pl $rd $L | gzip -c > rows_allfp.raw.gz
	"""
}
process trim_row_fingerprints {
	/* trim row-wise fingerprints by triples */
	publishDir docket, mode: 'copy'
	input: file rfp from rowsallfp
	output: file 'rows_fp.raw.gz' into rowstrimfp
	"""
	$dbin/filterTable.pl $rfp 1 $params.minTriples | gzip -c > rows_fp.raw.gz
	"""
}
process serialize_trim_row_fingerprints {
	/* serialize trimmed row-wise fingerprints */
	publishDir docket, mode: 'copy'
	input: file rfp from rowstrimfp
	output: file 'rows_fp.fp' into rowsfp
	output: file 'rows_fp.id' into rowsfpids
	"""
	$lphbin/serializeLPH.pl rows_fp $L 1 1 $rfp
	"""
}
process PCA_row_fingerprints {
	/* compute PCA on fingerprints of rows */
	publishDir docket, mode: 'copy'
	input: file rfp from rowstrimfp
	output: file 'rows_fp.pca.gz' into rowsfppca
	"""
	$dbin/pca.py $rfp --L $L | gzip -c > rows_fp.pca.gz
	"""
}
process plot_PCA_row_fingerprints {
	/* plot PC1-PC2 on fingerprints of rows */
	publishDir docket, mode: 'copy'
	input: file pca from rowsfppca
	output: file 'rows_fp.pc1_pc2.pdf'
	"""
	$dbin/plotpca.py $pca rows_fp.pc1_pc2.pdf
	"""
}
process compare_row_fingerprints {
	/* compare fingerprints of rows */
	publishDir docket, mode: 'copy'
	input: file rfp from rowsfp
	output: file 'rows_fp.aaa.gz' into rowsaaa
	output: file 'rows_fp.aaa.hist' into rowsaaahist
	"""
	$lphbin/searchLPHs.pl $rfp 0 1000000 rows_fp.aaa.hist | gzip -c > rows_fp.aaa.gz
	"""
}
process index_row_fingerprints {
	/* index fingerprints of rows, using annoy */
	publishDir docket, mode: 'copy'
	input: file rfp from rowstrimfp
	output: file 'rows_fp.tree' into rowsfpindex
	output: file 'rows_fp.names' into rowsfpnames
	"""
	$dbin/annoyIndexGz.py --file $rfp --L $L --norm 1 --out rows_fp
	"""
}
process KNN_row_fingerprints {
	/* find k nearest neighbors of rows, using annoy */
	publishDir docket, mode: 'copy'
	input: file rfpi from rowsfpindex
	input: file rfpn from rowsfpnames
	output: file 'rows_fp.knn.gz'
	"""
	$dbin/annoyQueryAll.py --index $rfpi --names $rfpn --L $L --k 100 | gzip -c > rows_fp.knn.gz
	"""
}
/* END SECTION: row analysis pipeline */


/* SECTION: column analysis pipeline */
process compute_col_fingerprints {
	/* col-wise fingerprints */
	publishDir docket, mode: 'copy'
	input: file cd from colsdata
	output: file 'cols_allfp.raw.gz' into colsallfp
	"""
	$dbin/compute_fp.pl $cd $L | gzip -c > cols_allfp.raw.gz
	"""
}
process trim_col_fingerprints {
	/* trim col-wise fingerprints by triples */
	publishDir docket, mode: 'copy'
	input: file cfp from colsallfp
	output: file 'cols_fp.raw.gz' into colstrimfp
	"""
	$dbin/filterTable.pl $cfp 1 $params.minTriples | gzip -c > cols_fp.raw.gz
	"""
}
process serialize_trim_col_fingerprints {
	/* serialize trimmed col-wise fingerprints */
	publishDir docket, mode: 'copy'
	input: file cfp from colstrimfp
	output: file 'cols_fp.fp' into colsfp
	output: file 'cols_fp.id' into colsfpids
	"""
	$lphbin/serializeLPH.pl cols_fp $L 1 1 $cfp
	"""
}
process PCA_col_fingerprints {
	/* compute PCA on fingerprints of columns */
	publishDir docket, mode: 'copy'
	input: file cfp from colstrimfp
	output: file 'cols_fp.pca.gz' into colsfppca
	"""
	$dbin/pca.py $cfp --L $L | gzip -c > cols_fp.pca.gz
	"""
}
process plot_PCA_col_fingerprints {
	/* plot PC1-PC2 on fingerprints of columns */
	publishDir docket, mode: 'copy'
	input: file pca from colsfppca
	output: file 'cols_fp.pc1_pc2.pdf'
	"""
	$dbin/plotpca.py $pca cols_fp.pc1_pc2.pdf
	"""
}
process compare_col_fingerprints {
	/* compare fingerprints of columns */
	publishDir docket, mode: 'copy'
	input: file cfp from colsfp
	output: file 'cols_fp.aaa.gz' into colsaaa
	output: file 'cols_fp.aaa.hist' into colsaaahist
	"""
	$lphbin/searchLPHs.pl $cfp 0 1000000 cols_fp.aaa.hist | gzip -c > cols_fp.aaa.gz
	"""
}
process index_col_fingerprints {
	/* index fingerprints of columns, using annoy */
	publishDir docket, mode: 'copy'
	input: file cfp from colstrimfp
	output: file 'cols_fp.tree' into colsfpindex
	output: file 'cols_fp.names' into colsfpnames
	"""
	$dbin/annoyIndexGz.py --file $cfp --L $L --norm 1 --out cols_fp
	"""
}
process KNN_col_fingerprints {
	/* find k nearest neighbors of columns, using annoy */
	publishDir docket, mode: 'copy'
	input: file cfpi from colsfpindex
	input: file cfpn from colsfpnames
	output: file 'cols_fp.knn.gz'
	"""
	$dbin/annoyQueryAll.py --index $cfpi --names $cfpn --L $L --k 100 | gzip -c > cols_fp.knn.gz
	"""
}
/* END SECTION: column analysis pipeline */
