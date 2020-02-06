# DOCKET
The Dataset Overview, Comparison and Knowledge Extraction Tool

## Build

To build the DOCKET docker image:

docker-compose build

This docker container is built off the jupyter/scipy-notebook
base image and installs java 8, nextflow and specific perl
and python libraries used by DOCKET

 https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-scipy-notebook

jupyter/scipy-notebook comes installed with gcc
 pandas, matplotlib, scipy, seaborn, scikit-learn, cython, Click
 uses apt-get to install system packages
 uses conda to install python libraries

## Run

To run the DOCKET docker container:

docker-compose up

## Connect

To connect to the DOCKET docker container:

docker-compose exec docket bash

## Jupyter notebook

Jupyter notebook runs on port 8888.
To see the token, either start the container without the detached flag
or check the logs using:

  docker-compose logs -f docket
