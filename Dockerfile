FROM jupyter/scipy-notebook:3deefc7d16c7

USER root
RUN mkdir /install
COPY requirements.txt /install

# https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-scipy-notebook
# jupyter/scipy-notebook comes installed with gcc
# pandas, matplotlib, scipy, seaborn, scikit-learn, cython, Click
# uses apt-get to install system packages
# uses conda to install python libraries

RUN apt-get update && apt-get install -y openjdk-8-jdk libjson-perl

USER jovyan

RUN wget -qO- https://get.nextflow.io | bash \
&& cpan install XML::Simple \
&& pip install -r /install/requirements.txt
COPY . /app
WORKDIR /app
