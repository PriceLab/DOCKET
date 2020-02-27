FROM jupyter/scipy-notebook:3deefc7d16c7

USER root
RUN mkdir /install
COPY requirements.txt /install

# https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-scipy-notebook
# jupyter/scipy-notebook comes installed with gcc
# pandas, matplotlib, scipy, seaborn, scikit-learn, cython, Click
# uses apt-get to install system packages
# uses conda to install python libraries

# subversion is needed for the svn to only download Perl data-fingerprints bin
# Perl data-fingerprints has hardcoded the location of env so softlink it
RUN apt-get update && apt-get install -y openjdk-8-jdk \
  libjson-perl subversion \
  && ln -s /usr/bin/env /bin/env

USER jovyan

RUN wget -qO- https://get.nextflow.io | bash \
&& pip install -r /install/requirements.txt

# set perl environment variables
ENV PERL_PATH=/home/jovyan/data-fingerprints
ENV PERL5LIB=/app/data-fingerprints:$PERL_PATH:$PERL_PATH/lib/perl5:$PERL_PATH:$PERL5LIB
ENV PATH="$PERL_PATH:$PATH"

# Commented out because the directory has been committed as data-fingeprints
# Download only the Perl bin directory from gglusman/data-fingerprints to /home/jovyan
#RUN svn export https://github.com/gglusman/data-fingerprints.git/trunk/bin

COPY . /app
WORKDIR /app
