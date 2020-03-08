#!/bin/env nextflow
scripts = "$baseDir/scripts"

/* Similarity comparison defaults */
params.cell_line_file = "$baseDir/data/Mut_site_LUAD_GDSC.csv"
params.tissue_file = "$baseDir/data/Mut_site_LUAD_TCGA.csv"
params.similarity_config = "$baseDir/test/similarity_compare.config"

/* Mutation drug response analysis defaults */
params.mut_matrix_file = "$baseDir/data/LUAD_GDSC_mut_matrix.csv"
params.drug_response_file = "$baseDir/data/LUAD_GDSC_drugResponse_matrix.csv"
params.drug_response_config = "$baseDir/test/drug_response.config"

/* Annotation and enrichment analysis defaults */
params.annotations_file = "$baseDir/data/GDSC_Drug_anno.csv"
params.annotations_config = "$baseDir/test/annotations.config"

params.docket = "$baseDir/test/test_integration.docket"

/* interpret parameters */
cell_line_file = file(params.cell_line_file)
tissue_file = file(params.tissue_file)
similarity_config = file(params.similarity_config)
mut_matrix_file = file(params.mut_matrix_file)
drug_response_file = file(params.drug_response_file)
drug_response_config = file(params.drug_response_config)
annotations_file = file(params.annotations_file)
annotations_config = file(params.annotations_config)
docket = file(params.docket)


/* Takes two files, one containing cell line gene mutation data and the other containing tumor tissue gene mutation   */
/* data. Compare the similarity of mutations (i.e. gene and mutation site within the gene) by estimating the ratio of */
/* identical mutation sites between the two data sets.                                                                */
process integrate_similarity_compare {
	publishDir "$docket/integration", mode: 'copyNoFollow'

    output:
    file 'similar_mutation_sites.csv' into similarity_out

	"""
	${scripts}/integrate_similarity_compare.py \
	  --cell_line_file $cell_line_file \
	  --tissue_file $tissue_file \
	  --config_file $similarity_config \
	  --file_out similar_mutation_sites.csv
	"""
}


/* Takes two files, one containing cell line mutation matrix data and the other containing cell line drug response    */
/* data. Merge these two tables and run drug sensitivity analysis for mutations in a specified list of genes.         */
process integrate_drug_response {
	publishDir "$docket/integration", mode: 'copyNoFollow'

    input:
    file similarity from similarity_out

    output:
    file 'mutation_drug_merged.csv' into drug_merged_out
    file 'mutation_drug_pairs.csv' into drug_pairs_out

	"""
	${scripts}/integrate_drug_response.py \
	  --mut_matrix_file $mut_matrix_file \
	  --drug_response_file $drug_response_file \
	  --mut_similarity_file $similarity \
	  --config_file $drug_response_config \
	  --merged_out mutation_drug_merged.csv \
	  --mut_drug_pairs_out mutation_drug_pairs.csv
	"""
}


/* # Takes two files, one containing drug/mutation sensitivity associations and one containing drug annotations.      */
process integrate_annotations {
	publishDir "$docket/integration", mode: 'copyNoFollow'

    input:
    file drug_pairs from drug_pairs_out

    output:
    file 'mutation_drug_pairs_annotated.csv' into annotations_out
    file 'mutation_drug_pair_enrichment.csv' into enrichment_out

	"""
	${scripts}/integrate_annotations.py \
	  --associations_file $drug_pairs \
	  --annotations_file $annotations_file \
	  --config_file $annotations_config \
	  --annotations_out mutation_drug_pairs_annotated.csv \
	  --enrichment_out mutation_drug_pair_enrichment.csv
	"""
}


/* Copy Jupyter notebook for visualizing results */
process copy_notebook {
    publishDir "$docket/integration", mode: 'copyNoFollow'

    output:
    file 'review-docket-integrate-results.ipynb'

    """
    cp '$baseDir/notebooks/review-docket-integrate-results.ipynb' .
    """
}
