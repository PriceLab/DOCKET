#!/bin/env nextflow

pyscripts = "$baseDir/scripts"

/* Parameter defaults */
params.infile = 'data/cluster_sample.csv'
params.docket = 'cluster_sample.docket'
params.sep = ','
params.index_col = 0
params.header_row = 0
params.L = 40
params.pca_comp = 10

/* local variable names */
infile = file(params.infile)
docket = file(params.docket)
sep = params.sep
index_col = params.index_col
header_row = params.header_row
L = params.L

process ingest_file {
    /* read the file, store contents as row-wise and column-wise json */
    publishDir docket, mode: 'copy'

    output:
    file 'rows_data.json.gz' into rowsdata
    file 'cols_data.json.gz' into colsdata

	"""
	${pyscripts}/ingest_pd.py \
	  --infile $infile \
	  --sep $sep \
	  --index_col $index_col \
	  --header_row $header_row \
	  --rows_out rows_data.json.gz \
	  --cols_out cols_data.json.gz
	"""
}

process compute_pca {
    /* Compute row-wise and column-wise PCA on fingerprints */
    publishDir docket, mode: 'copy'

    input:
    file rd from rowsdata
    file cd from colsdata

    output:
    file 'rows_pca.pca.gz' into rowspca
    file 'cols_pca.pca.gz' into colspca

    """
    ${pyscripts}/compute_pca.py \
      --source $rd \
      --out rows_pca.pca.gz \
      --n_comp 10
    ${pyscripts}/compute_pca.py \
      --source $cd \
      --out cols_pca.pca.gz \
      --n_comp 10
    """
}

process cluster_hier {
    /* Compute row-wise and column-wise clustering */
    publishDir docket, mode: 'copy'

    input:
    file rpca from rowspca
    file cpca from colspca

    output:
    file 'rows_hier_clusters.txt' into rows_hier_clust
    file 'cols_hier_clusters.txt' into cols_hier_clust

    """
    ${pyscripts}/cluster_hier.py \
      --source $rpca \
      --out rows_hier_clusters.txt
    ${pyscripts}/cluster_hier.py \
      --source $cpca \
      --out cols_hier_clusters.txt
    """
}

process copy_notebook {
    /* Copy Jupyter notebook for visualizing results */
    publishDir docket, mode: 'copy'

    output:
    file 'visualize-pca-clusters.ipynb'

    """
    cp '$baseDir/notebooks/visualize-pca-clusters.ipynb' .
    """
}
