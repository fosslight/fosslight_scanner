import pytest
from fosslight_scanner._parse_setting import parse_setting_json

def test_parse_setting_json_valid():
    data = {
        'mode': ['scan'],
        'path': ['/path/to/scan'],
        'dep_argument': '--arg',
        'output': 'output.txt',
        'format': 'json',
        'link': 'http://example.com',
        'db_url': 'http://db.example.com',
        'timer': True,
        'raw': True,
        'core': 4,
        'no_correction': True,
        'correct_fpath': '/path/to/correct',
        'ui': True,
        'exclude': ['/path/to/exclude']
    }
    result = parse_setting_json(data)
    expected = (
        ['scan'], ['/path/to/scan'], '--arg', 'output.txt', 'json', 'http://example.com',
        'http://db.example.com', True, True, 4, True, '/path/to/correct', True, ['/path/to/exclude']
    )
    assert result == expected

def test_parse_setting_json_invalid():
    data = {
        'mode': 'scan',
        'path': '/path/to/scan',
        'dep_argument': 123,
        'output': 456,
        'format': 789,
        'link': 101112,
        'db_url': 131415,
        'timer': 'yes',
        'raw': 'no',
        'core': 'four',
        'no_correction': 'true',
        'correct_fpath': 161718,
        'ui': 'false',
        'exclude': 'exclude_path'
    }
    result = parse_setting_json(data)
    expected = (
        [], [], '', '', '', '', '', False, False, -1, False, '', False, []
    )
    assert result == expected

def test_parse_setting_json_missing_keys():
    data = {}
    result = parse_setting_json(data)
    expected = (
        [], [], '', '', '', '', '', False, False, -1, False, '', False, []
    )
    assert result == expected