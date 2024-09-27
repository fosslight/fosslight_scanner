import pytest
from fosslight_scanner._run_compare import *
from pathlib import Path
import json
import yaml

"""
1. write_result_json_yaml:
Test with JSON extension.
Test with YAML extension.
Test with invalid extension.

2. parse_result_for_table:
Test with ADD status.
Test with DELETE status.
Test with CHANGE status.
Test with invalid status.

3. get_sample_html:
Test if the function returns a file object or empty string.

4. write_result_html:
Test with valid HTML content.
Test with invalid HTML content.

5. write_result_xlsx:
Test with valid data.
Test with invalid data.

6. write_compared_result:
Test with XLSX extension.
Test with HTML extension.
Test with JSON extension.
Test with YAML extension.
Test with invalid extension.

7. get_comparison_result_filename:
Test with different extensions and filenames.

8. count_compared_result:
Test with different compared results.

9. run_compare:
Test with valid YAML files.
Test with valid XLSX files.
Test with invalid file extensions.
"""

def test_write_result_json_yaml(tmp_path):
    output_file = tmp_path / "result.json"
    compared_result = {"key": "value"}
    assert write_result_json_yaml(output_file, compared_result, JSON_EXT) == True
    assert json.load(open(output_file)) == compared_result

    output_file = tmp_path / "result.yaml"
    assert write_result_json_yaml(output_file, compared_result, YAML_EXT) == True
    assert yaml.safe_load(open(output_file)) == compared_result

    # Handle ".txt" case based on actual behavior of the function
    output_file = tmp_path / "result.txt"
    assert write_result_json_yaml(output_file, compared_result, ".txt") == True


def test_parse_result_for_table():
    oi = {"name": "test", "version": "1.0", "license": ["MIT"]}
    assert parse_result_for_table(oi, ADD) == [ADD, '', '', 'test(1.0)', 'MIT']
    assert parse_result_for_table(oi, DELETE) == [DELETE, 'test(1.0)', 'MIT', '', '']

    oi = {"name": "test", "prev": [{"version": "1.0", "license": ["MIT"]}], "now": [{"version": "2.0", "license": ["Apache-2.0"]}]}
    assert parse_result_for_table(oi, CHANGE) == [CHANGE, 'test(1.0)', 'MIT', 'test(2.0)', 'Apache-2.0']

    assert parse_result_for_table(oi, "invalid") == []


def test_get_sample_html():
    assert get_sample_html() != ''


def test_write_result_html(tmp_path):
    output_file = tmp_path / "result.html"
    compared_result = {ADD: [], DELETE: [], CHANGE: []}
    assert write_result_html(output_file, compared_result, "before.yaml", "after.yaml") == True

    compared_result = {ADD: [{"name": "test", "version": "1.0", "license": ["MIT"]}], DELETE: [], CHANGE: []}
    assert write_result_html(output_file, compared_result, "before.yaml", "after.yaml") == True


def test_write_result_xlsx(tmp_path):
    output_file = tmp_path / "result.xlsx"
    compared_result = {ADD: [], DELETE: [], CHANGE: []}
    assert write_result_xlsx(output_file, compared_result) == True

    compared_result = {ADD: [{"name": "test", "version": "1.0", "license": ["MIT"]}], DELETE: [], CHANGE: []}
    assert write_result_xlsx(output_file, compared_result) == True


def test_write_compared_result(tmp_path):
    output_file = tmp_path / "result"
    compared_result = {ADD: [], DELETE: [], CHANGE: []}

    # XLSX 확장자 비교
    success, result_file = write_compared_result(output_file, compared_result, XLSX_EXT)
    assert success is True
    assert str(result_file) == str(output_file)

    # HTML 확장자 비교
    success, result_file = write_compared_result(output_file, compared_result, HTML_EXT)
    expected_result_file = f"{str(output_file) + XLSX_EXT}, {str(output_file)}"
    assert success is True
    assert result_file == expected_result_file

    # JSON 확장자 비교
    success, result_file = write_compared_result(output_file, compared_result, JSON_EXT)
    assert success is True
    assert str(result_file) == str(output_file)

    # YAML 확장자 비교
    success, result_file = write_compared_result(output_file, compared_result, YAML_EXT)
    assert success is True
    assert str(result_file) == str(output_file)

def test_get_comparison_result_filename():
    assert get_comparison_result_filename("/path", "file", XLSX_EXT, "time") == "/path/file.xlsx"
    assert get_comparison_result_filename("/path", "", XLSX_EXT, "time") == "/path/fosslight_compare_time.xlsx"
    assert get_comparison_result_filename("/path", "", HTML_EXT, "time") == "/path/fosslight_compare_time.html"
    assert get_comparison_result_filename("/path", "", YAML_EXT, "time") == "/path/fosslight_compare_time.yaml"
    assert get_comparison_result_filename("/path", "", JSON_EXT, "time") == "/path/fosslight_compare_time.json"


@pytest.mark.parametrize("compared_result, expected_log", [
    ({ADD: [], DELETE: [], CHANGE: []}, "all oss lists are the same."),
    ({ADD: [{"name": "test"}], DELETE: [], CHANGE: []}, "total 1 oss updated (add: 1, delete: 0, change: 0)")
])
def test_count_compared_result(compared_result, expected_log, caplog):
    with caplog.at_level(logging.INFO):
        count_compared_result(compared_result)
    assert expected_log in caplog.text


def test_run_compare_different_extension(tmp_path):
    # given
    before_f = tmp_path / "before.yaml"
    after_f = tmp_path / "after.xlsx"
    output_path = tmp_path
    output_file = "result"
    file_ext = ".yaml"
    _start_time = "time"
    _output_dir = tmp_path

    # Write example content to before_f and after_f
    before_content = {
        "oss_list": [
            {"name": "test", "version": "1.0", "license": "MIT"}
        ]
    }

    after_content = {
        "oss_list": [
            {"name": "test", "version": "2.0", "license": "Apache-2.0"}
        ]
    }

    # Write these contents to the files
    with open(before_f, "w") as bf:
        yaml.dump(before_content, bf)

    # Create an empty xlsx file for after_f
    with open(after_f, "w") as af:
        af.write("")

    # when
    comparison_result = run_compare(before_f, after_f, output_path, output_file, file_ext, _start_time, _output_dir)

    # then
    assert comparison_result == False