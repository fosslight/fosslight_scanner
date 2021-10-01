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
from fosslight_source import run_scancode
from fosslight_dependency.run_dependency_scanner import main as dep_main
from fosslight_util.download import cli_download_and_extract
from ._get_input import get_input_mode
from ._help import print_help_msg
from fosslight_util.set_log import init_log
from fosslight_util.write_excel import merge_excels
from fosslight_util.timer_thread import TimerThread
import fosslight_util.constant as constant

_OUTPUT_FILE_PREFIX = "FOSSLight-Report_"
_PKG_NAME = "fosslight_scanner"
logger = logging.getLogger(constant.LOGGER_NAME)
warnings.simplefilter(action='ignore', category=FutureWarning)
_output_dir = "fosslight_raw_data_"
_log_file = "fosslight_log_"
_start_time = ""
_executed_path = ""
_SRC_DIR_FROM_LINK_PREFIX = "fosslight_src_dir_"


def run_analysis(path_to_run, params, func, str_run_start):
    # This function will be replaced by call_analysis_api().
    logger.info("## Start to run "+str_run_start)
    try:
        if path_to_run != "":
            logger.info("|--- Path to analyze :"+path_to_run)
            os.chdir(_output_dir)
            sys.argv = params
            func()
            os.chdir(_executed_path)
        else:
            logger.info("Analyzing path is missing...")
    except SystemExit:
        pass
    except Exception as ex:
        logger.error(str(ex))


def call_analysis_api(path_to_run, str_run_start, func, *args):
    logger.info("## Start to run " + str_run_start)

    try:
        if path_to_run != "":
            logger.info("|--- Path to analyze :"+path_to_run)
            success, msg, result_list = func(*args)
            if not success:
                logger.warning(msg)
        else:
            logger.info("Analyzing path is missing...")
    except SystemExit:
        pass
    except Exception as ex:
        logger.error(str(ex))


def set_sub_parameter(default_params, params):  # For dependency
    try:
        if params != "":
            match_obj = re.findall(
                r'\s*(-\s*[a|d|m|c|p|v|o])\s*\'([^\']+)\'\s*', params)
            for param, value in match_obj:
                default_params.append(param)
                default_params.append(value)
    except Exception as ex:
        logger.warning("SET dependency Param:"+str(ex))
    return default_params


def run(src_path, dep_path, dep_arguments, output_path, remove_raw_data=True,
        remove_src_data=True, need_init=True, result_log={}):
    try:
        success = True
        if need_init:
            success, final_excel_dir, result_log = init(output_path)
        else:
            final_excel_dir = output_path

        if success:
            output_files = {"SRC": "FL_Source",
                            "BIN": "FL_Binary.xlsx",
                            "DEP": "FL_Dependency",
                            "REUSE": "reuse.xml",
                            "FINAL": _OUTPUT_FILE_PREFIX + _start_time + '.xlsx'}

            call_analysis_api(src_path, "Source Analysis",
                              run_scancode.run_scan,
                              os.path.abspath(src_path), os.path.join(
                                  _output_dir, output_files["SRC"]),
                              False)

            run_analysis(dep_path,
                         set_sub_parameter(["DEP",
                                            "-p", os.path.abspath(dep_path),
                                            "-o", _output_dir], dep_arguments),
                         dep_main, "Dependency Analysis")

            ouput_file = os.path.join(final_excel_dir, output_files["FINAL"])
            success, error_msg = merge_excels(_output_dir, ouput_file)
            result_log["Result"] = success
            if success:
                result_log["FOSSLight-Report"] = ouput_file
            else:
                result_log["Result Message - Merge"] = error_msg
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


def run_after_download_source(link, out_dir, remove_raw_data):
    start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        success, final_excel_dir, result_log = init(out_dir)
        temp_src_dir = os.path.join(
            _output_dir, _SRC_DIR_FROM_LINK_PREFIX+start_time)

        logger.info("Link to download :"+link)
        success, msg = cli_download_and_extract(
            link, temp_src_dir, _output_dir)

        if success:
            logger.info("Downloaded Dir:"+temp_src_dir)
            run(temp_src_dir, temp_src_dir,
                "", final_excel_dir, remove_raw_data, remove_raw_data, False, result_log)
        else:
            logger.error("Download failed:" + msg)
    except Exception as ex:
        success = False
        logger.error("Failed to analyze from link:" + str(ex))
    return success


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
                                  True, logging.INFO, logging.DEBUG, _PKG_NAME)

    return os.path.isdir(_output_dir), output_root_dir, result_log


def main():
    global _executed_path
    _cli_mode = False

    # Path_to_analyze
    src_path = ""
    dep_path = ""
    dep_arguments = ""
    url_to_analyze = ""
    _executed_path = os.getcwd()
    output_dir = _executed_path
    remove_raw_data = True

    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv, 'hrs:d:a:o:w:')
    except getopt.GetoptError:
        print_help_msg()

    for opt, arg in opts:
        if opt == "-h":
            print_help_msg()
        elif opt == "-s":
            src_path = arg
            _cli_mode = True
        elif opt == "-d":
            dep_path = arg
            _cli_mode = True
        elif opt == "-a":
            dep_arguments = arg
        elif opt == "-w":
            _cli_mode = True
            url_to_analyze = arg
        elif opt == "-o":
            output_dir = os.path.abspath(arg)
        elif opt == "-r":
            remove_raw_data = False

    try:
        if not _cli_mode:
            src_path, dep_path, dep_arguments, url_to_analyze = get_input_mode()
        timer = TimerThread()
        timer.setDaemon(True)
        timer.start()
        if url_to_analyze != "":
            run_after_download_source(url_to_analyze, output_dir, remove_raw_data)

        if src_path != "" or dep_path != "":
            run(src_path, dep_path,
                dep_arguments, output_dir, remove_raw_data, False)

    except Exception as ex:
        logger.warning(str(ex))


if __name__ == '__main__':
    main()
