#!/bin/bash

# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

# Set JAVA_HOME dynamically
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
export PATH=$JAVA_HOME/bin:$PATH

# Check if the first argument is a command, if so execute it
if command -v "$1" > /dev/null 2>&1; then
    exec "$@"
else
    # If not a command, run fosslight with arguments
    exec fosslight "$@"
fi