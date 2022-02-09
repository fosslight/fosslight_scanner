#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Scanner
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import sys
import logging
import warnings
import re
import getopt
import yaml
from pathlib import Path
from shutil import rmtree as rmdir
from datetime import datetime
from fosslight_binary import binary_analysis
from fosslight_source import run_scancode
from fosslight_dependency.run_dependency_scanner import run_dependency_scanner
from fosslight_util.download import cli_download_and_extract
from ._get_input import get_input_mode
from ._help import print_help_msg
from fosslight_util.help import print_package_version
from fosslight_util.set_log import init_log
from fosslight_util.timer_thread import TimerThread
import fosslight_util.constant as constant
from fosslight_util.output_format import write_output_file, check_output_format

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


def run_analysis(path_to_run, params, func, str_run_start, output, exe_path):
    # This function will be replaced by call_analysis_api().
    logger.info("## Start to run "+str_run_start)
    return_value = ""
    try:
        if path_to_run != "":
            logger.info("|--- Path to analyze :" + path_to_run)
            os.chdir(output)
            sys.argv = params
            return_value = func()
            os.chdir(exe_path)
        else:
            logger.info("Analyzing path is missing...")
    except SystemExit:
        pass
    except Exception as ex:
        logger.error(str_run_start + ":" + str(ex))
    return return_value


def call_analysis_api(path_to_run, str_run_start, return_idx, func, *args):
    # return_idx == -1 : Raw return value itself
    logger.info("## Start to run " + str_run_start)
    success = True
    result = []
    try:
        if path_to_run != "":
            logger.info("|--- Path to analyze :"+path_to_run)
            result = func(*args)
        else:
            logger.info("Analyzing path is missing...")
    except SystemExit:
        success = False
    except Exception as ex:
        success = False
        logger.error(str_run_start + ":" + str(ex))
    try:
        if success:
            if result and return_idx >= 0:
                if len(result) > return_idx:
                    result = result[return_idx]
                else:
                    success = False
    except Exception as ex:
        logger.debug("Get return value:" + str(ex))
        success = False
    if not result:
        result = []
    return success, result


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


def run(src_path, dep_arguments, output_path, remove_raw_data=True,
        remove_src_data=True, need_init=True, result_log={}, output_file="", output_extension="", num_cores=-1, db_url=""):
    try:
        success = True
        sheet_list = {}
        if need_init:
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
                            "DEP": "FL_Dependency.xlsx",
                            "REUSE": "reuse.xml"}

            success, result = call_analysis_api(src_path, "Source Analysis",
                                                2, run_scancode.run_scan,
                                                abs_path,
                                                os.path.join(_output_dir, output_files["SRC"]),
                                                False, num_cores, True)
            if success:
                sheet_list["SRC_FL_Source"] = [scan_item.get_row_to_print() for scan_item in result]

            success, result_bin = call_analysis_api(src_path, "Binary Analysis",
                                                1, binary_analysis.find_binaries,
                                                abs_path,
                                                os.path.join(_output_dir, output_files["BIN"]),
                                                "", db_url)
            if result_bin:
                sheet_list["BIN_FL_Binary"] = result_bin

            result_list = run_dependency(src_path, os.path.join(_output_dir, output_files["DEP"]), dep_arguments)
            sheet_list['SRC_FL_Dependency'] = result_list

            output_file_without_ext = os.path.join(final_excel_dir, output_file)
            success, msg, result_file = write_output_file(output_file_without_ext, output_extension, sheet_list)

            if success:
                logger.info(f"Writing Output file({result_file}, Success: {success}")
            else:
                logger.error(f"Fail to generate result file. msg:({msg})")
                sys.exit(0)
    except Exception as ex:
        logger.error("Scanning:" + str(ex))

    try:
        _str_final_result_log = yaml.safe_dump(result_log, allow_unicode=True, sort_keys=True)
        logger.info(_str_final_result_log)
    except Exception as ex:
        logger.warn("Error to print final log:"+str(ex))

    try:
        if remove_raw_data:
            logger.debug("Remove temporary files: " + _output_dir)
            rmdir(_output_dir)
        if remove_src_data:
            logger.debug("Remove Source: " + src_path)
            rmdir(src_path)
    except Exception as ex:
        logger.debug("Error to remove temp files:"+str(ex))


def run_after_download_source(link, out_dir):
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


def main():
    global _executed_path
    _cli_mode = False

    # Path_to_analyze
    src_path = ""
    dep_arguments = ""
    url_to_analyze = ""
    _executed_path = os.getcwd()
    remove_raw_data = True
    output_path = _executed_path
    output_file = ""
    output_file_or_dir = ""
    show_progressbar = True
    file_format = ""
    num_cores = -1
    db_url = ""

    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv, 'hvtrs:d:a:o:w:f:p:c:u:')
    except getopt.GetoptError:
        print_help_msg()

    for opt, arg in opts:
        if opt == "-h":
            print_help_msg()
        elif opt == "-v":
            print_package_version(PKG_NAME, "FOSSLight Scanner Version:")
        elif opt == "-p":
            src_path = arg
            _cli_mode = True
        elif opt == "-d":
            dep_arguments = arg
        elif opt == "-w":
            _cli_mode = True
            url_to_analyze = arg
        elif opt == "-o":
            output_file_or_dir = arg
        elif opt == "-r":
            remove_raw_data = False
        elif opt == "-t":
            show_progressbar = False
        elif opt == "-f":
            file_format = arg
        elif opt == "-c":
            num_cores = arg
        elif opt == "-u":
            db_url = arg

    try:
        success, msg, output_path, output_file, output_extension = check_output_format(output_file_or_dir, file_format)
        if not success:
            logger.error(msg)
            return False

        if not _cli_mode:
            src_path, dep_arguments, url_to_analyze = get_input_mode()
        if show_progressbar:
            timer = TimerThread()
            timer.setDaemon(True)
            timer.start()

        if url_to_analyze != "":
            success, src_path = run_after_download_source(url_to_analyze, output_path)
        if src_path != "":
            run(src_path, dep_arguments, output_path, remove_raw_data,
                False, True, {}, output_file, output_extension, num_cores, db_url)
    except Exception as ex:
        logger.warning(str(ex))


if __name__ == '__main__':
    main()
