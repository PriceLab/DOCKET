# DOCKET
The Dataset Overview, Comparison and Knowledge Extraction Tool

DOCKET can be built in a Docker container with the following instructions.
Run these commands from the root DOCKET directory that contains the docker-compose.yml

## Build

To build the DOCKET docker image:

```bash
docker-compose build
```

This docker container is built off the jupyter/scipy-notebook base image and installs java 8, nextflow and specific perl and python libraries used by DOCKET

 https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-scipy-notebook

jupyter/scipy-notebook comes installed with gcc, pandas, matplotlib, scipy, seaborn, scikit-learn, cython, Click, uses apt-get to install system packages, uses conda to install python libraries

## Run

To run the DOCKET docker container:

```bash
docker-compose up
```

## Connect

To connect to the DOCKET docker container:

```bash
docker-compose exec docket bash
```


## Nextflow

Connect to the container and run:

```bash
nextflow run docket_study --infile test/dataset1.txt --docket test/ds1_test
```

## Python sample

Connect to the container and run:

```bash
python scripts/hello_docket.py --files test/hello_docket.txt
```

## Tests

Connect to the container and run:

```bash
pip install -r common/tests/requirements.txt
python -m pytest common/tests
```

## Jupyter notebook

Jupyter notebook runs on port 8888.
To see the token, either start the container without the detached flag
or check the logs using:

```bash
docker-compose logs -f docket
```

## Data

Data can be mounted into the Docker container using the volume mount command

Background: https://docs.docker.com/storage/volumes/

As DOCKET builds with docker-compose, here is the file reference:

https://docs.docker.com/compose/compose-file/compose-file-v2/#volume-configuration-reference%23volumes

The short format is SOURCE:TARGET

    SOURCE = /Data/datasets
    TARGET = /datasets

SOURCE is the directory on the host machine

TARGET is the directory inside the Docker container

If this is the configuration you wanted, you would add this line to the docker-compose.yml file:

/Data/datasets:/datasets

An example `docker-compose.yml` 

```yaml
version: "2.1"
services:
  docket:
    build: "."
    image: "docket-dev"
    environment:
      DEBUG: 1
      PYTHONUNBUFFERED: 1
      PYTHONPATH: '/app'
      JUPYTER_ENABLE_LAB: 'yes'
    ports:
      - 8888:8888
    volumes:
      - ./:/app
      - /Data/datasets:/datasets
```
## Password

Generate a hash to safely define your password by executing the following 2 lines in a Jupyter Notebook:

```python
from notebook.auth import passwd
passwd()
```

Use this hash to define the password in the command run when the container is started:

```yaml
version: "2.1"
services:
  docket:
    build: "."
    image: "docket-dev"
    command: start-notebook.sh  --NotebookApp.password='sha1:9316432938f9:93985dffbb854d31308dfe0602a51db947fb7d80'
    environment:
      DEBUG: 1
      PYTHONUNBUFFERED: 1
      PYTHONPATH: '/app'
      JUPYTER_ENABLE_LAB: 'yes'
    ports:
      - 8888:8888
    volumes:
      - ./:/app
```

