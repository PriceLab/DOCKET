## Packages needed

```python
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
import cyjupyter
```

## An example of comparison between GDSC dataset and TCGA dataset in the genetic level
#### It will detected the most high frequently mutated genes, and compare the mutation sites from the GDSC data set
Command:
```bash
$ python docket_integration_interface.py \ 
    Output/ comp \
    config/Para_sim.json
```
Parameters description:
Output/ : the output directory
comp: Label for which process will the integration process do
config/Para_sim.json: Parameter file

## An example of integration of gene mutation and drug sensitivity
Command:
```bash
$ python docket_integration_interface.py \
    Output/  mut_drugResponse \
    config/Para1_integration.json config/Para2_integration.json
```

Parameters description:
Output/ : the output directory
mut_drugResponse: Label for which process will the integration process do
config/Para1_integration.json: Parameter file
config/Para2_integration.json: Parameter file

## An example of annotate the knowledge graph
```bash
$ python docket_integration_interface.py \
    Output/  annotation \
    config/Para1_annotation.json config/Para2_annotation.json
```

Parameters description:
Output/ : the output directory
annotation: Label for which process will the integration process do
config/Para1_annotation.json: Parameter file 
config/Para2_annotation.json: Parameter file


## An example of visualize the knowledge graph
```bash
$ python docket_integration_interface.py \
    Output/  visualization \
    config/Para_visualization.json
```

Parameters description:
Output/ : the output directory
visualization: Label for which process will the integration process do
config/Para_visulization.json: Parameter file

