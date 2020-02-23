#!/bin/env nextflow

scripts = "$baseDir/scripts"

/* Parameter defaults */
params.infile = 'data/iris_tab.data'
params.docket = 'test_enrichment.docket'
params.pca_n = 50
params.fill_na = true

/* local variable names */
infile = file(params.infile)
docket = file(params.docket)
pca_n = params.pca_n
fill_na = params.fill_na

process preprocess_input {
    /* Pre-process input files to get numeric data on which to cluster and attribute data for enrichment analysis */
    publishDir docket, mode: 'copy'

    output:
    file 'rows_numeric_data.txt.gz' into rows_numdata
    file 'cols_numeric_data.txt.gz' into cols_numdata
    file 'cols_attribute_data.json.gz' into cols_attrdata
    file 'cols_attribute_counts.json.gz' into cols_attrcounts

	"""
	${scripts}/preprocess_input.py \
	  --file $infile \
	  --fill_na $fill_na \
	  --rows_data rows_numeric_data.txt.gz \
	  --cols_data cols_numeric_data.txt.gz \
	  --attr_data cols_attribute_data.json.gz \
	  --attr_counts cols_attribute_counts.json.gz
	"""
}

process compute_numeric_pca {
    /* Compute PCA on row-wise data */
    publishDir docket, mode: 'copy'

    input:
    /* Use fingerprint results, if available; Otherwise, use original data */
    file numdata from rows_numdata

    output:
    file 'rows_numeric_pca.pca.gz' into rowspca

    """
    ${scripts}/compute_pca.py \
      --source $numdata \
      --out rows_numeric_pca.pca.gz \
      --n_comp $pca_n
    """
}

process cluster_numeric_hier {
    /* Compute row-wise clustering */
    publishDir docket, mode: 'copy'

    input:
    file rpca from rowspca

    output:
    file 'cluster_labels.txt.gz' into rows_hier_clust
    file 'cluster_members.json.gz' into row_clust_members

    """
    ${scripts}/cluster_hier.py \
      --source $rpca \
      --cl_labels_out cluster_labels.txt.gz \
      --cl_members_out cluster_members.json.gz
    """
}

process compute_enrich {
    /* Compute enrichment */
    publishDir docket, mode: 'copy'

    input:
    file cattrdata from cols_attrdata
    file cattrcnts from cols_attrcounts
    file rhc from rows_hier_clust

    output:
    file 'enrichment_results.txt'

    """
    ${scripts}/compute_enrich.py \
      --attr_data $cattrdata \
      --attr_counts $cattrcnts \
      --cluster_data $rhc \
      --out enrichment_results.txt
    """
}

process copy_code {
    /* Copy code needed for visualizing results */
    publishDir "$docket/code", mode: 'copy'

    output:
    file '__init__.py'
    file 'results.py'

    """
    cp '$baseDir/common/results.py' .
    touch __init__.py
    """
}

process copy_notebooks {
    /* Copy Jupyter notebook for visualizing results */
    publishDir docket, mode: 'copy'

    output:
    file 'visualize-enrichment-results.ipynb'

    """
    cp '$baseDir/notebooks/visualize-enrichment-results.ipynb' .
    """
}
