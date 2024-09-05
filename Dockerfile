# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
FROM python:3.8-slim-buster

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
    pip3 install fosslight_util && \  
    pip3 install python-magic && \  
    pip3 install dparse  

RUN pip3 install fosslight_source --no-deps && \  
    pip3 show fosslight_source | grep "Requires:" | sed 's/Requires://' | tr ',' '\n' | grep -v "typecode-libmagic" > /tmp/fosslight_source_deps.txt && \  
    pip3 install -r /tmp/fosslight_source_deps.txt && \  
    rm /tmp/fosslight_source_deps.txt

COPY requirements.txt /tmp/requirements.txt
RUN grep -vE "fosslight[-_]source" /tmp/requirements.txt > /tmp/custom_requirements.txt && \
    pip3 install -r /tmp/custom_requirements.txt && \
    rm /tmp/requirements.txt /tmp/custom_requirements.txt

COPY . /fosslight_scanner
WORKDIR /fosslight_scanner
RUN pip3 install . --no-deps && \
    rm -rf ~/.cache/pip /root/.cache/pip

ENV PATH="/usr/local/bin:${PATH}"  

VOLUME /src  
WORKDIR /src  

RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if command -v "$1" > /dev/null 2>&1; then' >> /entrypoint.sh && \
    echo '    exec "$@"' >> /entrypoint.sh && \
    echo 'else' >> /entrypoint.sh && \
    echo '    exec fosslight_source "$@"' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["-h"]
