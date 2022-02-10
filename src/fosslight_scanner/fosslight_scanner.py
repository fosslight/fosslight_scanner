#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Scanner
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import logging
import warnings
import re
import yaml
import sys
from pathlib import Path
from shutil import rmtree as rmdir
from datetime import datetime
from fosslight_binary import binary_analysis
from fosslight_source.cli import run_all_scanners as source_analysis
from fosslight_source.cli import create_report_file
from fosslight_dependency.run_dependency_scanner import run_dependency_scanner
from fosslight_util.download import cli_download_and_extract
from ._get_input import get_input_mode
from fosslight_util.set_log import init_log
from fosslight_util.timer_thread import TimerThread
import fosslight_util.constant as constant
from fosslight_util.output_format import write_output_file, check_output_format
from fosslight_reuse._fosslight_reuse import run_lint as reuse_lint
from .common import copy_file, call_analysis_api

OUTPUT_EXCEL_PREFIX = "FOSSLight-Report_"
OUTPUT_JSON_PREFIX = "Opossum_input_"
PKG_NAME = "fosslight_scanner"
logger = logging.getLogger(constant.LOGGER_NAME)
warnings.simplefilter(action='ignore', category=FutureWarning)
_output_dir = "fosslight_raw_data_"
_log_file = "fosslight_log_"
_start_time = ""
_executed_path = ""
SRC_DIR_FROM_LINK_PREFIX = "fosslight_src_dir_"


def run_dependency(path_to_analyze, output_file_with_path, params=""):
    result_list = []

    package_manager = ""
    pip_activate_cmd = ""
    pip_deactivate_cmd = ""
    output_custom_dir = ""
    app_name = ""
    github_token = ""

    try:
        if params != "":
            match_obj = re.findall(
                r'\s*(-\s*[a|d|m|c|n|t])\s*\'([^\']+)\'\s*', params)
            for param, value in match_obj:
                if param == "-m":
                    package_manager = value
                elif param == "-a":
                    pip_activate_cmd = value
                elif param == "-d":
                    pip_deactivate_cmd = value
                elif param == "-c":
                    output_custom_dir = value
                elif param == "-n":
                    app_name = value
                elif param == "-t":
                    github_token = value
    except Exception as ex:
        logger.warning("Set dependency Param:" + str(ex))

    try:
        success, result = call_analysis_api(path_to_analyze, "Dependency Analysis",
                                            1, run_dependency_scanner,
                                            package_manager,
                                            os.path.abspath(path_to_analyze),
                                            output_file_with_path,
                                            pip_activate_cmd, pip_deactivate_cmd,
                                            output_custom_dir, app_name,
                                            github_token)
        if success:
            result_list = result.get('SRC_FL_Dependency')
    except Exception as ex:
        logger.warning("Run dependency:"+str(ex))

    if not result_list:
        result_list = []
    return result_list


def run_scanner(src_path, dep_arguments, output_path, keep_raw_data=False,
                run_src=True, run_bin=True, run_dep=True, run_reuse=True,
                remove_src_data=True, result_log={}, output_file="",
                output_extension="", num_cores=-1, db_url=""):
    try:
        success = True
        sheet_list = {}
        if not remove_src_data:
            success, final_excel_dir, result_log = init(output_path)
        else:
            final_excel_dir = output_path
        final_excel_dir = os.path.abspath(final_excel_dir)
        abs_path = os.path.abspath(src_path)

        if output_file == "":
            output_prefix = OUTPUT_EXCEL_PREFIX if output_extension != ".json" else OUTPUT_JSON_PREFIX
            output_file = output_prefix + _start_time

        if success:
            output_files = {"SRC": "FL_Source",
                            "BIN": "FL_Binary.xlsx",
                            "BIN_TXT": "FL_Binary.txt",
                            "DEP": "FL_Dependency.xlsx",
                            "REUSE": "reuse.xml"}
            if run_reuse:
                output_reuse = os.path.join(_output_dir, output_files["REUSE"])
                success, result = call_analysis_api(src_path, "Reuse Lint",
                                                    -1, reuse_lint,
                                                    abs_path, "", False,
                                                    output_reuse)
                copy_file(output_reuse, output_path)

            if run_src:
                try:
                    success, result = call_analysis_api(src_path, "Source Analysis",
                                                        -1, source_analysis,
                                                        abs_path,
                                                        os.path.join(_output_dir, output_files["SRC"]),
                                                        False, num_cores, True)
                    if success:
                        sheet_list["SRC_FL_Source"] = [scan_item.get_row_to_print() for scan_item in result[2]]
                        create_report_file(0, result[2], result[3], 'all', True, _output_dir, output_files["SRC"], "")
                except Exception as ex:
                    logger.warning(f"Failed to run source analysis:{ex}")

            if run_bin:
                success, result_bin = call_analysis_api(src_path, "Binary Analysis",
                                                        1, binary_analysis.find_binaries,
                                                        abs_path,
                                                        os.path.join(_output_dir, output_files["BIN"]),
                                                        "", db_url)
                if result_bin:
                    sheet_list["BIN_FL_Binary"] = result_bin
                    copy_file(os.path.join(_output_dir, output_files["BIN_TXT"]), output_path)

            if run_dep:
                result_list = run_dependency(src_path, os.path.join(_output_dir, output_files["DEP"]), dep_arguments)
                sheet_list['SRC_FL_Dependency'] = result_list

            output_file_without_ext = os.path.join(final_excel_dir, output_file)
            success, msg, result_file = write_output_file(output_file_without_ext, output_extension, sheet_list)

            if success:
                logger.info(f"Writing Output file({result_file}, Success: {success}")
            else:
                logger.error(f"Fail to generate result file. msg:({msg})")

            result_log["Result"] = success
            if success:
                file_extension = ".xlsx" if output_extension == "" else output_extension
                result_log["Output File"] = output_file_without_ext + file_extension
            else:
                result_log["Result Message - Merge"] = msg
    except Exception as ex:
        logger.error(f"Scanning:{ex}")

    try:
        _str_final_result_log = yaml.safe_dump(result_log, allow_unicode=True, sort_keys=True)
        logger.info(_str_final_result_log)
    except Exception as ex:
        logger.warn(f"Error to print final log:{ex}")

    try:
        if not keep_raw_data:
            logger.debug(f"Remove temporary files: {_output_dir}")
            rmdir(_output_dir)
        if remove_src_data:
            logger.debug(f"Remove Source: {src_path}")
            rmdir(src_path)
    except Exception as ex:
        logger.debug(f"Error to remove temp files:{ex}")


