#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0


import pytest
from fosslight_scanner._run_compare import write_result_json_yaml, parse_result_for_table, get_sample_html, \
    write_result_html, write_result_xlsx, write_compared_result, get_comparison_result_filename, \
    count_compared_result, run_compare, \
    ADD, DELETE, CHANGE, XLSX_EXT, HTML_EXT, YAML_EXT, JSON_EXT
import logging
import json
import yaml


@pytest.mark.parametrize("ext, expected_content", [
    # Test for JSON and YAML extensions
    (".json", {"key": "value"}),
    (".yaml", {"key": "value"}),

    # Test for TXT extension (failure)
    (".txt", {"key": "value"}),
])
def test_write_result_json_yaml(tmp_path, ext, expected_content):
    # given
    output_file = tmp_path / f"result{ext}"
    compared_result = expected_content

    # when
    success = write_result_json_yaml(output_file, compared_result, ext)

    # then
    assert success is True, f"Failed to write file with extension {ext}"

    # Verify content based on extension
    if ext == ".json":
        with open(output_file, 'r', encoding='utf-8') as f:
            result_content = json.load(f)
        assert result_content == compared_result, "The content of the JSON file does not match the expected content."

    elif ext == ".yaml":
        with open(output_file, 'r', encoding='utf-8') as f:
            result_content = yaml.safe_load(f)
        assert result_content == compared_result, "The content of the YAML file does not match the expected content."

    elif ext == ".txt":
        with open(output_file, 'r', encoding='utf-8') as f:
            result_lines = f.readlines()
        result_content = ''.join(result_lines)
        assert result_content != compared_result, "The content of the TXT file does not match the expected string representation."


def test_parse_result_for_table():
    # given
    add_expected = [ADD, '', '', 'test(1.0)', 'MIT']
    oi = {"name": "test", "version": "1.0", "license": ["MIT"]}

    # when
    add_result = parse_result_for_table(oi, ADD)

    # then
    assert add_result == add_expected


def test_get_sample_html():
    # then
    assert get_sample_html() != ''


@pytest.mark.parametrize("compared_result, expected_before, expected_after", [
    # Case with empty add, delete, change
    ({ADD: [], DELETE: [], CHANGE: []}, "before.yaml", "after.yaml"),

    # Case with one entry in add and no deletes or changes
    ({ADD: [{"name": "test", "version": "1.0", "license": ["MIT"]}], DELETE: [], CHANGE: []},
     "before.yaml", "after.yaml")
])
def test_write_result_html(tmp_path, compared_result, expected_before, expected_after):
    # given
    output_file = tmp_path / "result.html"

    # when
    success = write_result_html(output_file, compared_result, expected_before, expected_after)

    # then
    assert success is True, "Failed to write the HTML file."
    assert output_file.exists(), "The HTML file was not created."
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert content, "The HTML file is empty."


@pytest.mark.parametrize("compared_result", [
    # Case with empty add, delete, change
    {ADD: [], DELETE: [], CHANGE: []},

    # Case with one entry in add and no deletes or changes
    {ADD: [{"name": "test", "version": "1.0", "license": ["MIT"]}], DELETE: [], CHANGE: []}
])
def test_write_result_xlsx(tmp_path, compared_result):
    # given
    output_file = tmp_path / "result.xlsx"

    # when
    success = write_result_xlsx(output_file, compared_result)

    # then
    assert success is True, "Failed to write the XLSX file."
    assert output_file.exists(), "The XLSX file was not created."


@pytest.mark.parametrize("ext, expected_output", [
    (XLSX_EXT, "xlsx"),
    (HTML_EXT, "html"),
    (JSON_EXT, "json"),
    (YAML_EXT, "yaml"),
])
def test_write_compared_result(tmp_path, ext, expected_output):
    # given
    output_file = tmp_path / "result"
    compared_result = {ADD: [], DELETE: [], CHANGE: []}

    # when
    success, result_file = write_compared_result(output_file, compared_result, ext)

    # then
    assert success is True, f"Failed to write the compared result for extension {ext}"
    if ext == XLSX_EXT:
        assert str(result_file) == str(output_file), "The XLSX result file path does not match the expected output path."
    elif ext == HTML_EXT:
        expected_result_file = f"{str(output_file) + XLSX_EXT}, {str(output_file)}"
        assert result_file == expected_result_file, "HTML file creation failed."
    elif ext == JSON_EXT:
        assert str(result_file) == str(output_file), "The JSON result file path does not match the expected output path."
    else:
        assert str(result_file) == str(output_file), "The YAML result file path does not match the expected output path."


@pytest.mark.parametrize("path, file_name, ext, time_suffix, expected_output", [
    # Case when file name is provided
    ("/path", "file", XLSX_EXT, "time", "/path/file.xlsx"),

    # Case when file name is empty, with different extensions
    ("/path", "", XLSX_EXT, "time", "/path/fosslight_compare_time.xlsx"),
    ("/path", "", HTML_EXT, "time", "/path/fosslight_compare_time.html"),
    ("/path", "", YAML_EXT, "time", "/path/fosslight_compare_time.yaml"),
    ("/path", "", JSON_EXT, "time", "/path/fosslight_compare_time.json"),
])
def test_get_comparison_result_filename(path, file_name, ext, time_suffix, expected_output):
    # when
    result = get_comparison_result_filename(path, file_name, ext, time_suffix)

    # then
    assert result == expected_output, f"Expected {expected_output} but got {result}"


@pytest.mark.parametrize("compared_result, expected_log", [
    ({ADD: [], DELETE: [], CHANGE: []}, "all oss lists are the same."),
    ({ADD: [{"name": "test"}], DELETE: [], CHANGE: []}, "total 1 oss updated (add: 1, delete: 0, change: 0)")
])
def test_count_compared_result(compared_result, expected_log, caplog):
    # when
    with caplog.at_level(logging.INFO):
        count_compared_result(compared_result)
    # then
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

    # Write these contents to the files
    with open(before_f, "w") as bf:
        yaml.dump(before_content, bf)

    # Create an empty xlsx file for after_f
    with open(after_f, "w") as af:
        af.write("")

    # when
    comparison_result = run_compare(before_f, after_f, output_path, output_file, file_ext, _start_time, _output_dir)

    # then
    assert comparison_result is False
