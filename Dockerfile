# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
FROM python:3.8-slim-buster

COPY . /app
WORKDIR /app

# Install necessary packages including nodejs, npm, and default-jdk
RUN ln -sf /bin/bash /bin/sh && \
  apt-get update && \
  apt-get install --no-install-recommends -y \
  build-essential \
  python3 python3-distutils python3-pip python3-dev python3-magic \
  libxml2-dev \
  libxslt1-dev \
  libhdf5-dev \
  bzip2 xz-utils zlib1g libpopt0 \
  curl \
  default-jdk && \
  curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
  apt-get install -y nodejs && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME dynamically
RUN echo "export JAVA_HOME=\$(dirname \$(dirname \$(readlink -f \$(which java))))" >> /etc/profile && \
    echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> /etc/profile

# Install license-checker globally
RUN npm install -g license-checker

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

# Add /usr/local/bin to the PATH
ENV PATH="/usr/local/bin:${PATH}"

VOLUME /src
WORKDIR /src

# Create and set up the entrypoint script
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'source /etc/profile' >> /entrypoint.sh && \
    echo 'export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))' >> /entrypoint.sh && \
    echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /entrypoint.sh && \
    echo 'if command -v "$1" > /dev/null 2>&1; then' >> /entrypoint.sh && \
    echo '    exec "$@"' >> /entrypoint.sh && \
    echo 'else' >> /entrypoint.sh && \
    echo '    exec fosslight "$@"' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["-h"]

# Clean up the build
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*