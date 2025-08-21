#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0


import os
import pytest
from fosslight_scanner.common import copy_file, run_analysis, call_analysis_api, check_package_dir, \
    create_scancodejson, correct_scanner_result


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


def test_create_scancodejson(monkeypatch):
    # Given

    # Mocking os.walk
    def mock_os_walk(path):
        return [("/mocked/absolute/path", ["dir1"], ["file1", "file2"])]

    # Mocking write_scancodejson
    def mock_write_scancodejson(dirname, basename, all_scan_item):
        pass

    # Mocking copy.deepcopy
    def mock_deepcopy(obj):
        return obj

    # Mocking os.path.abspath
    monkeypatch.setattr("os.path.abspath", lambda x: "/mocked/absolute/path")

    # Mocking os.path.basename
    monkeypatch.setattr("os.path.basename", lambda x: "mocked_parent")
    monkeypatch.setattr("os.walk", mock_os_walk)
    monkeypatch.setattr("fosslight_scanner.common.write_scancodejson", mock_write_scancodejson)
    monkeypatch.setattr("copy.deepcopy", mock_deepcopy)

    # Mocking FOSSLIGHT_DEPENDENCY and FOSSLIGHT_SOURCE
    global FOSSLIGHT_DEPENDENCY, FOSSLIGHT_SOURCE
    FOSSLIGHT_DEPENDENCY = "fosslight_dependency"
    FOSSLIGHT_SOURCE = "fosslight_source"

    # Mocking all_scan_item_origin
    class AllScanItem:
        def __init__(self):
            self.file_items = {
                FOSSLIGHT_DEPENDENCY: [],
                FOSSLIGHT_SOURCE: []
            }

    all_scan_item_origin = AllScanItem()
    ui_mode_report = "/mocked/ui_mode_report"
    src_path = "/mocked/src_path"

    # When
    success, err_msg = create_scancodejson(all_scan_item_origin, ui_mode_report, src_path)

    # Then
    assert success is True
    assert err_msg == ''


def test_correct_scanner_result(monkeypatch):
    # Given
    class MockOSSItem:
        def __init__(self, license, exclude=False):
            self.license = license
            self.exclude = exclude

    class MockFileItem:
        def __init__(self, source_name_or_path, oss_items, exclude=False):
            self.source_name_or_path = source_name_or_path
            self.oss_items = oss_items
            self.exclude = exclude

    class MockAllScanItem:
        def __init__(self, file_items):
            self.file_items = file_items

    src_oss_item = MockOSSItem(license="MIT")
    bin_oss_item = MockOSSItem(license="")

    src_file_item = MockFileItem("path/to/source", [src_oss_item])
    bin_file_item = MockFileItem("path/to/source", [bin_oss_item])

    all_scan_item = MockAllScanItem({
        "FOSSLIGHT_SOURCE": [src_file_item],
        "FOSSLIGHT_BINARY": [bin_file_item]
    })

    # When
    result = correct_scanner_result(all_scan_item)
    # Then
    assert len(result.file_items["FOSSLIGHT_BINARY"][0].oss_items) == 1


@pytest.mark.parametrize("source_name_or_path, expected", [
    ("project/venv/file.py", True),
    ("project/node_modules/file.js", True),
    ("project/Pods/file.m", True),
    ("project/Carthage/file.swift", True),
    ("project/src/file.py", False),
    ("project/venv/file.py", True),
])
def test_check_package_dir(source_name_or_path, expected):
    result = check_package_dir(source_name_or_path)
    # Then
    assert result == expected
