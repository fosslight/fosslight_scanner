# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

import sys
import io
import subprocess
import logging
from datetime import datetime
import os


def setup_logging():
    current_time = datetime.now().strftime("%Y%m%d_%H%M")
    log_filename = f'fosslight_log_{current_time}.txt'
    logging.basicConfig(filename=log_filename, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        encoding='utf-8')


def is_double_clicked():
    return sys.argv[0].endswith('.exe') and len(sys.argv) == 1


def check_and_pull_image(image_name):
    try:
        # Check if the image exists locally
        result = subprocess.run(["docker", "image", "inspect", image_name],
                                capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"Image {image_name} already exists locally.")
            return True

        # If the image doesn't exist, pull it
        logging.info(f"Pulling the image {image_name} from Docker Hub")
        subprocess.run(["docker", "pull", image_name], check=True)
        logging.info(f"Successfully pulled the image {image_name}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error with Docker image {image_name}: {e}")
        return False


def get_user_input(auto_image=None):
    if auto_image:
        return auto_image, 'local', os.getcwd()

    print("FossLight Wrapper")
    image = input("Enter Docker image name (e.g., fosslight/fosslight_scanner:latest): ")
    analysis_type = input("Choose analysis type (1 for local path, 2 for Git repository): ")

    if analysis_type == '1':
        input_path = input("Enter local path to analyze: ")
        return image, 'local', input_path
    elif analysis_type == '2':
        git_url = input("Enter Git repository URL to analyze: ")
        return image, 'git', git_url
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)


def display_current_options(options):
    if not options:
        print("Only the default option has been applied.")
    else:
        print("Current additional options:")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")


def get_additional_options():
    options = []
    while True:
        print("\nManage additional options:")
        print("1. Add new option")
        print("2. Remove option")
        print("3. View current options")
        print("4. Finish and proceed")

        choice = input("\nEnter your choice (1-4): ")

        if choice == '1':
            options.extend(add_option())
        elif choice == '2':
            options = remove_option(options)
        elif choice == '3':
            display_current_options(options)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

    return options


def add_option():
    print("\nAvailable additional options:")
    print("1. -f <format>: FOSSLight Report file format (excel, yaml)")
    print("2. -c <number>: Number of processes to analyze source")
    print("3. -r: Keep raw data")
    print("4. -t: Hide the progress bar")
    print("5. -s <path>: Path to apply setting from file")
    print("6. --no_correction: Don't correct OSS information")
    print("7. --correct_fpath <path>: Path to the sbom-info.yaml file")
    print("8. -u <db_url>: DB Connection (for 'all' or 'bin' mode)")
    print("9. -d <dependency_argument>: Additional arguments for dependency analysis")

    choice = input("\nEnter the number of the option you want to add: ")

    if choice == '1':
        format_type = input("Enter format (excel/yaml): ")
        return ['-f', format_type]
    elif choice == '2':
        processes = input("Enter number of processes: ")
        return ['-c', processes]
    elif choice == '3':
        return ['-r']
    elif choice == '4':
        return ['-t']
    elif choice == '5':
        settings_path = input("Enter path to settings file: ")
        return ['-s', settings_path]
    elif choice == '6':
        return ['--no_correction']
    elif choice == '7':
        sbom_path = input("Enter path to sbom-info.yaml: ")
        return ['--correct_fpath', sbom_path]
    elif choice == '8':
        db_url = input("Enter DB URL: ")
        return ['-u', db_url]
    elif choice == '9':
        dep_arg = input("Enter dependency argument: ")
        return ['-d', dep_arg]
    else:
        print("Invalid option. No option added.")
        return []


def remove_option(options):
    if not options:
        print("No options to remove.")
        return options

    display_current_options(options)
    choice = input("Enter the number of the option you want to remove (or 0 to cancel): ")

    try:
        index = int(choice) - 1
        if 0 <= index < len(options):
            removed_option = options.pop(index)
            print(f"Removed option: {removed_option}")
        elif index == -1:
            print("Removal cancelled.")
        else:
            print("Invalid number. No option removed.")
    except ValueError:
        print("Invalid input. No option removed.")

    return options


def remove_wfp_file(output_path):
    wfp_file = os.path.join(output_path, "scanner_output.wfp")
    if os.path.exists(wfp_file):
        try:
            os.remove(wfp_file)
            logging.info(f"Successfully removed WFP file: {wfp_file}")
        except Exception as e:
            logging.error(f"Failed to remove WFP file: {wfp_file}. Error: {e}")


def run_fosslight(image, analysis_type, input_source, output_path, additional_options):
    # Convert Windows paths to Docker-compatible paths
    output_path = output_path.replace('\\', '/').replace('C:', '/c')

    # Construct the Docker command
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{output_path}:/output"
    ]

    if analysis_type == 'local':
        input_path = input_source.replace('\\', '/').replace('C:', '/c')
        docker_cmd.extend(["-v", f"{input_path}:/src"])

    docker_cmd.extend([
        image,
        "fosslight",
        "-o", "/output",
    ])

    if analysis_type == 'local':
        docker_cmd.extend(["-p", "/src"])
    else:  # Git repository
        docker_cmd.extend(["-w", input_source])

    # Add additional options
    docker_cmd.extend(additional_options)

    # Log the Docker command
    logging.info(f"Running Docker command: {' '.join(docker_cmd)}")

    # Run the Docker command with real-time output and UTF-8 encoding
    try:
        process = subprocess.Popen(docker_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   bufsize=1, universal_newlines=True, encoding='utf-8')
        for line in process.stdout:
            line = line.strip()
            if line:  # Only log non-empty lines
                print(line)  # Print to console in real-time
                sys.stdout.flush()  # Ensure real-time output
                logging.info(line)  # Log to file
        process.wait()
        if process.returncode != 0:
            logging.error(f"FossLight exited with error code {process.returncode}")
        else:
            logging.info("FossLight completed successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running FossLight: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    remove_wfp_file(output_path)


def get_execution_mode():
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        return "manual"
    return "auto"


def main():
    # Redirect stdout to use utf-8 encoding without buffering
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

    setup_logging()

    execution_mode = get_execution_mode()

    if execution_mode == "auto":
        logging.info("Executing in automatic mode (double-click)")
        image_name = "fosslight/fosslight_scanner:latest"
        if not check_and_pull_image(image_name):
            print(f"Failed to ensure the presence of the Docker image: {image_name}")
            input("Press Enter to exit...")
            sys.exit(1)

        current_dir = os.getcwd()
        image, analysis_type, input_source = image_name, 'local', current_dir
        output_path = current_dir
        additional_options = ["-f", "excel"]
    else:
        logging.info("Executing in manual mode (command prompt)")
        image, analysis_type, input_source = get_user_input()
        output_path = input("Enter path for output: ")
        additional_options = get_additional_options()

    # Ensure no duplicate options
    additional_options = list(dict.fromkeys(additional_options))

    logging.info("Starting FossLight wrapper")
    logging.info(f"Docker image: {image}")
    logging.info(f"Analysis type: {analysis_type}")
    logging.info(f"Input source: {input_source}")
    logging.info(f"Output path: {output_path}")
    logging.info(f"Additional options: {' '.join(additional_options)}")

    run_fosslight(image, analysis_type, input_source, output_path, additional_options)

    print("\nFossLight wrapper completed. Press Enter to exit.")
    input()


if __name__ == "__main__":
    main()