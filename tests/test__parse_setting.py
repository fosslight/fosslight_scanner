#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

from fosslight_scanner._parse_setting import parse_setting_json


def test_parse_setting_json_valid_data():
    data = {
        'mode': ['test'],
        'path': ['/some/path'],
        'dep_argument': 'arg',
        'output': 'output',
        'format': 'json',
        'link': 'http://example.com',
        'db_url': 'sqlite:///:memory:',
        'timer': True,
        'raw': True,
        'core': 4,
        'no_correction': True,
        'correct_fpath': '/correct/path',
        'ui': True,
        'exclude': ['/exclude/path'],
        'selected_source_scanner': 'scanner',
        'source_write_json_file': True,
        'source_print_matched_text': True,
        'source_time_out': 60,
        'binary_simple': True
    }
    result = parse_setting_json(data)
    assert result == (
        ['test'], ['/some/path'], 'arg', 'output', 'json', 'http://example.com', 'sqlite:///:memory:', True,
        True, 4, True, '/correct/path', True, ['/exclude/path'], 'scanner', True, True, 60, True, False
    )
