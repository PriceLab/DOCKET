#!/bin/env nextflow

pyscripts = "$baseDir/scripts"

/* Parameter defaults */
params.infile = 'data/small_table.txt'
params.docket = 'small_table.docket'

/* local variable names */
infile = file(params.infile)
docket = file(params.docket)

process ingest_file {
    /* read the file, store contents as row-wise and column-wise json */
    publishDir docket, mode: 'copy'

    output:
    file 'rows_data.json.gz' into rowsdata
    file 'cols_data.json.gz' into colsdata

	"""
	${pyscripts}/ingest_pd.py \
	  --infile $infile \
	  --sep '\t' \
	  --rows_out rows_data.json.gz \
	  --cols_out cols_data.json.gz
	"""
}

process compute_histograms {
	/* Compute row-wise and column-wise histograms (occurrence counts) of observed values */
	publishDir docket, mode: 'copy'

	input:
	file rd from rowsdata
	file cd from colsdata

	output:
	file 'rows_hist.json.gz' into rowshist
	file 'cols_hist.json.gz' into colshist

	"""
	${pyscripts}/compute_hist.py \
	  --source $rd \
	  --out rows_hist.json.gz
	${pyscripts}/compute_hist.py \
	  --source $cd \
	  --out cols_hist.json.gz
	"""
}
