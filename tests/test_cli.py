import pytest
import json
import os
from fosslight_scanner.cli import set_args

def test_set_args_with_valid_setting_file(mocker):
    # Mock the os.path.isfile to return True
    mocker.patch('os.path.isfile', return_value=True)
    
    # Mock the open function to return a valid JSON
    mock_open = mocker.mock_open(read_data=json.dumps({
        "mode": "source",
        "path": "/test/path",
        "dep_argument": "test_dep",
        "output": "test_output",
        "format": "json",
        "link": "http://test.link",
        "db_url": "http://test.db.url",
        "timer": True,
        "raw": True,
        "core": 4,
        "no_correction": True,
        "correct_fpath": "/test/correct/path",
        "ui": True,
        "exclude_path": ["/exclude/path"]
    }))
    mocker.patch('builtins.open', mock_open)
    
    mode, path, dep_argument, output, format, link, db_url, timer, raw, core, no_correction, correct_fpath, ui, exclude_path = set_args(
        None, None, None, None, None, None, None, None, None, None, None, None, None, "test_setting.json", None
    )
    
    assert mode == "source"
    assert path == "/test/path"
    assert dep_argument == "test_dep"
    assert output == "test_output"
    assert format == "json"
    assert link == "http://test.link"
    assert db_url == "http://test.db.url"
    assert timer is True
    assert raw is True
    assert core == 4
    assert no_correction is True
    assert correct_fpath == "/test/correct/path"
    assert ui is True
    assert exclude_path == ["/exclude/path"]

def test_set_args_with_invalid_setting_file(mocker):
    # Mock the os.path.isfile to return True
    mocker.patch('os.path.isfile', return_value=True)
    
    # Mock the open function to raise an exception
    mocker.patch('builtins.open', side_effect=Exception("File not found"))
    
    mode, path, dep_argument, output, format, link, db_url, timer, raw, core, no_correction, correct_fpath, ui, exclude_path = set_args(
        None, None, None, None, None, None, None, None, None, None, None, None, None, "invalid_setting.json", None
    )
    
    assert mode is None
    assert path is None
    assert dep_argument is None
    assert output is None
    assert format is None
    assert link is None
    assert db_url is None
    assert timer is None
    assert raw is None
    assert core is None
    assert no_correction is None
    assert correct_fpath is None
    assert ui is None
    assert exclude_path is None

def test_set_args_without_setting_file():
    mode, path, dep_argument, output, format, link, db_url, timer, raw, core, no_correction, correct_fpath, ui, exclude_path = set_args(
        "source", "/test/path", "test_dep", "test_output", "json", "http://test.link", "http://test.db.url", True, True, 4, True, "/test/correct/path", True, None, ["/exclude/path"]
    )
    
    assert mode == "source"
    assert path == "/test/path"
    assert dep_argument == "test_dep"
    assert output == "test_output"
    assert format == "json"
    assert link == "http://test.link"
    assert db_url == "http://test.db.url"
    assert timer is True
    assert raw is True
    assert core == 4
    assert no_correction is True
    assert correct_fpath == "/test/correct/path"
    assert ui is True
    assert exclude_path == ["/exclude/path"]