#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0


import os
import pytest
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


@pytest.mark.parametrize("source_name_or_path, file_item_exclude, expected", [
    ("project/venv/file.py", False, True),
    ("project/node_modules/file.js", False, True),
    ("project/Pods/file.m", False, True),
    ("project/Carthage/file.swift", False, True),
    ("project/src/file.py", False, False),
    ("project/src/file.py", True, True),
    ("project/venv/file.py", True, True),
])
def test_check_exclude_dir(source_name_or_path, file_item_exclude, expected):
    assert check_exclude_dir(source_name_or_path, file_item_exclude) == expected
