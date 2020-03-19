#!/bin/sh

######### Usages #########
#./run.sh input_dir  output_dir
######### Usages #########
input=$1
output=$2


echo "Integration_GDSC_TCGA_drug_response"
python docket_integration_interface.py mut_filter_drugResponse $input $output \
	config/config_LUAD_GDSC_TCGA/para_integration_filtered.json

echo "Integration-drug annotation:-------------"
python docket_integration_interface.py  annotation $input $output \
    config/config_LUAD_GDSC_TCGA/Para1_annotation.json \
    config/config_LUAD_GDSC_TCGA/Para2_annotation.json

echo "Integration-visulization: ---------------"
python docket_integration_interface.py  visualization $input $output \
    config/config_LUAD_GDSC_TCGA/Para_visualization.json

echo "---------------Finished-----------------"
