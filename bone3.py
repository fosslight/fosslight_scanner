from datetime import datetime
import os
import subprocess
import logging
import sys

def setup_logging():
    current_time = datetime.now().strftime("%Y%m%d_%H%M")
    log_filename = f'fosslight_log_{current_time}.txt'

    logging.basicConfig(filename=log_filename, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def get_user_input():
    print("FossLight Wrapper")
    image = input("Enter Docker image name (e.g., fosslight/fosslight): ")
    
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

def run_fosslight(image, analysis_type, input_source, output_path):
    # Convert Windows paths to Docker-compatible paths
    output_path = output_path.replace('\\', '/').replace('C:', '/c')

    # Construct the Docker command
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{output_path}:/output",
        image,
        "fosslight",
        "all",
        "-o", "/output"
    ]

    if analysis_type == 'local':
        input_path = input_source.replace('\\', '/').replace('C:', '/c')
        docker_cmd.extend(["-v", f"{input_path}:/src", "-p", "/src"])
    else:  # Git repository
        docker_cmd.extend(["-w", input_source])

    # Log the Docker command
    logging.info(f"Running Docker command: {' '.join(docker_cmd)}")

    # Run the Docker command
    try:
        process = subprocess.Popen(docker_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            line = line.strip()
            if line:  # Only log non-empty lines
                print(line)  # Print to console in real-time
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

def main():
    setup_logging()

    image, analysis_type, input_source = get_user_input()
    output_path = input("Enter path for output: ")

    logging.info("Starting FossLight wrapper")
    logging.info(f"Docker image: {image}")
    logging.info(f"Analysis type: {analysis_type}")
    logging.info(f"Input source: {input_source}")
    logging.info(f"Output path: {output_path}")

    run_fosslight(image, analysis_type, input_source, output_path)

    print("\nFossLight wrapper completed. Press Enter to exit.")
    input()

if __name__ == "__main__":
    main()