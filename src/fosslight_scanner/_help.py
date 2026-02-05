#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
from fosslight_util.help import PrintHelpMsg
from fosslight_util.output_format import SUPPORT_FORMAT

_HELP_MESSAGE_SCANNER = f"""
    📖 Usage
    ────────────────────────────────────────────────────────────────────
    fosslight [mode] [options] <arguments>

    📝 Description
    ────────────────────────────────────────────────────────────────────
    FOSSLight Scanner performs comprehensive open source analysis by running
    multiple modes (Source, Dependency, Binary) together. It can download
    source code from URLs (git/wget) or analyze local paths, and generates
    results in OSS Report format.

    📚 Guide: https://fosslight.org/fosslight-guide/scanner/

    🔧 Modes
    ────────────────────────────────────────────────────────────────────
    all (default)          Run all modes (Source, Dependency, Binary)
    source                 Run FOSSLight Source analysis only
    dependency             Run FOSSLight Dependency analysis only
    binary                 Run FOSSLight Binary analysis only
    compare                Compare two FOSSLight reports

    Note: Multiple modes can be specified separated by comma
          Example: fosslight source,binary -p /path/to/analyze

    ⚙️  General Options
    ────────────────────────────────────────────────────────────────────
    -p <path>              Path to analyze
                           • Compare mode: path to two FOSSLight reports (excel/yaml)
    -w <url>               URL to download and analyze (git clone or wget)
    -f <format>            Output format ({', '.join(SUPPORT_FORMAT)})
                           • Compare mode: excel, json, yaml, html
                           • Multiple formats: ex) -f excel yaml json (separated by space)
    -e <pattern>           Exclude paths from analysis (files and directories)
                           ⚠️  IMPORTANT: Always wrap in quotes to avoid shell expansion
                           Example: fosslight -e "test/" "*.jar"
    -o <path>              Output directory or file name
    -c <number>            Number of processes for source analysis
    -r                     Keep raw data from scanners
    -t                     Hide progress bar
    -h                     Show this help message
    -v                     Show version information
    -s <path>              Apply settings from JSON file(check format with 'setting.json' in this repository)
                           Note: CLI flags override settings file
                           Example: -f yaml -s setting.json → output is .yaml
    --no_correction        Skip OSS information correction with sbom-info.yaml
                           (Correction only supports excel format)
    --correct_fpath <path> Path to sbom-info.yaml file for correction
    --recursive_dep        Recursively analyze dependencies

    🔍 Mode-Specific Options
    ────────────────────────────────────────────────────────────────────
    For 'all' or 'binary' mode:
      -u <db_url>          Database connection string
                           Format: postgresql://username:password@host:port/database

    For 'all' or 'dependency' mode:
      -d <args>            Additional arguments for dependency analysis

    💡 Examples
    ────────────────────────────────────────────────────────────────────
    # Scan current directory with all scanners
    fosslight

    # Scan specific path with exclusions
    fosslight -p /path/to/source -e "test/" "node_modules/" "*.pyc"

    # Generate output in specific format
    fosslight -p /path/to/source -f yaml

    # Run specific modes only
    fosslight source,dependency -p /path/to/source

    # Download and analyze from git repository
    fosslight -w https://github.com/user/repo.git -o result_dir

    # Compare two FOSSLight reports
    fosslight compare -p report_v1.xlsx report_v2.xlsx -f excel

    # Run with database connection for binary analysis
    fosslight binary -p /path/to/binary -u "postgresql://user:pass@localhost:5432/sample"
    """


def print_help_msg():
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_SCANNER)
    helpMsg.print_help_msg(True)
