import os
import pytest
# import pandas as pd
from fosslight_scanner.common import copy_file, run_analysis, call_analysis_api
# get_osslist, overwrite_excel, check_exclude_dir
# from fosslight_util.oss_item import OssItem


def test_copy_file(tmp_path):
    # success
    source_success = tmp_path / "source.txt"
    destination_success = tmp_path / "destination"
    source_success.write_text("Test content")

    success, copied_file = copy_file(str(source_success), str(destination_success))

    assert success is True
    assert os.path.exists(copied_file)

    # failure
    source_failure = "/nonexistent/path/source.txt"
    destination_failure = "/destination/path"

    success, copied_file = copy_file(source_failure, destination_failure)

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
        return "Mocked result"

    # Mock os.chdir to prevent changing directories during test
    monkeypatch.setattr(os, 'chdir', lambda x: None)
    # Mock os.getcwd to return a default path
    monkeypatch.setattr(os, 'getcwd', lambda: "/mocked/path")

    # when
    result = run_analysis(path_to_run, params, mock_func, "Test Run", output, exe_path)

    # then
    assert result == expected_result


@pytest.mark.parametrize("path_to_run, expected_result", [
    ("/test/path", ["Result"]),
    ("", [])
])
def test_call_analysis_api(path_to_run, expected_result):
    # given
    str_run_start = "Test Run"
    return_idx = -1

    def mock_func(*args, **kwargs):
        return ["Result"]

    # when
    success, result = call_analysis_api(path_to_run, str_run_start, return_idx, mock_func)

    # then
    assert success is True
    assert result == expected_result


# def test_overwrite_excel(tmp_path):
#     # given
#     excel_file_path = tmp_path / "excel_files"
#     excel_file_path.mkdir(parents=True)

#     # Create a sample Excel file
#     sample_file = excel_file_path / "test.xlsx"
#     df = pd.DataFrame({"OSS Name": [None, "Existing OSS"], "Other Column": ["value1", "value2"]})
#     df.to_excel(sample_file, index=False)

#     oss_name = "Updated OSS Name"
#     column_name = "OSS Name"

#     # when
#     overwrite_excel(str(excel_file_path), oss_name, column_name)

#     # then
#     # Check if the Excel file is updated correctly
#     updated_df = pd.read_excel(sample_file)

#     # Ensure the OSS Name column is updated where it was originally empty
#     assert updated_df[column_name].iloc[0] == oss_name, "The first row should be updated with the new OSS name."
#     assert updated_df[column_name].iloc[1] == "Existing OSS", "The second row should remain unchanged."

#     # Check if other columns are unaffected
#     assert updated_df["Other Column"].iloc[0] == "value1"
#     assert updated_df["Other Column"].iloc[1] == "value2"


def test_merge_yamls():
    pass


def test_create_scancodejson():
    pass


def test_correct_scanner_result():
    pass


def test_write_output_with_osslist():
    pass


# def test_get_osslist(monkeypatch, tmp_path):
#     # given
#     output_dir = tmp_path / "output"
#     output_dir.mkdir()
#     output_file = "oss_list.xlsx"

#     # when
#     oss_list = get_osslist(str(output_dir), output_file, ".xlsx")

#     # then
#     assert isinstance(oss_list, list)


# def test_check_exclude_dir():
#     # given
#     # Create dummy OssItem objects for the test
#     oss_list = [
#         OssItem("dummy_value"),
#         OssItem("dummy_value"),
#         OssItem("dummy_value"),
#         OssItem("dummy_value"),
#         OssItem("dummy_value"),
#     ]

#     oss_list[0].name = "package1"
#     oss_list[0].source_name_or_path = ["/project/venv/file.py"]

#     oss_list[1].name = "package2"
#     oss_list[1].source_name_or_path = ["/project/src/file.py"]

#     oss_list[2].name = "package3"
#     oss_list[2].source_name_or_path = ["/project/node_modules/module.js"]

#     oss_list[3].name = "package4"
#     oss_list[3].source_name_or_path = ["/project/Carthage/Build"]

#     oss_list[4].name = "package5"
#     oss_list[4].source_name_or_path = ["/project/Pods/framework"]

#     # when
#     updated_oss_list = check_exclude_dir(oss_list)

#     # then
#     assert updated_oss_list[0].exclude is True
#     assert updated_oss_list[1].exclude is not True
#     assert updated_oss_list[2].exclude is True
#     assert updated_oss_list[3].exclude is True
#     assert updated_oss_list[4].exclude is True
