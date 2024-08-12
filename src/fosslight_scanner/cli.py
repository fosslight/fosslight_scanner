#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import importlib
from pathlib import Path
import sys
import json
import os
import os.path
from argparse import ArgumentParser

from ._help import print_help_msg
from .fosslight_scanner import run_main, PKG_NAME
from ._parse_setting import parse_setting_json
from fosslight_util.help import print_package_version
import os.path


def print_make_license_notice(output_dir=None):
    try:
        # fosslight_binary 패키지의 위치 찾기
        spec = importlib.util.find_spec("fosslight_binary")
        if spec is None:
            print("fosslight_binary package not found")
            return

        package_root = Path(spec.origin).parent

        licenses_path = package_root / "LICENSES"

        if not licenses_path.exists():
            print(f"LICENSES directory not found at {licenses_path}")
            return

        license_content = f"*** {PKG_NAME} open source license notice ***\n\n"
        for license_file in licenses_path.glob("*"):
            if license_file.is_file():
                with open(license_file, 'r', encoding='utf8') as f:
                    file_content = f.read()
                    license_content += file_content
                    license_content += "\n" + "="*80 + "\n\n"

        if output_dir:
            output_path = Path(output_dir) / f"{PKG_NAME}_licenses.txt"
            with open(output_path, 'w', encoding='utf8') as f:
                f.write(license_content)
            print(f"License notice has been saved to: {output_path}")

        print(license_content)

    except Exception as e:
        print(f"Error while printing license notice: {e}")


def set_args(mode, path, dep_argument, output, format, link, db_url, timer,
             raw, core, no_correction, correct_fpath, ui, setting, exclude_path,
             selected_source_scanner, source_write_json_file, source_print_matched_text, source_time_out,
             binary_simple, binary_notice):

    if setting and os.path.isfile(setting):
        try:
            with open(setting, 'r', encoding='utf-8') as file:
                data = json.load(file)
            s_mode, s_path, s_dep_argument, s_output, s_format, s_link, s_db_url, s_timer, s_raw, s_core, \
                s_no_correction, s_correct_fpath, s_ui, s_exclude_path, \
                s_selected_source_scanner, s_source_write_json_file, s_source_print_matched_text, \
                s_source_time_out, s_binary_simple, s_binary_notice = parse_setting_json(data)

            # direct cli arguments have higher priority than setting file
            mode = mode or s_mode
            path = path or s_path
            dep_argument = dep_argument or s_dep_argument
            output = output or s_output
            format = format or s_format
            link = link or s_link
            db_url = db_url or s_db_url
            timer = timer or s_timer
            raw = raw or s_raw
            core = core if core != -1 else s_core
            no_correction = no_correction or s_no_correction
            correct_fpath = correct_fpath or s_correct_fpath
            ui = ui or s_ui
            exclude_path = exclude_path or s_exclude_path
            selected_source_scanner = selected_source_scanner or s_selected_source_scanner
            source_write_json_file = source_write_json_file or s_source_write_json_file
            source_print_matched_text = source_print_matched_text or s_source_print_matched_text
            source_time_out = source_time_out if source_time_out != 120 else s_source_time_out
            binary_simple = binary_simple or s_binary_simple
            binary_notice = binary_notice if binary_notice is not False else s_binary_notice
        except Exception as e:
            print(f"Cannot open setting file: {e}")
    return mode, path, dep_argument, output, format, link, db_url, timer, \
        raw, core, no_correction, correct_fpath, ui, exclude_path, \
        selected_source_scanner, source_write_json_file, source_print_matched_text, source_time_out, \
        binary_simple, binary_notice


def main():
    parser = ArgumentParser(description='FOSSLight Scanner',
                            prog='fosslight_scanner', add_help=False)
    parser.add_argument('mode', nargs='*',
                        help='source| dependency| binary| all| compare',
                        default="")
    parser.add_argument('--path', '-p',
                        help='Path to analyze (In compare mode, two FOSSLight reports',
                        dest='path', nargs='+', default="")
    parser.add_argument('--wget', '-w', help='Link to be analyzed',
                        type=str, dest='link', default="")
    parser.add_argument('--format', '-f',
                        help='Scanner output file format (excel,yaml), Compare mode (excel,html,yaml,json)',
                        type=str, dest='format', default="")
    parser.add_argument('--output', '-o', help='Output directory or file',
                        type=str, dest='output', default="")
    parser.add_argument('--dependency', '-d', help='Dependency arguments',
                        type=str, dest='dep_argument', default="")
    parser.add_argument('--url', '-u', help="DB Url",
                        type=str, dest='db_url', default="")
    parser.add_argument('--core', '-c',
                        help='Number of processes to analyze source',
                        type=int, dest='core', default=-1)
    parser.add_argument('--raw', '-r', help='Keep raw data',
                        action='store_true', dest='raw', default=False)
    parser.add_argument('--timer', '-t', help='Hide the progress bar',
                        action='store_true', dest='timer', default=False)
    parser.add_argument('--version', '-v', help='Print version',
                        action='store_true', dest='version', default=False)
    parser.add_argument('--help', '-h', help='Print help message',
                        action='store_true', dest='help')
    parser.add_argument('--exclude', '-e', help='Path to exclude from analysis',
                        dest='exclude_path', nargs='*', default=[])
    parser.add_argument('--setting', '-s', help='Scanner json setting file',
                        type=str, dest='setting', default="")
    parser.add_argument('--no_correction',
                        help='No correction with sbom-info.yaml',
                        action='store_true', required=False, default=False)
    parser.add_argument('--correct_fpath', help='Path to the sbom-info.yaml',
                        type=str, required=False, default='')
    parser.add_argument('--ui', help='Generate UI mode result file',
                        action='store_true', required=False, default=False)
    parser.add_argument('--selected_source_scanner',
                        help='Specify the source scanner to use',
                        type=str, required=False, default='')
    parser.add_argument('--source_write_json_file',
                        help='Generate raw result of scanners in json format',
                        required=False, default=False)
    parser.add_argument('--source_print_matched_text',
                        help='Print additional information for scan result on separate sheets',
                        required=False, default=False)
    parser.add_argument('--source_time_out',
                        help='Stop scancode scanning if scanning takes longer than a timeout in seconds',
                        type=int, dest='source_time_out', default=120)
    parser.add_argument('--binary_simple',
                        help='Extract only the binary list in simple mode',
                        action='store_true', required=False, default=False)
    parser.add_argument('--binary_notice',
                        help='Print the open source license notice text',
                        action='store_true', required=False, default=False)

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
            ui, exclude_path, selected_source_scanner, source_write_json_file, source_print_matched_text, \
            source_time_out, binary_simple, binary_notice = set_args(
                args.mode, args.path, args.dep_argument, args.output,
                args.format, args.link, args.db_url, args.timer, args.raw,
                args.core, args.no_correction, args.correct_fpath, args.ui,
                args.setting, args.exclude_path, args.selected_source_scanner,
                args.source_write_json_file, args.source_print_matched_text,
                args.source_time_out, args.binary_simple, args.binary_notice)

        run_main(mode, path, dep_argument, output, format, link, db_url, timer,
                 raw, core, not no_correction, correct_fpath, ui, exclude_path,
                 selected_source_scanner, source_write_json_file, source_print_matched_text,
                 source_time_out, binary_simple,)
    if binary_notice:
        print_make_license_notice(output_dir=output)
        sys.exit(0)


if __name__ == "__main__":
    main()
