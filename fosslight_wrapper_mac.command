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
ADDITIONAL_OPTIONS=()

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

# Function to display current additional options
display_current_options() {
    if [ ${#ADDITIONAL_OPTIONS[@]} -eq 0 ]; then
        echo "No additional options set."
    else
        echo "Current additional options:"
        for i in "${!ADDITIONAL_OPTIONS[@]}"; do
            echo "$((i+1)). ${ADDITIONAL_OPTIONS[i]}"
        done
    fi
}

# Function to add an option
add_option() {
    echo "Available additional options:"
    echo "1. -f <format>: FOSSLight Report file format (excel, yaml)"
    echo "2. -c <number>: Number of processes to analyze source"
    echo "3. -r: Keep raw data"
    echo "4. -t: Hide the progress bar"
    echo "5. -s <path>: Path to apply setting from file"
    echo "6. --no_correction: Don't correct OSS information"
    echo "7. --correct_fpath <path>: Path to the sbom-info.yaml file"
    echo "8. -u <db_url>: DB Connection (for 'all' or 'bin' mode)"
    echo "9. -d <dependency_argument>: Additional arguments for dependency analysis"

    read -p "Enter the number of the option you want to add: " choice

    case $choice in
        1) 
            read -p "Enter format (excel/yaml): " format
            ADDITIONAL_OPTIONS+=("-f" "$format")
            ;;
        2)
            read -p "Enter number of processes: " processes
            ADDITIONAL_OPTIONS+=("-c" "$processes")
            ;;
        3) ADDITIONAL_OPTIONS+=("-r") ;;
        4) ADDITIONAL_OPTIONS+=("-t") ;;
        5)
            read -p "Enter path to settings file: " settings_path
            ADDITIONAL_OPTIONS+=("-s" "$settings_path")
            ;;
        6) ADDITIONAL_OPTIONS+=("--no_correction") ;;
        7)
            read -p "Enter path to sbom-info.yaml: " sbom_path
            ADDITIONAL_OPTIONS+=("--correct_fpath" "$sbom_path")
            ;;
        8)
            read -p "Enter DB URL: " db_url
            ADDITIONAL_OPTIONS+=("-u" "$db_url")
            ;;
        9)
            read -p "Enter dependency argument: " dep_arg
            ADDITIONAL_OPTIONS+=("-d" "$dep_arg")
            ;;
        *) echo "Invalid option. No option added." ;;
    esac
}

# Function to remove an option
remove_option() {
    if [ ${#ADDITIONAL_OPTIONS[@]} -eq 0 ]; then
        echo "No options to remove."
        return
    fi

    display_current_options
    read -p "Enter the number of the option you want to remove (or 0 to cancel): " choice

    if [ "$choice" -ge 1 ] && [ "$choice" -le "${#ADDITIONAL_OPTIONS[@]}" ]; then
        unset 'ADDITIONAL_OPTIONS[choice-1]'
        ADDITIONAL_OPTIONS=("${ADDITIONAL_OPTIONS[@]}")
        echo "Option removed."
    elif [ "$choice" -eq 0 ]; then
        echo "Removal cancelled."
    else
        echo "Invalid number. No option removed."
    fi
}

# Function to manage additional options
manage_additional_options() {
    while true; do
        echo -e "\nManage additional options:"
        echo "1. Add new option"
        echo "2. Remove option"
        echo "3. View current options"
        echo "4. Finish and proceed"

        read -p "Enter your choice (1-4): " choice

        case $choice in
            1) add_option ;;
            2) remove_option ;;
            3) display_current_options ;;
            4) break ;;
            *) echo "Invalid choice. Please try again." ;;
        esac
    done
}

# Function to run FossLight
run_fosslight() {
    local docker_cmd="docker run --rm"
    
    if [ "$analysis_type" == "local" ]; then
        docker_cmd="$docker_cmd -v $input_source:/src -v $OUTPUT_DIR:/output"
        docker_cmd="$docker_cmd $IMAGE fosslight -p /src -o /output"
    else
        docker_cmd="$docker_cmd -v $OUTPUT_DIR:/output"
        docker_cmd="$docker_cmd $IMAGE fosslight -o /output -w $input_source"
    fi

    # Add additional options
    for option in "${ADDITIONAL_OPTIONS[@]}"; do
        docker_cmd="$docker_cmd $option"
    done

    echo "Running FossLight..."
    echo "Command: $docker_cmd"
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
    manage_additional_options
else
    echo "FossLight Wrapper (Automatic Mode)"
    analysis_type="local"
    input_source="$SCRIPT_DIR"
    echo "Analyzing directory: $input_source"
    ADDITIONAL_OPTIONS=("-f" "excel")
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