#!/usr/bin/env nextflow
dbin = "$baseDir/bin"
lphbin = "/users/gglusman/proj/LPH/data-fingerprints/bin"

/* parameter defaults */
params.infile = 'test_data.txt'
params.fmt = 'table'
params.docket = 'test_data.docket'
params.L = 2000
params.histL = 50

/* interpret parameters */
input = file(params.infile)
fmt = params.fmt
docket = file(params.docket)
L = params.L
histL = params.histL


/* SECTION: preparation */
process ingest_file {
	/* read the file, store contents as row-wise and column-wise json */
	output:
		val "${docket}/cols_data.json" into colsdata
		val "${docket}/rows_data.json" into rowsdata
	"""
	${dbin}/ingest.pl $input $fmt $docket
	"""
}
/* END SECTION: preparation */



/* SECTION: column histogram pipeline */
process column_histograms {
	/* column-wise histograms of observed values */
	input: val cd from colsdata
	output: val "${docket}/cols_hist.json" into colshist
	"""
	${dbin}/compute_hist.pl $cd cols $docket
	"""
}
process compute_col_hist_fingerprints {
	/* compute and serialize fingerprints of column-wise histograms of observed values */
	input: val ch from colshist
	output: val "${docket}/cols_hist_fp" into colshistfp
	"""
	${dbin}/compute_hist_fp.pl $ch cols $histL $docket
	"""
}
process compare_col_hist_fingerprints {
	/* compare fingerprints of column-wise histograms of observed values */
	/* ### issue: recomputes every time, will be slow for large data sets ### */
	input: val chf from colshistfp
	"""
	${lphbin}/searchLPHs.pl $chf 0 1000000 ${chf}.aaa.hist | gzip -c > ${chf}.aaa.gz
	"""
}
process index_col_hist_fingerprints {
	/* index fingerprints of column-wise histograms, using annoy */
	/* ### issue: recomputes every time ### */
	input: val chf from colshistfp
	output: val "${docket}/cols_hist_fp" into colshistfpindex
	"""
	${dbin}/annoyIndexGz.py --file ${chf}.raw.gz --L $histL --norm 1 --out $chf
	"""
}
process KNN_col_hist_fingerprints {
	/* find k nearest neighbors of column-wise histograms, using annoy */
	/* ### issue: recomputes every time ### */
	input: val chf from colshistfpindex
	"""
	${dbin}/annoyQueryAll.py --index ${chf} --L $histL --k 100 | gzip -c > ${chf}.knn.gz
	"""
}
/* END SECTION: column histogram pipeline */



/* SECTION: row histogram pipeline */
process row_histograms {
	/* row-wise histograms of observed values */
	input: val rd from rowsdata
	output: val "${docket}/rows_hist.json" into rowshist
	"""
	${dbin}/compute_hist.pl $rd rows $docket
	"""
}
/* END SECTION: row histogram pipeline */



/* SECTION: row analysis pipeline */
process compute_row_fingerprints {
	/* row-wise fingerprints */
	input: val rd from rowsdata
	output: val "${docket}/rows_fp" into rowsfp
	"""
	${dbin}/compute_fp.pl $rd rows $L $docket
	"""
}
process PCA_row_fingerprints {
	/* compute PCA on fingerprints of rows */
	/* ### issue: recomputes every time, will be slow for large data sets ### */
	input: val rfp from rowsfp
	output: val "${docket}/rows_fp" into rowsfppca
	"""
	${dbin}/pca.py ${rfp}.raw.gz --L $L | gzip -c > ${rfp}.pca.gz
	"""
}
process plot_PCA_row_fingerprints {
	/* plot PC1-PC2 on fingerprints of rows */
	input: val rfp from rowsfppca
	"""
	${dbin}/plotpca.py ${rfp}.pca.gz ${rfp}.pc1_pc2.pdf
	"""
}
process compare_row_fingerprints {
	/* compare fingerprints of rows */
	/* ### issue: recomputes every time, will be slow for large data sets ### */
	input: val rfp from rowsfp
	"""
	${lphbin}/searchLPHs.pl $rfp 0 1000000 ${rfp}.aaa.hist | gzip -c > ${rfp}.aaa.gz
	"""
}
process index_row_fingerprints {
	/* index fingerprints of rows, using annoy */
	/* ### issue: recomputes every time ### */
	/* ### issue: pca.py doesn't expect gzipped input ### */
	input: val rfp from rowsfp
	output: val "${docket}/rows_fp" into rowsfpindex
	"""
	${dbin}/annoyIndexGz.py --file ${rfp}.raw.gz --L $L --norm 1 --out $rfp
	"""
}
process KNN_row_fingerprints {
	/* find k nearest neighbors of rows, using annoy */
	/* ### issue: recomputes every time ### */
	input: val rfp from rowsfpindex
	"""
	${dbin}/annoyQueryAll.py --index ${rfp} --L $L --k 100 | gzip -c > ${rfp}.knn.gz
	"""
}
/* END SECTION: row analysis pipeline */


/* SECTION: column analysis pipeline */
process compute_col_fingerprints {
	/* col-wise fingerprints */
	input: val rd from colsdata
	output: val "${docket}/cols_fp" into colsfp
	"""
	${dbin}/compute_fp.pl $rd cols $L $docket
	"""
}
process PCA_col_fingerprints {
	/* compute PCA on fingerprints of columns */
	/* ### issue: recomputes every time, will be slow for large data sets ### */
	input: val rfp from colsfp
	output: val "${docket}/cols_fp" into colsfppca
	"""
	${dbin}/pca.py ${rfp}.raw.gz --L $L | gzip -c > ${rfp}.pca.gz
	"""
}
process plot_PCA_col_fingerprints {
	/* plot PC1-PC2 on fingerprints of columns */
	input: val rfp from colsfppca
	"""
	${dbin}/plotpca.py ${rfp}.pca.gz ${rfp}.pc1_pc2.pdf
	"""
}
process compare_col_fingerprints {
	/* compare fingerprints of columns */
	/* ### issue: recomputes every time, will be slow for large data sets ### */
	input: val rfp from colsfp
	"""
	${lphbin}/searchLPHs.pl $rfp 0 1000000 ${rfp}.aaa.hist | gzip -c > ${rfp}.aaa.gz
	"""
}
process index_col_fingerprints {
	/* index fingerprints of columns, using annoy */
	/* ### issue: recomputes every time ### */
	/* ### issue: pca.py doesn't expect gzipped input ### */
	input: val rfp from colsfp
	output: val "${docket}/cols_fp" into colsfpindex
	"""
	${dbin}/annoyIndexGz.py --file ${rfp}.raw.gz --L $L --norm 1 --out $rfp
	"""
}
process KNN_col_fingerprints {
	/* find k nearest neighbors of columns, using annoy */
	/* ### issue: recomputes every time ### */
	input: val rfp from colsfpindex
	"""
	${dbin}/annoyQueryAll.py --index ${rfp} --L $L --k 100 | gzip -c > ${rfp}.knn.gz
	"""
}
/* END SECTION: column analysis pipeline */

