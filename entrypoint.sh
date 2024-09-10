# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

#!/bin/bash
# Set JAVA_HOME and PATH explicitly
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
export PATH=$JAVA_HOME/bin:$PATH

# Check if the first argument is a command, if so execute it
if command -v "$1" > /dev/null 2>&1; then
    exec "$@"
else
    # If not a command, run fosslight_source with arguments
    exec fosslight "$@"
fi
