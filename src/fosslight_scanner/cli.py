#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import sys
from argparse import ArgumentParser
from ._help import print_help_msg
from .fosslight_scanner import run_main, PKG_NAME
from fosslight_util.help import print_package_version


def main():
    parser = ArgumentParser(description='FOSSLight Scanner', prog='fosslight_scanner', add_help=False)
    parser.add_argument('mode', nargs='?', help='source| dependency| binary| prechecker| all| compare', default="all")
    parser.add_argument('--path', '-p', help='Path to analyze (In compare mode, two FOSSLight reports',
                        dest='path', nargs='+', default="")
    parser.add_argument('--wget', '-w', help='Link to be analyzed', type=str, dest='link', default="")
    parser.add_argument('--file', '-f', help='Scanner output file format (excel,yaml), Compare mode (excel,html,yaml,json)',
                        type=str, dest='file', default="")
    parser.add_argument('--output', '-o', help='Output directory or file', type=str, dest='output', default="")
    parser.add_argument('--dependency', '-d', help='Dependency arguments', type=str, dest='dep_argument', default="")
    parser.add_argument('--url', '-u', help="DB Url", type=str, dest='db_url', default="")
    parser.add_argument('--core', '-c', help='Number of processes to analyze source', type=int, dest='core', default=-1)
    parser.add_argument('--raw', '-r', help='Keep raw data',  action='store_true', dest='raw', default=False)
    parser.add_argument('--timer', '-t', help='Hide the progress bar',  action='store_true', dest='timer', default=False)
    parser.add_argument('--version', '-v', help='Print version',  action='store_true', dest='version', default=False)
    parser.add_argument('--help', '-h', help='Print help message', action='store_true', dest='help')

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(0)

    if args.help:
        print_help_msg()
    elif args.version:
        print_package_version(PKG_NAME, "FOSSLight Scanner Version:")
    else:
        run_main(args.mode, args.path, args.dep_argument, args.output, args.file,
                 args.link, args.db_url, args.timer, args.raw, args.core)


if __name__ == "__main__":
    main()
