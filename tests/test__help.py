#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0


import sys
from fosslight_scanner._help import print_help_msg, _HELP_MESSAGE_SCANNER


def test_print_help_msg(capsys, monkeypatch):
    # given
    # monkeypatch sys.exit to prevent the test from stopping
    monkeypatch.setattr(sys, "exit", lambda: None)

    # when
    print_help_msg()

    # then
    captured = capsys.readouterr()
    # Validate the help message output
    assert _HELP_MESSAGE_SCANNER.strip() in captured.out
