#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

import pytest
import json
import sys
from fosslight_scanner.cli import main, set_args


def test_set_args(monkeypatch):
    # Mocking os.path.isfile to return True
    monkeypatch.setattr("os.path.isfile", lambda x: True)

    # Mocking the open function to return a mock file object
    mock_file_data = json.dumps({
        "mode": ["test_mode"],
        "path": ["test_path"],
        "dep_argument": "test_dep_argument",
        "output": "test_output",
        "format": ["test_format"],
        "link": "test_link",
        "db_url": "test_db_url",
        "timer": True,
        "raw": True,
        "core": 4,
        "no_correction": True,
        "correct_fpath": "test_correct_fpath",
        "ui": True,
        "exclude": ["test_exclude_path"],
        "selected_source_scanner": "test_scanner",
        "source_write_json_file": True,
        "source_print_matched_text": True,
        "source_time_out": 100,
        "binary_simple": True
    })

    def mock_open(*args, **kwargs):
        from io import StringIO
        return StringIO(mock_file_data)

    monkeypatch.setattr("builtins.open", mock_open)

    # Call the function with some arguments
    result = set_args(
        mode=None, path=None, dep_argument=None, output=None, format=None, link=None, db_url=None, timer=None,
        raw=None, core=-1, no_correction=None, correct_fpath=None, ui=None, setting="dummy_path", exclude_path=None,
        recursive_dep=False
    )

    # Expected result
    expected = (
        ["test_mode"], ["test_path"], "test_dep_argument", "test_output", ["test_format"], "test_link", "test_db_url", True,
        True, 4, True, "test_correct_fpath", True, ["test_exclude_path"], "test_scanner", True, True, 100, True, False
    )

    assert result == expected


def test_main_invalid_option(capsys):
    # given
    test_args = ["fosslight_scanner", "--invalid_option"]
    sys.argv = test_args

    # when
    with pytest.raises(SystemExit):  # 예상되는 SystemExit 처리
        main()

    # then
    captured = capsys.readouterr()
    assert "unrecognized arguments" in captured.err  # 인식되지 않은 인자에 대한 에러 메시지 확인
