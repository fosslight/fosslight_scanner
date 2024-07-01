#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
from fosslight_util.help import PrintHelpMsg

_HELP_MESSAGE_SCANNER = """
    FOSSLight Scanner performs open source analysis after downloading the source from URL that can be cloned by git or wget.
    Instead, open source analysis and checking copyright/license rules can be performed for the local source path.
    The output result is generated in OSS Report format.

    Usage: fosslight [Mode] [option1] <arg1> [option2] <arg2>...

    Parameters:
        Mode: Multiple modes can be entered by separating them with , (ex. source,binary)
            all\t\t\t    Run all scanners(Default)
            source\t\t    Run FOSSLight Source Scanner
            dependency\t\t    Run FOSSLight Dependency Scanner
            binary\t\t    Run FOSSLight Binary Scanner
            compare\t\t    Compare two FOSSLight reports

        Options:
            -h\t\t\t    Print help message
            -p <path>\t\t    Path to analyze (ex, -p {input_path})
                                     * Compare mode input file: Two FOSSLight reports (supports excel, yaml)
                                       (ex, -p {before_name}.xlsx {after_name}.xlsx)
            -w <link>\t\t    Link to be analyzed can be downloaded by wget or git clone
            -f <format>\t\t    FOSSLight Report file format (excel, yaml)
                                     * Compare mode result file: supports excel, json, yaml, html
            -e <path>\t\t    Path to exclude from analysis (ex, -e {dir} {file})
            -o <output>\t\t    Output directory or file
            -c <number>\t\t    Number of processes to analyze source
            -r\t\t\t    Keep raw data
            -t\t\t\t    Hide the progress bar
            -v\t\t\t    Print FOSSLight Scanner version
            -s <path>\t            Path to apply setting from file (check format with 'setting.json' in this repository)
                                     * Direct cli flags have higher priority than setting file
                                       (ex, '-f yaml -s setting.json' - result file extension is .yaml)
            --no_correction\t    Enter if you don't want to correct OSS information with sbom-info.yaml
                                     * Correction mode only supported xlsx format.
            --correct_fpath <path>  Path to the sbom-info.yaml file
            --ui\t\t\t  Generate UI mode result file

        Options for only 'all' or 'bin' mode
            -u <db_url>\t\t    DB Connection(format :'postgresql://username:password@host:port/database_name')

        Options for only 'all' or 'dependency' mode
            -d <dependency_argument>\t    Additional arguments for running dependency analysis"""


def print_help_msg():
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_SCANNER)
    helpMsg.print_help_msg(True)
