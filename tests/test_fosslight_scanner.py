from fosslight_scanner.fosslight_scanner import run_scanner, download_source, init, run_main, run_dependency
from fosslight_util.oss_item import ScannerItem


def test_run_dependency(tmp_path):
    # given
    path_to_analyze = tmp_path / "test_project"
    output_file_with_path = tmp_path / "output_file"
    params = "-m 'npm' -a 'activate_cmd' -d 'deactivate_cmd' -c 'custom_dir' -n 'app_name' -t 'token_value'"
    path_to_exclude = ["node_modules"]

    # Create the directory to analyze
    path_to_analyze.mkdir(parents=True, exist_ok=True)

    # when
    result = run_dependency(str(path_to_analyze), str(output_file_with_path), params, path_to_exclude)

    # then
    # Check that result is an instance of ScannerItem
    assert isinstance(result, ScannerItem), "Result should be an instance of ScannerItem."

    # Check that result is not None
    assert result is not None, "Result should not be None."


def test_run_scanner(tmp_path):
    # given
    src_path = tmp_path / "test_src"
    output_path = tmp_path / "output"
    dep_arguments = ""
    output_file = ['test_output']
    output_extension = [".yaml"]

    # Create necessary directories and files for the test
    src_path.mkdir(parents=True, exist_ok=True)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create a dummy source file in `src_path` to be scanned
    test_file = src_path / "test_file.py"
    test_file.write_text("# This is a test file\nprint('Hello, World!')")

    # when
    run_scanner(
        src_path=str(src_path),
        dep_arguments=dep_arguments,
        output_path=str(output_path),
        keep_raw_data=True,
        run_src=True,
        run_bin=False,
        run_dep=False,
        run_prechecker=False,
        remove_src_data=False,
        result_log={},
        output_files=output_file,
        output_extensions=output_extension,
        num_cores=1,
        path_to_exclude=[]
    )

    # then
    # Check if `src_path` and `output_path` still exist
    assert src_path.is_dir(), "Source path should still exist."
    assert output_path.is_dir(), "Output path should still exist."


def test_download_source(tmp_path):
    # given
    link = "https://example.com/test_repo.git"
    out_dir = tmp_path / "output"

    # Create the necessary output directory
    out_dir.mkdir(parents=True, exist_ok=True)

    # when
    success, temp_src_dir, oss_name, oss_version = download_source(str(link), str(out_dir))

    # then
    # Ensure the function completes successfully
    assert isinstance(success, bool), "Function should return a boolean for success."

    # If the function fails, ensure temp_src_dir is empty
    if not success:
        assert temp_src_dir == "", "temp_src_dir should be an empty string if download fails."
    else:
        # If the function succeeds, check temp_src_dir is a valid path
        assert isinstance(temp_src_dir, str), "Temporary source directory should be a string."
        assert str(temp_src_dir).startswith(str(out_dir)), "Temporary source directory should be within the output directory."

    # Ensure oss_name and oss_version are strings
    assert isinstance(oss_name, str), "OSS name should be a string."
    assert isinstance(oss_version, str), "OSS version should be a string."


def test_init(tmp_path):
    # given
    output_path = tmp_path / "output"

    # Initialize global variables if necessary
    global _output_dir, _log_file
    _output_dir = "test_output"  # Set to a default or test-specific value
    _log_file = "test_log"       # Set the name of the log file

    # when
    dir_created, output_root_dir, result_log = init(str(output_path))

    # then
    # Ensure that the output directory was created
    assert dir_created is True, "The output directory should be created."

    # Check if the output_root_dir is correct
    assert output_root_dir == str(output_path), "Output root directory should match the given path."

    # Check that the result_log is not None and is a dictionary
    assert result_log is not None, "Result log should not be None."
    assert isinstance(result_log, dict), "Result log should be a dictionary."


def test_run_main(tmp_path):
    # given
    mode_list = ["source"]
    path_arg = [str(tmp_path / "test_src")]
    dep_arguments = []
    output_file_or_dir = str(tmp_path / "output")
    file_format = ['yaml']
    url_to_analyze = ""
    db_url = ""

    # Create necessary directories and files for the test
    (tmp_path / "test_src").mkdir(parents=True, exist_ok=True)

    # when
    result = run_main(
        mode_list=mode_list,
        path_arg=path_arg,
        dep_arguments=dep_arguments,
        output_file_or_dir=output_file_or_dir,
        file_format=file_format,
        url_to_analyze=url_to_analyze,
        db_url=db_url,
        hide_progressbar=True,  # Disable progress bar for testing
        keep_raw_data=True,     # Keep raw data to avoid cleanup during test
        num_cores=1,
        correct_mode=True,
        correct_fpath="",
        ui_mode=False,
        path_to_exclude=[]
    )

    # then
    assert result is True
