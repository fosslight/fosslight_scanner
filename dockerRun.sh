# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

#!/bin/bash
# run_fosslight.sh

# Function to convert relative path to absolute path
to_absolute_path() {
    local path="$1"
    if [[ "$path" != /* ]]; then
        path="$PWD/$path"
    fi
    echo "$path"
}

# Function to print usage
print_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -i <image>    Docker image to use (required)"
    echo "  -m <mode>     FossLight mode (all, source, dependency, binary, compare)"
    echo "  -p <path>     Path to analyze or compare files"
    echo "  -w <link>     Link to be analyzed"
    echo "  -f <format>   Output format (excel, yaml, json, html)"
    echo "  -o <output>   Output directory or file (optional, defaults to -p path if not provided)"
    echo "  -c <number>   Number of processes to analyze source"
    echo "  -r            Keep raw data"
    echo "  -t            Hide the progress bar"
    echo "  -u <db_url>   DB Connection URL"
    echo "  -d <args>     Additional arguments for dependency analysis"
    echo "  --no_correction             Disable OSS information correction"
    echo "  --correct_fpath <path>      Path to the sbom-info.yaml file"
    echo "  -h            Show this help message"
}

# Parse command line arguments
DOCKER_IMAGE=""
FOSSLIGHT_ARGS=""
INPUT_PATH=""
OUTPUT_PATH=""

while getopts ":i:m:p:w:f:o:c:rtu:d:-:h" opt; do
  case ${opt} in
    i )
      DOCKER_IMAGE=$OPTARG
      ;;
    m )
      FOSSLIGHT_ARGS="$FOSSLIGHT_ARGS $OPTARG"
      ;;
    p )
      if [[ "$OPTARG" == *" "* ]]; then
        # If the argument contains a space, it's likely two file paths for compare mode
        IFS=' ' read -ra PATHS <<< "$OPTARG"
        INPUT_PATH=$(to_absolute_path "${PATHS[0]}")
        FOSSLIGHT_ARGS="$FOSSLIGHT_ARGS -p /src1 /src2"
      else
        INPUT_PATH=$(to_absolute_path "$OPTARG")
        FOSSLIGHT_ARGS="$FOSSLIGHT_ARGS -p /src"
      fi
      ;;
    o )
      OUTPUT_PATH=$(to_absolute_path "$OPTARG")
      FOSSLIGHT_ARGS="$FOSSLIGHT_ARGS -o /output"
      ;;
    w )
      FOSSLIGHT_ARGS="$FOSSLIGHT_ARGS -w $OPTARG"
      ;;
    f | c | u | d )
      FOSSLIGHT_ARGS="$FOSSLIGHT_ARGS -$opt $OPTARG"
      ;;
    r | t )
      FOSSLIGHT_ARGS="$FOSSLIGHT_ARGS -$opt"
      ;;
    - )
      case "${OPTARG}" in
        no_correction )
          FOSSLIGHT_ARGS="$FOSSLIGHT_ARGS --no_correction"
          ;;
        correct_fpath )
          CORRECT_PATH=$(to_absolute_path "${!OPTIND}")
          FOSSLIGHT_ARGS="$FOSSLIGHT_ARGS --correct_fpath /correct_path"
          OPTIND=$((OPTIND + 1))
          ;;
        * )
          echo "Invalid option: --$OPTARG" >&2
          print_usage
          exit 1
          ;;
      esac
      ;;
    h )
      print_usage
      exit 0
      ;;
    \? )
      echo "Invalid option: $OPTARG" 1>&2
      print_usage
      exit 1
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      print_usage
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

# Check if Docker image is provided
if [ -z "$DOCKER_IMAGE" ]; then
    echo "Error: Docker image (-i) is required."
    print_usage
    exit 1
fi

# If OUTPUT_PATH is not set, use INPUT_PATH
if [ -z "$OUTPUT_PATH" ]; then
    OUTPUT_PATH="$INPUT_PATH"
fi

# Prepare volume mounts
VOLUME_MOUNTS=""
if [ -n "$INPUT_PATH" ]; then
    if [[ "$FOSSLIGHT_ARGS" == *"-p /src1 /src2"* ]]; then
        # For compare mode
        VOLUME_MOUNTS="-v ${PATHS[0]}:/src1 -v ${PATHS[1]}:/src2"
    else
        VOLUME_MOUNTS="-v $INPUT_PATH:/src"
    fi
fi

if [ -n "$OUTPUT_PATH" ]; then
    VOLUME_MOUNTS="$VOLUME_MOUNTS -v $OUTPUT_PATH:/output"
fi

if [ -n "$CORRECT_PATH" ]; then
    VOLUME_MOUNTS="$VOLUME_MOUNTS -v $CORRECT_PATH:/correct_path"
fi

# Run Docker command
docker run --rm $VOLUME_MOUNTS $DOCKER_IMAGE fosslight $FOSSLIGHT_ARGS

echo "FossLight command completed. Results saved to: $OUTPUT_PATH"