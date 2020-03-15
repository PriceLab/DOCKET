#!/bin/sh

######### Usages #########
#./run.sh input_dir  output_dir
######### Usages #########
input=$1
output=$2


echo "Comparison between TCGA & GDSC----------"

python docket_integration_interface.py comp $input $output \
    config/Para_sim.json

echo "Integration-mut-drug response:----------"
python docket_integration_interface.py mut_drugResponse $input $output \
    config/Para1_integration.json \
    config/Para2_integration.json

echo "Integration-drug annotation:-------------"
python docket_integration_interface.py  annotation $input $output \
    config/Para1_annotation.json \
    config/Para2_annotation.json

echo "Integration-visulization: ---------------"
python docket_integration_interface.py  visualization $input $output \
    config/Para_visualization.json

#echo "Integration-mut-expression: -------------"
#python docket_integration_interface.py mut_expr $input $output\
#    config/Para1_integration_mut_expr.json \
#    config/Para2_integration_mut_expr.json

echo "---------------Finished-----------------"
