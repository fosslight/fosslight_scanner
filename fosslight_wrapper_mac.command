#!/bin/bash

# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

# FossLight Wrapper Shell Script

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default values
IMAGE="fosslight/fosslight_scanner:latest"
OUTPUT_DIR="$SCRIPT_DIR/fosslight_output"
MANUAL_MODE=false

# Function to check if running in terminal
is_running_in_terminal() {
    [ -t 0 ]
}

# Function to pause execution (for GUI mode)
pause() {
    if ! is_running_in_terminal; then
        echo "Press Enter to exit..."
        read
    fi
}

# Function to check and pull Docker image
check_and_pull_image() {
    if ! docker image inspect "$IMAGE" &> /dev/null; then
        echo "Pulling image $IMAGE..."
        if ! docker pull "$IMAGE"; then
            echo "Failed to pull image $IMAGE"
            exit 1
        fi
    fi
}

# Function to get user input in manual mode
get_user_input() {
    echo "FossLight Wrapper (Manual Mode)"
    read -p "Choose analysis type (1 for local path, 2 for Git repository): " analysis_type
    if [ "$analysis_type" == "1" ]; then
        read -p "Enter local path to analyze: " input_source
        analysis_type="local"
    elif [ "$analysis_type" == "2" ]; then
        read -p "Enter Git repository URL to analyze: " input_source
        analysis_type="git"
    else
        echo "Invalid choice. Exiting."
        exit 1
    fi
    read -p "Enter path for output (default: $OUTPUT_DIR): " user_output
    OUTPUT_DIR=${user_output:-$OUTPUT_DIR}
}

# Function to run FossLight
run_fosslight() {
    local docker_cmd="docker run --rm"
    
    if [ "$analysis_type" == "local" ]; then
        docker_cmd="$docker_cmd -v $input_source:/src -v $OUTPUT_DIR:/output"
        docker_cmd="$docker_cmd $IMAGE fosslight -p /src -o /output -f excel"
    else
        docker_cmd="$docker_cmd -v $OUTPUT_DIR:/output"
        docker_cmd="$docker_cmd $IMAGE fosslight -o /output -w $input_source -f excel"
    fi

    echo "Running FossLight..."
    if ! eval $docker_cmd; then
        echo "Error running FossLight"
        exit 1
    fi
}

# Main execution
if [ "$1" == "--manual" ]; then
    MANUAL_MODE=true
fi

if [ "$MANUAL_MODE" = true ]; then
    get_user_input
else
    echo "FossLight Wrapper (Automatic Mode)"
    analysis_type="local"
    input_source="$SCRIPT_DIR"
    echo "Analyzing directory: $input_source"
fi

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check and pull Docker image
check_and_pull_image

# Run FossLight
run_fosslight

echo "FossLight analysis completed. Results are in $OUTPUT_DIR"
pause