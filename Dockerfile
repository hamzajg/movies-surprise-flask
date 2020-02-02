FROM python:3.6-slim-buster

RUN DEBIAN_FRONTEND=noninteractive apt-get update -y --no-install-recommends && \
  apt-get install -y --no-install-recommends locales && \
  locale-gen en_US.UTF-8 && \
  apt-get install -y --no-install-recommends software-properties-common && \
  apt-get install -y --no-install-recommends \
        make \
        automake \
        libpq-dev \
        libffi-dev \
        gfortran \
        g++ \
        git \
        libboost-program-options-dev \
        libtool \
        libxrender1 \
        wget \
        ca-certificates \
        curl && \
  apt-get clean -y && \
  rm -rf /var/lib/apt/lists/*
#ENV PYTHONUNBUFFERED=0
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN pip install scikit-surprise
ADD . /app
WORKDIR /app
COPY ./docker-entrypoint.sh /
RUN chmod a+x /docker-entrypoint.sh

#RUN adduser -D user
#RUN adduser --disabled-password user
#USER user
RUN python -u ./src/build.py
EXPOSE 12345


# ENTRYPOINT ["/docker-entrypoint.sh"]