def download_source(link, out_dir):
    start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    success = False
    temp_src_dir = ""
    try:
        success, final_excel_dir, result_log = init(out_dir)
        temp_src_dir = os.path.join(
            _output_dir, SRC_DIR_FROM_LINK_PREFIX+start_time)

        logger.info("Link to download :"+link)
        success, msg = cli_download_and_extract(
            link, temp_src_dir, _output_dir)

        if success:
            logger.info("Downloaded Dir:"+temp_src_dir)
        else:
            temp_src_dir = ""
            logger.error("Download failed:" + msg)
    except Exception as ex:
        success = False
        logger.error("Failed to analyze from link:" + str(ex))
    return success, temp_src_dir


def init(output_path=""):
    global _output_dir, _log_file, _start_time, logger

    result_log = {}
    output_root_dir = ""
    _start_time = datetime.now().strftime('%Y%m%d_%H%M%S')

    _output_dir = _output_dir + _start_time
    if output_path != "":
        _output_dir = os.path.join(output_path, _output_dir)
        output_root_dir = output_path
    else:
        output_root_dir = _executed_path

    Path(_output_dir).mkdir(parents=True, exist_ok=True)
    _output_dir = os.path.abspath(_output_dir)

    log_dir = os.path.join(output_root_dir, "fosslight_log")
    logger, result_log = init_log(os.path.join(log_dir, _log_file + _start_time + ".txt"),
                                  True, logging.INFO, logging.DEBUG, PKG_NAME)

    return os.path.isdir(_output_dir), output_root_dir, result_log


def run_main(mode, src_path, dep_arguments, output_file_or_dir, file_format, url_to_analyze, db_url,
             hide_progressbar=False, keep_raw_data=False, num_cores=-1):
    output_file = ""
    output_path = _executed_path
    try:
        success, msg, output_path, output_file, output_extension = check_output_format(output_file_or_dir, file_format)
        if not success:
            logger.error(msg)
            sys.exit(1)
        else:
            run_src = False
            run_bin = False
            run_dep = False
            run_reuse = False
            remove_downloaded_source = False

            if src_path == "" and url_to_analyze == "":
                src_path, dep_arguments, url_to_analyze = get_input_mode()

            if not hide_progressbar:
                timer = TimerThread()
                timer.setDaemon(True)
                timer.start()

            if url_to_analyze != "":
                remove_downloaded_source = True
                success, src_path = download_source(url_to_analyze, output_path)

            if mode == "reuse":
                run_reuse = True
            elif mode == "bin":
                run_bin = True
            elif mode == "source":
                run_src = True
            elif mode == "dependency":
                run_dep = True
            else:
                run_src = True
                run_bin = True
                run_dep = True
                run_reuse = True

            if src_path != "":
                run_scanner(src_path, dep_arguments, output_path, keep_raw_data,
                            run_src, run_bin, run_dep, run_reuse,
                            remove_downloaded_source, {}, output_file,
                            output_extension, num_cores, db_url)

    except Exception as ex:
        logger.warning(str(ex))
        return False
    return True
