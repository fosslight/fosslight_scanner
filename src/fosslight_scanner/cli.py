#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import sys
import json
from argparse import ArgumentParser
from ._help import print_help_msg
from .fosslight_scanner import run_main, PKG_NAME
from ._parse_setting import parse_setting_json
from fosslight_util.help import print_package_version
import os.path


def set_args(mode, path, dep_argument, output, format, link, db_url, timer,
             raw, core, no_correction, correct_fpath, ui, setting, exclude_path):
    if setting and os.path.isfile(setting):
        try:
            with open(setting, 'r', encoding='utf-8') as file:
                data = json.load(file)
            s_mode, s_path, s_dep_argument, s_output, s_format, s_link, s_db_url, s_timer, s_raw, s_core, \
                s_no_correction, s_correct_fpath, s_ui, s_exclude_path = parse_setting_json(data)

            # direct cli arguments have higher priority than setting file
            mode = mode if mode else s_mode
            path = path if path else s_path
            dep_argument = dep_argument if dep_argument else s_dep_argument
            output = output if output else s_output
            format = format if format else s_format
            link = link if link else s_link
            db_url = db_url if db_url else s_db_url
            timer = timer if timer else s_timer
            raw = raw if raw else s_raw
            core = core if core else s_core
            no_correction = no_correction if no_correction else s_no_correction
            correct_fpath = correct_fpath if correct_fpath else s_correct_fpath
            ui = ui if ui else s_ui
            exclude_path = exclude_path if exclude_path else s_exclude_path

        except Exception as e:
            print(f"Cannot open setting file: {e}")
    return mode, path, dep_argument, output, format, link, db_url, timer, \
        raw, core, no_correction, correct_fpath, ui, exclude_path


def main():
    parser = ArgumentParser(description='FOSSLight Scanner', prog='fosslight_scanner', add_help=False)
    parser.add_argument('mode', nargs='*', help='source| dependency| binary| all| compare', default="")
    parser.add_argument('--path', '-p', help='Path to analyze (In compare mode, two FOSSLight reports',
                        dest='path', nargs='+', default="")
    parser.add_argument('--wget', '-w', help='Link to be analyzed', type=str, dest='link', default="")
    parser.add_argument('--format', '-f', help='Scanner output file format (excel,yaml), Compare mode (excel,html,yaml,json)',
                        type=str, dest='format', default="")
    parser.add_argument('--output', '-o', help='Output directory or file', type=str, dest='output', default="")
    parser.add_argument('--dependency', '-d', help='Dependency arguments', type=str, dest='dep_argument', default="")
    parser.add_argument('--url', '-u', help="DB Url", type=str, dest='db_url', default="")
    parser.add_argument('--core', '-c', help='Number of processes to analyze source', type=int, dest='core', default=-1)
    parser.add_argument('--raw', '-r', help='Keep raw data', action='store_true', dest='raw', default=False)
    parser.add_argument('--timer', '-t', help='Hide the progress bar', action='store_true', dest='timer', default=False)
    parser.add_argument('--version', '-v', help='Print version', action='store_true', dest='version', default=False)
    parser.add_argument('--help', '-h', help='Print help message', action='store_true', dest='help')
    parser.add_argument('--exclude', '-e', help='Path to exclude from analysis', dest='exclude_path', nargs='*', default=[])
    parser.add_argument('--setting', '-s', help='Scanner json setting file', type=str, dest='setting', default="")
    parser.add_argument('--no_correction', help='No correction with sbom-info.yaml',
                        action='store_true', required=False, default=False)
    parser.add_argument('--correct_fpath', help='Path to the sbom-info.yaml',
                        type=str, required=False, default='')
    parser.add_argument('--ui', help='Generate UI mode result file', action='store_true', required=False, default=False)

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1)

    if args.help:
        print_help_msg()
    elif args.version:
        print_package_version(PKG_NAME, "FOSSLight Scanner Version:")
    else:
        mode, path, dep_argument, output, format, link, db_url, timer, raw, core, no_correction, correct_fpath, \
          ui, exclude_path = set_args(args.mode, args.path, args.dep_argument, args.output, args.format,
                                      args.link, args.db_url, args.timer, args.raw, args.core, args.no_correction,
                                      args.correct_fpath, args.ui, args.setting, args.exclude_path)

        run_main(mode, path, dep_argument, output, format, link, db_url, timer,
                 raw, core, not no_correction, correct_fpath, ui, exclude_path)


if __name__ == "__main__":
    main()
