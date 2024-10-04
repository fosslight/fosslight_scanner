#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0


from fosslight_scanner._get_input import get_input, get_input_mode


def test_get_input(monkeypatch):
    # given
    ask_msg = "Please enter the path to analyze:"
    default_value = "default"

    # when
    # Mock input to return an empty string
    monkeypatch.setattr('builtins.input', lambda _: "")
    result_no_input = get_input(ask_msg, default_value)

    # Mock input to return "user_input"
    monkeypatch.setattr('builtins.input', lambda _: "user_input")
    result_with_input = get_input(ask_msg, "user_input")

    # then
    assert result_no_input == "default"
    assert result_with_input == "user_input"


def test_get_input_mode(monkeypatch):
    # given
    executed_path = ""
    mode_list = ["all", "dep"]

    # Mock ask_to_run to return a predetermined input value
    monkeypatch.setattr('fosslight_scanner._get_input.ask_to_run', lambda _: "1")

    # Mock input to provide other necessary return values
    monkeypatch.setattr('builtins.input', lambda _: "https://example.com")

    # when
    _, _, url_to_analyze = get_input_mode(executed_path, mode_list)

    # then
    assert url_to_analyze == "https://example.com"
