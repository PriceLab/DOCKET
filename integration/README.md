## Packages needed
#### Make sure jupyter is in your PATH environment, users need to check their envrionment if the following libraries are in their environment
Command:
```bash
$ pip install jupyter
$ pip install notebook
$ pip install pandas
$ pip install matplotlib 
$ pip install numpy scipy
$ pip install statsmodels
$ pip install plotly
$ pip install cyjupyter
```
## Run through the example
Before running the following scripts, make sure you have checked the 'config' directory, and have all the input files in the 'input_dir' directory.

Command:
```bash
./run.sh input_dir/ Output_dir/
```

This bash file includes
1. The comparison between the TCGA dataset and GDSC dataset in the mutation level, and select genes which are highly  frequently altered in the patient derived tumor samples compared to the normal samples, and among these somatic mutated genes, select the genes in the GDSC(cell line derived mutation profiles without paired normal samples) show similar mutation sites with the TCGA dataset.

2. Integration of gene mutation and drug sensitivity in the GDSC dataset to get the knowlege graph about "gene-mutation ~ Drug": 
   Node: 
        gene(mutation) 
        Drug 
   association: 
        Sensitivity (P-value, size effect)
        Resistance
    context: 
        tumor types: LUAD
        sample types: cell lines
        dataset used: GDSC
        number of samples: 

3. Annotate the "gene-mutation ~ Drug" knowledge graph with exteral knowledge about drug targeted genes or targeted sigalig pathways, and generating the knowlege graph about "gene-mutation ~ drug target" or "gene-mutation ~ signaling pathway":
    "gene-mutation ~ gene"
    Node: 
        gene(mutation)
        gene(drug target)
    association:
        Sensitivity
        Resistance
    context: 
        tumor types: LUAD
        sample types: cell lines
        dataset used: GDSC
        number of samples: 

    "gene-mutation ~ gene signaling"
    Node: 
        gene(mutation)
        signaling pathway(drug targeted)
    association:
        Sensitivity (enrichment p-value)
        Resistance (enrichment p-value)
    context:
        tumor types: LUAD
        sample types: cell lines
        dataset used: GDSC
        number of samples: 

4. Integration of gene mutation and gene expression in the cancer cell lines, and get the knowledge graph about the "gene-mutation ~ gene-expression". 
   "gene-mutation ~ gene-expression"
    Node: 
        gene(mutation)
        gene(expression)
    association:
        high expression (p-value, effect size)
        low expression (p-value, effect size)
    context:
        tumor types: LUAD
        sample types: cell lines
        dataset used: GDSC
        number of samples: 

5. Visulize the knowledge graph
   
## Seperate steps

## An example of comparison between GDSC dataset and TCGA dataset in the genetic level
#### It will detected the most high frequently mutated genes, and compare the mutation sites from the GDSC data set
Command:
```bash
$ python docket_integration_interface.py comp  \
input_dir/ \
output_dir/  \
config/Para_sim.json
```
Parameters description:
Output/ : the output directory
comp: Label for which process will the integration process do
config/Para_sim.json: Parameter file

## An example of integration of gene mutation and drug sensitivity
Command:
```bash
$ python docket_integration_interface.py mut_drugResponse \
 input_dir/  \
 output_dir/  \
 config/Para1_integration.json \
 config/Para2_integration.json
```

Parameters description:
Output/ : the output directory
mut_drugResponse: Label for which process will the integration process do
config/Para1_integration.json: Parameter file
config/Para2_integration.json: Parameter file

## An example of annotate the knowledge graph
```bash
$ python docket_integration_interface.py annotation \
 input_dir/  \
 output_dir/  \
 config/Para1_annotation.json \ 
 config/Para2_annotation.json

```

Parameters description:
Output/ : the output directory
annotation: Label for which process will the integration process do
config/Para1_annotation.json: Parameter file 
config/Para2_annotation.json: Parameter file


## An example of visualize the knowledge graph
```bash
$ python docket_integration_interface.py visualization  \
input_dir/  \
output_dir/  \
config/Para_visualization.json   
```

Parameters description:
Output/ : the output directory
visualization: Label for which process will the integration process do
config/Para_visulization.json: Parameter file


## An example of integration of gene mutation and gene expression
```bash
$ python docket_integration_interface.py mut_expr  \
input_dir/  \
output_dir/  \
config/Para1_integration_mut_expr.json config/Para2_integration_mut_expr.json
```

Parameters description:
Output/ : the output directory
mut_drugResponse: Label for which process will the integration process do
config/Para1_integration_mut_expr.json: Parameter file
cconfig/Para2_integration_mut_expr.json: Parameter file
