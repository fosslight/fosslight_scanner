#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0


import pytest
from fosslight_scanner._parse_setting import parse_setting_json


@pytest.mark.parametrize("data, expected_output, expect_warning", [
    (
        {
            "mode": ["source", "binary"],
            "path": ["/path/to/scan"],
            "dep_argument": "--arg",
            "output": "output_directory",
            "format": "excel",
            "link": "https://example.com",
            "db_url": "postgresql://user:pass@host/db",
            "timer": True,
            "raw": True,
            "core": 4,
            "no_correction": True,
            "correct_fpath": "sbom-info.yaml",
            "ui": False,
            "exclude": ["excluded/path"]
        },
        (
            ["source", "binary"], ["/path/to/scan"], "--arg", "output_directory", "excel",
            "https://example.com", "postgresql://user:pass@host/db", True, True, 4, True,
            "sbom-info.yaml", False, ["excluded/path"]
        ),
        False
    ),
])
def test_parse_setting_json(data, expected_output, expect_warning, capsys):
    # when
    result = parse_setting_json(data)

    # then
    assert result == expected_output

    # Invalid data should produce a warning message
    captured = capsys.readouterr()
    if expect_warning:
        assert 'Ignoring some values with incorrect format in the setting file.' in captured.out
    else:
        assert 'Ignoring some values with incorrect format in the setting file.' not in captured.out
