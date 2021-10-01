#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
from fosslight_util.help import PrintHelpMsg

_HELP_MESSAGE_SCANNER = """
    Usage: fosslight [option1] <arg1> [option2] <arg2>...

    FOSSLight performs open source analysis after downloading the source from URL that can be cloned by git or wget.
    Instead, open source analysis and checking copyright/license rules can be performed for the local source path.
    The output result is generated in OSS Report format.

    Options:
        -h\t\t\t\t\t    Print help message
        -r\t\t\t\t\t    Keep raw data
        -s <source_path>\t\t\t    Path to analyze source
        -w <link>\t\t\t\t    Link to be analyzaed can be downloaded by wget or git clone
        -o <dir_name>\t\t\t\t    Output Directory
        -d <dependency_path> \t\t\t    Path to analyze dependencies
        -d <dependency_path> -a <additional_arg>    (Using with -d option) Additional arguments for running dependency analysis"""


def print_help_msg():
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_SCANNER)
    helpMsg.print_help_msg(True)
