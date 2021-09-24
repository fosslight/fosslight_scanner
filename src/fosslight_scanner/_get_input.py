#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import sys
from pip._vendor.distlib.compat import raw_input

_PYTHON_VERSION = 3


def get_input(ask_msg, default_value=""):
    i = 0
    result = True
    for i in range(2):
        return_value = raw_input(
            ask_msg) if _PYTHON_VERSION < 3 else input(ask_msg)
        if return_value != "":
            break
        elif default_value != "":
            break
        else:
            i += 1
    if return_value == "" and default_value == "":
        result = False
    elif return_value == "" and default_value != "":
        return_value = default_value
    return result, return_value


def ask_to_run(ask_msg):
    return_true_item = ["y", "Y", "1"]
    return_value = raw_input(
        ask_msg) if _PYTHON_VERSION < 3 else input(ask_msg)
    return return_value in return_true_item


def get_input_mode():
    global _PYTHON_VERSION
    _PYTHON_VERSION = sys.version_info[0]

    _input_path_msg = "Please enter the path to analyze:"
    _additional_msg = "\n(Enter if it is the same as "\
        + "the source code analysis path)"

    url_to_analyze = ""
    src_path = ""
    dep_path = ""
    dep_arguments = ""

    # 0. Select to analyze
    if ask_to_run("0. What are you going to analyze? (1/2)\n\
        \t1. Links that can be cloned by git or wget\n\
            2. Local source path\n"):
        success, url_to_analyze = get_input("Enter the link to analyze:", "")
    else:
        # 1. FOSSLight Source
        if ask_to_run("1. Do you want to analyze the source code? (y/n)"):
            success, src_path = get_input(_input_path_msg, "")

        if src_path == "":
            _additional_msg = ""

        # 2. FOSSLight Dependency
        if ask_to_run("3. Do you want to analyze the dependency? (y/n)"):
            success, dep_path = get_input(
                _input_path_msg + _additional_msg, src_path)
            success, dep_arguments = get_input(
                "Please enter arguments for dependency analysis:", "")

    return src_path, dep_path, dep_arguments, url_to_analyze
