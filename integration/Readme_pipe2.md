
## This is a seperate pipeline that filter the variants in GDSC mutation data with the somatic mutations in TCGA and Cosmic dataset, and use the filtered varients to analyze the association between tumor related variants and drug response.

## Run in the docker enviroment:
Follow the instruction in the README.md in the upper dirctory.
```bash
$ docker-compose build
$ docker-compose up
$ docker-compose exec docket bash
```
Once you are in the docker enviroment: [jovyan@137216bcc469:/app$ , 
you can run the following the example with the input files


### About the input files:
#### Parameter files in /app/integration/config/config_LUAD_GDSC_TCGA
Para1_annotation.json
Para1_integration_mut_expr.json
Para2_annotation.json
Para2_integration_mut_expr.json
para_integration_filtered.json
Para_sim.json
Para_visualization.json

#### Datasets:
#### Datasets for annotation in /app/integration/Dataset
GDSC_Drug_anno.csv
variants.xlsx

#### input multiple omics data in /app/integration/data/Data_input_for_LUAD
Drug_GDSC_matrix.csv
Exp_GDSC_matrix.csv
GDSC_drug.csv
GDSC_Expr.csv
GDSC_MUT.csv
Mut_GDSC_matrix.csv
Mut_site_GDSC.csv
Mut_site_TCGA.csv
Mut_TCGA_matrix.csv
TCGA_mut.csv

```bash
$ ./run_GDSC_TCGA.sh /app/integration/data/Data_input_for_LUAD/ /app/integration/Output_LUAD_demo/
```

Parameters description:
/app/integration/data/Data_input_for_LUAD/: absolute directory for the input data
/app/integration/Output_LUAD_demo/: absolute directory for the output; 

Notes: 
1. '/' at the end is needed!
2. /app/integration/Output_LUAD_demo/: the output directory need to be a subdirectory of 'integration'