import os
import pytest
import pandas as pd
from fosslight_util.oss_item import OssItem
from fosslight_scanner.common import copy_file, run_analysis, call_analysis_api, check_exclude_dir


def test_copy_file_success(tmp_path):
    # given
    source = tmp_path / "source.txt"
    destination = tmp_path / "destination"
    source.write_text("Test content")

    # when
    success, copied_file = copy_file(str(source), str(destination))

    # then
    assert success is True
    assert os.path.exists(copied_file)


def test_copy_file_failure():
    # given
    source = "/nonexistent/path/source.txt"
    destination = "/destination/path"

    # when
    success, _ = copy_file(source, destination)

    # then
    assert success is False


@pytest.mark.parametrize("path_to_run, expected_result", [
    ("/test/path", "Mocked result"),
    ("", "")
])
def test_run_analysis(monkeypatch, path_to_run, expected_result):
    # given
    params = ["--param1", "value1"]
    output = "/output/path"
    exe_path = "/exe/path"

    def mock_func():
        return expected_result

    # Mock os.chdir to prevent changing directories during test
    monkeypatch.setattr(os, 'chdir', lambda x: None)
    # Mock os.getcwd to return a default path
    monkeypatch.setattr(os, 'getcwd', lambda: "/mocked/path")

    # when
    result = run_analysis(path_to_run, params, mock_func, "Test Run", output, exe_path)

    # then
    assert result == expected_result


def test_call_analysis_api_with_path():
    # given
    path_to_run = "/test/path"
    str_run_start = "Test Run"
    return_idx = -1

    def mock_func():
        return ["Result"]

    # when
    success, result = call_analysis_api(path_to_run, str_run_start, return_idx, mock_func)

    # then
    assert success is True
    assert result == ["Result"]


def test_call_analysis_api_without_path():
    # given
    path_to_run = ""
    str_run_start = "Test Run"
    return_idx = -1

    def mock_func():
        return ["Result"]

    # when
    success, result = call_analysis_api(path_to_run, str_run_start, return_idx, mock_func)

    # then
    assert success is True
    assert result == []


def test_create_scancodejson():
    pass


def test_correct_scanner_result():
    pass


def test_check_exclude_dir():
    # given
    # Create dummy OssItem objects for the test
    oss_list = [
        OssItem("dummy_value"),
        OssItem("dummy_value"),
        OssItem("dummy_value"),
        OssItem("dummy_value"),
        OssItem("dummy_value"),
    ]

    oss_list[0].name = "package1"
    oss_list[0].source_name_or_path = ["/project/venv/file.py"]

    oss_list[1].name = "package2"
    oss_list[1].source_name_or_path = ["/project/src/file.py"]

    oss_list[2].name = "package3"
    oss_list[2].source_name_or_path = ["/project/node_modules/module.js"]

    oss_list[3].name = "package4"
    oss_list[3].source_name_or_path = ["/project/Carthage/Build"]

    oss_list[4].name = "package5"
    oss_list[4].source_name_or_path = ["/project/Pods/framework"]

    # when
    updated_oss_list = check_exclude_dir(oss_list)

    # then
    assert updated_oss_list[0].exclude is True
    assert updated_oss_list[1].exclude is not True
    assert updated_oss_list[2].exclude is True
    assert updated_oss_list[3].exclude is True
    assert updated_oss_list[4].exclude is True
