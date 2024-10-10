# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
FROM python:3.10-slim-buster

COPY . /app
WORKDIR	/app

RUN	ln -sf /bin/bash /bin/sh && \
  apt-get update && \
  apt-get install --no-install-recommends -y  \
  build-essential \
  python3 python3-distutils python3-pip python3-dev python3-magic \
  libxml2-dev \
  libxslt1-dev \
  libhdf5-dev \
  bzip2 xz-utils zlib1g libpopt0 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip && \
  pip3 install . || true && \
  pip3 install dparse && \
  rm -rf ~/.cache/pip /root/.cache/pipe

ENTRYPOINT ["/usr/local/bin/fosslight"]
