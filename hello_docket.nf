#!/usr/bin/env nextflow
pyscripts = "$baseDir/scripts"

/* Parameter defaults */
params.infile = 'data/sample/hello_docket/hello_docket_partial.txt'
params.docket = 'hello_docket.docket'
params.L = 200

/* Interpret parameters */
infile = file(params.infile)
docket = file(params.docket)
L = params.L

/* SECTION: Preparation */

// Read file and store contents as row-wise and column-wise json
process ingest_file {
    output:
    file('rows_data.json') into rowsdata
    file('cols_data.json') into colsdata

    """
    python ${pyscripts}/ingest.py \
      --source $infile \
      --comment '#' \
      --rows_out 'rows_data.json' \
      --cols_out 'cols_data.json'
    """
}

/* SECTION: Row and column histogram pipeline */

// Get row- and column-wise value occurrence counts (histograms)
process compute_histograms {
    input:
    file('rows_data.json') from rowsdata
    file('cols_data.json') from colsdata

    output:
    file('rows_hist.json') into rowshist
    file('cols_hist.json') into colshist

    """
    python ${pyscripts}/compute_hist.py \
      --source 'rows_data.json' \
      --out 'rows_hist.json'

    python ${pyscripts}/compute_hist.py \
      --source 'cols_data.json' \
      --out 'cols_hist.json'
    """
}

// Convert row- and column-wise value occurrence counts to fingerprints
process compute_histogram_fingerprints {
    input:
    file('rows_hist.json') from rowshist
    file('cols_hist.json') from colshist

    output:
    file('rows_histfp.json') into rowshistfp
    file('cols_histfp.json') into colshistfp

    """
    python ${pyscripts}/compute_fp.py \
      --source 'rows_hist.json' \
      --L $L \
      --out 'rows_histfp.json'

    python ${pyscripts}/compute_fp.py \
      --source 'cols_hist.json' \
      --L $L \
      --out 'cols_histfp.json'
    """
}
