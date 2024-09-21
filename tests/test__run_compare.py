import pytest
from fosslight_scanner._run_compare import *

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

    output_file = tmp_path / "result.txt"
    assert write_result_json_yaml(output_file, compared_result, ".txt") == False


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
    assert write_compared_result(output_file, compared_result, XLSX_EXT) == (True, str(output_file) + XLSX_EXT)
    assert write_compared_result(output_file, compared_result, HTML_EXT) == (True, str(output_file) + XLSX_EXT + ", " + str(output_file) + HTML_EXT)
    assert write_compared_result(output_file, compared_result, JSON_EXT) == (True, str(output_file) + JSON_EXT)
    assert write_compared_result(output_file, compared_result, YAML_EXT) == (True, str(output_file) + YAML_EXT)
    assert write_compared_result(output_file, compared_result, ".txt") == (False, str(output_file))


def test_get_comparison_result_filename():
    assert get_comparison_result_filename("/path", "file", XLSX_EXT, "time") == "/path/file.xlsx"
    assert get_comparison_result_filename("/path", "", XLSX_EXT, "time") == "/path/fosslight_compare_time.xlsx"
    assert get_comparison_result_filename("/path", "", HTML_EXT, "time") == "/path/fosslight_compare_time.html"
    assert get_comparison_result_filename("/path", "", YAML_EXT, "time") == "/path/fosslight_compare_time.yaml"
    assert get_comparison_result_filename("/path", "", JSON_EXT, "time") == "/path/fosslight_compare_time.json"


def test_count_compared_result(caplog):
    compared_result = {ADD: [], DELETE: [], CHANGE: []}
    count_compared_result(compared_result)
    assert "all oss lists are the same." in caplog.text

    compared_result = {ADD: [{"name": "test"}], DELETE: [], CHANGE: []}
    count_compared_result(compared_result)
    assert "total 1 oss updated (add: 1, delete: 0, change: 0)" in caplog.text


def test_run_compare(tmp_path, mocker):
    before_f = tmp_path / "before.yaml"
    after_f = tmp_path / "after.yaml"
    output_path = tmp_path
    output_file = "result"
    file_ext = YAML_EXT
    _start_time = "time"
    _output_dir = tmp_path

    mocker.patch("fosslight_util.convert_excel_to_yaml")
    mocker.patch("fosslight_util.compare_yaml", return_value={ADD: [], DELETE: [], CHANGE: []})
    mocker.patch("fosslight_scanner._run_compare.write_compared_result", return_value=(True, str(output_file)))

    assert run_compare(before_f, after_f, output_path, output_file, file_ext, _start_time, _output_dir) == True