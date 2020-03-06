#!/bin/sh

echo "Comparison:-----------------------------"
python docket_integration_interface.py Output/ comp \
    config/Para_sim.json

echo "Integration-mut-drug response:----------"
python docket_integration_interface.py Output/  mut_drugResponse \
    config/Para1_integration.json \
    config/Para2_integration.json

echo "Integration-drug annotation:-------------"
python docket_integration_interface.py Output/  annotation \
    config/Para1_annotation.json \
    config/Para2_annotation.json

echo "Integration-visulization: ---------------"
python docket_integration_interface.py Output/  visualization \
    config/Para_visualization.json

echo "Integration-mut-expression: -------------"
python docket_integration_interface.py Output/  mut_expr \
    config/Para1_integration_mut_expr.json \
    config/Para2_integration_mut_expr.json

echo "---------------Finished-----------------"
