import pytest
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from fosslight_scanner.common import *

def test_copy_file(tmpdir):
    src = tmpdir.join("source.txt")
    dest = tmpdir.join("dest.txt")
    src.write("content")

    success, copied_file = copy_file(str(src), str(dest))
    assert success
    assert os.path.exists(copied_file)

    success, copied_file = copy_file("non_existent.txt", str(dest))
    assert not success

def test_run_analysis():
    with patch('os.chdir') as mock_chdir, patch('sys.argv', new=[]):
        def mock_func():
            return "result"
        result = run_analysis("path", ["param"], mock_func, "start", "output", "exe_path")
        assert result == "result"

        result = run_analysis("", ["param"], mock_func, "start", "output", "exe_path")
        assert result == ""

def test_call_analysis_api():
    def mock_func(*args, **kwargs):
        return ["result"]
    success, result = call_analysis_api("path", "start", 0, mock_func)
    assert success
    assert result == "result"

    success, result = call_analysis_api("", "start", 0, mock_func)
    assert not success

def test_overwrite_excel(tmpdir):
    file_path = tmpdir.join("test.xlsx")
    df = pd.DataFrame({"OSS Name": ["", ""]})
    df.to_excel(file_path, index=False)

    overwrite_excel(str(tmpdir), "New OSS Name")
    df = pd.read_excel(file_path)
    assert all(df["OSS Name"] == "New OSS Name")

def test_merge_yamls(tmpdir):
    yaml_file = tmpdir.join("test.yaml")
    yaml_file.write("oss_list: []")
    success, err_msg = merge_yamls(str(tmpdir), ["test.yaml"], "final_report.yaml")
    assert success

def test_create_scancodejson(tmpdir):
    final_report = tmpdir.join("final_report.yaml")
    final_report.write("oss_list: []")
    success, err_msg = create_scancodejson(str(final_report), ".json", "ui_mode_report.json")
    assert success

def test_correct_scanner_result():
    with patch('fosslight_scanner.common.get_osslist', return_value=[]), \
         patch('fosslight_scanner.common.write_output_with_osslist', return_value=(True, "")):
        correct_scanner_result("output_dir", {"SRC": "src_file", "BIN": "bin_file"}, ".xlsx", True, True)

def test_write_output_with_osslist(tmpdir):
    success, err_msg = write_output_with_osslist([], str(tmpdir), "output_file.xlsx", ".xlsx", "Sheet1")
    assert success

def test_get_osslist(tmpdir):
    yaml_file = tmpdir.join("test.yaml")
    yaml_file.write("oss_list: []")
    oss_list = get_osslist(str(tmpdir), "test.yaml", ".yaml")
    assert oss_list == []

def test_check_exclude_dir():
    oss_list = [OssItem(source_name_or_path=["venv/file"])]
    updated_list = check_exclude_dir(oss_list)
    assert updated_list[0].exclude