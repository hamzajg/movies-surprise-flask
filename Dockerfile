FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        locales \
        build-essential \
        gfortran \
        libboost-program-options-dev \
        libpq-dev \
        libffi-dev \
        libxrender1 \
        git \
        curl && \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN pip install scikit-surprise

ADD . /app
WORKDIR /app
COPY ./docker-entrypoint.sh /
RUN chmod a+x /docker-entrypoint.sh

# Trains the KNN model at build time so the container starts ready to serve.
RUN python -u ./src/build.py

EXPOSE 12345
