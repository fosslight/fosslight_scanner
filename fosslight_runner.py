import argparse
import os
import subprocess
import json

def run_fosslight(args):
    # Construct the Docker command
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{args.input_path}:/src",
        "-v", f"{args.output_path}:/output"
    ]

    # Add correct_path volume if provided
    if args.correct_path:
        docker_cmd.extend(["-v", f"{args.correct_path}:/correct_path"])

    # Add the Docker image
    docker_cmd.append(args.image)

    # Add FossLight command and arguments
    docker_cmd.append("fosslight")
    docker_cmd.append(args.mode)

    # Add options
    if args.input_path:
        docker_cmd.extend(["-p", "/src"])
    if args.output_path:
        docker_cmd.extend(["-o", "/output"])
    if args.wget:
        docker_cmd.extend(["-w", args.wget])
    if args.format:
        docker_cmd.extend(["-f", args.format])
    if args.num_processes:
        docker_cmd.extend(["-c", str(args.num_processes)])
    if args.keep_raw:
        docker_cmd.append("-r")
    if args.hide_progress:
        docker_cmd.append("-t")
    if args.db_url:
        docker_cmd.extend(["-u", args.db_url])
    if args.dep_args:
        docker_cmd.extend(["-d", args.dep_args])
    if args.no_correction:
        docker_cmd.append("--no_correction")
    if args.correct_path:
        docker_cmd.extend(["--correct_fpath", "/correct_path"])
    if args.version:
        docker_cmd.append("-v")

    # Print the Docker command (for debugging)
    print("Running Docker command:", " ".join(docker_cmd))

    # Run the Docker command
    try:
        subprocess.run(docker_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running FossLight: {e}")
        exit(1)

def load_settings(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Run FossLight in Docker")
    parser.add_argument("mode", choices=["all", "source", "dependency", "binary", "compare"], help="FossLight mode")
    parser.add_argument("-i", "--image", required=True, help="Docker image to use")
    parser.add_argument("-p", "--input_path", help="Path to analyze or compare files")
    parser.add_argument("-w", "--wget", help="Link to be analyzed can be downloaded by wget or git clone")
    parser.add_argument("-o", "--output_path", help="Output directory or file")
    parser.add_argument("-f", "--format", choices=["excel", "yaml", "json", "html"], help="Output format")
    parser.add_argument("-c", "--num_processes", type=int, help="Number of processes to analyze source")
    parser.add_argument("-r", "--keep_raw", action="store_true", help="Keep raw data")
    parser.add_argument("-t", "--hide_progress", action="store_true", help="Hide the progress bar")
    parser.add_argument("-u", "--db_url", help="DB Connection URL")
    parser.add_argument("-d", "--dep_args", help="Additional arguments for dependency analysis")
    parser.add_argument("--no_correction", action="store_true", help="Disable OSS information correction")
    parser.add_argument("--correct_path", help="Path to the sbom-info.yaml file")
    parser.add_argument("-v", "--version", action="store_true", help="Print FOSSLight Scanner version")
    parser.add_argument("-s", "--settings", help="Path to settings JSON file")

    args = parser.parse_args()

    # If settings file is provided, load it and update args
    if args.settings:
        settings = load_settings(args.settings)
        # Update args with settings, but command-line args take precedence
        for key, value in settings.items():
            if not getattr(args, key):
                setattr(args, key, value)

    # Convert relative paths to absolute paths
    if args.input_path:
        args.input_path = os.path.abspath(args.input_path)
    if args.output_path:
        args.output_path = os.path.abspath(args.output_path)
    if args.correct_path:
        args.correct_path = os.path.abspath(args.correct_path)

    run_fosslight(args)

if __name__ == "__main__":
    main()