FROM python:3.7-alpine3.11 as base

FROM base as builder
USER root
RUN mkdir /install
RUN mkdir -p /install/lib/python3.7/site-packages
WORKDIR /install
ENV PYTHONPATH "${PYTHONPATH}:/install/lib/python3.7/site-packages"

COPY requirements.txt /install/requirements.txt

# numpy requires Cython which requires gcc
RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
&& pip install --target="/install" -r /install/requirements.txt \
&& apk del .build-deps

FROM base
COPY --from=builder /install /usr/local

COPY . /app
WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/usr/local/:/app"

RUN apk add --no-cache openjdk8 bash git perl perl-json \
&& pip install --upgrade  setuptools \
&& pip install -r local_requirements.txt \
&& wget -qO- https://get.nextflow.io | bash

