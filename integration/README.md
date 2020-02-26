##Packages needed##
import matplotlib.pyplot as plt
import pandas as pd
import scipy
import numpy as np
import math
import plotly
import plotly.express as px
from scipy import stats 
import statsmodels.stats.multitest as multi
import scipy.stats as stats
import sys
import json

##An example of integration of gene mutation and drug sensitivity##
Command:
python docket_integration_interface.py Output/  mut_drugResponse data/Para1_integration.json data/Para2_integration.json

Parameters description:
Output/ : the output directory
mut_drugResponse: Label for which process will the integration process do
data/Para1_integration.json: Parameter file
data/Para2_integration.json: Parameter file

## An example of annotate the knoledge graph## 
python docket_integration_interface.py Output/  annotation data/Para1_annotation.json data/Para2_annotation.json

Parameters description:
Output/ : the output directory
annotation: Label for which process will the integration process do
data/Para1_annotation.json: Parameter file 
data/Para2_annotation.json: Parameter file
