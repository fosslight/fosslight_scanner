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
import shutil
from pathlib import Path
from datetime import datetime
from fosslight_binary import binary_analysis
from fosslight_dependency.run_dependency_scanner import run_dependency_scanner
from fosslight_util.download import cli_download_and_extract
from ._get_input import get_input_mode
from fosslight_util.set_log import init_log
from fosslight_util.timer_thread import TimerThread
import fosslight_util.constant as constant
from fosslight_util.output_format import check_output_format
from fosslight_prechecker._precheck import run_lint as prechecker_lint
from .common import (copy_file, call_analysis_api,
                     overwrite_excel, extract_name_from_link,
                     merge_yamls, correct_scanner_result)
from fosslight_util.write_excel import merge_excels
from ._run_compare import run_compare
import subprocess
fosslight_source_installed = True
try:
    from fosslight_source.cli import run_all_scanners as source_analysis
    from fosslight_source.cli import create_report_file
except ModuleNotFoundError:
    fosslight_source_installed = False

OUTPUT_REPORT_PREFIX = "fosslight_report_all_"
PKG_NAME = "fosslight_scanner"
logger = logging.getLogger(constant.LOGGER_NAME)
warnings.simplefilter(action='ignore', category=FutureWarning)
_output_dir = "fosslight_raw_data"
_log_file = "fosslight_log_all_"
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
        logger.warning(f"Set dependency Param: {ex}")

    timer = TimerThread()
    timer.setDaemon(True)
    timer.start()

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
        logger.warning(f"Run dependency: {ex}")

    if not result_list:
        result_list = []
    return result_list


def run_scanner(src_path, dep_arguments, output_path, keep_raw_data=False,
                run_src=True, run_bin=True, run_dep=True, run_prechecker=True,
                remove_src_data=True, result_log={}, output_file="",
                output_extension="", num_cores=-1, db_url="",
                default_oss_name="", url="",
                correct_mode=True, correct_fpath=""):
    final_excel_dir = output_path
    success = True
    temp_output_fiiles = []
    if not remove_src_data:
        success, final_excel_dir, result_log = init(output_path)

    if output_file == "":
        output_file = OUTPUT_REPORT_PREFIX + _start_time

    if output_extension == "":
        output_extension = ".xlsx"

    if not correct_fpath:
        correct_fpath = src_path

    try:
        sheet_list = {}
        final_excel_dir = os.path.abspath(final_excel_dir)
        abs_path = os.path.abspath(src_path)

        if success:
            output_files = {"SRC": f"fosslight_src_{_start_time}{output_extension}",
                            "BIN": f"fosslight_bin_{_start_time}{output_extension}",
                            "BIN_TXT": f"fosslight_binary_bin_{_start_time}.txt",
                            "DEP": f"fosslight_dep_{_start_time}{output_extension}",
                            "PRECHECKER": f"fosslight_lint_{_start_time}.yaml"}
            if run_prechecker:
                output_prechecker = os.path.join(_output_dir, output_files["PRECHECKER"])
                success, result = call_analysis_api(src_path, "Prechecker Lint",
                                                    -1, prechecker_lint,
                                                    abs_path, False,
                                                    output_prechecker)
                success_file, copied_file = copy_file(output_prechecker, output_path)
                if success_file:
                    temp_output_fiiles.append(copied_file)

            if run_src:
                try:
                    if fosslight_source_installed:
                        src_output = os.path.join(_output_dir, output_files["SRC"])
                        success, result = call_analysis_api(src_path, "Source Analysis",
                                                            -1, source_analysis,
                                                            abs_path,
                                                            src_output,
                                                            False, num_cores)
                        if success:
                            sheet_list["SRC_FL_Source"] = [scan_item.get_row_to_print() for scan_item in result[2]]
                            create_report_file(0, result[2], result[3], 'all', False,
                                               _output_dir, output_files["SRC"].split('.')[0], output_extension,
                                               correct_mode, correct_fpath, abs_path)
                    else:  # Run fosslight_source by using docker image
                        src_output = os.path.join("output", output_files["SRC"])
                        output_rel_path = os.path.relpath(abs_path, os.getcwd())
                        command = f"docker run -it -v {_output_dir}:/app/output "\
                                  f"fosslight -p {output_rel_path} -o {src_output}.xlsx"
                        command_result = subprocess.run(command.split(' '), stdout=subprocess.PIPE, text=True)
                        logger.info(f"Source Analysis Result:{command_result.stdout}")

                except Exception as ex:
                    logger.warning(f"Failed to run source analysis: {ex}")

            if run_bin:
                success, _ = call_analysis_api(src_path, "Binary Analysis",
                                               1, binary_analysis.find_binaries,
                                               abs_path,
                                               os.path.join(_output_dir, output_files["BIN"]),
                                               "", db_url, False,
                                               correct_mode, correct_fpath)
                if success:
                    output_binary_txt_raw = f"{output_files['BIN'].split('.')[0]}.txt"
                    success_file, copied_file = copy_file(os.path.join(_output_dir, output_binary_txt_raw),
                                                          os.path.join(output_path, output_files["BIN_TXT"]))
                    if success_file:
                        temp_output_fiiles.append(copied_file)

            if run_dep:
                run_dependency(src_path, os.path.join(_output_dir, output_files["DEP"]), dep_arguments)

        else:
            return

    except Exception as ex:
        logger.error(f"Scanning: {ex}")

    try:
        output_file_without_ext = os.path.join(final_excel_dir, output_file)
        final_report = f"{output_file_without_ext}{output_extension}"

        if output_extension == ".xlsx":
            tmp_dir = f"tmp_{datetime.now().strftime('%y%m%d_%H%M')}"
            exist_src = False
            exist_bin = False
            if correct_mode:
                os.makedirs(os.path.join(_output_dir, tmp_dir), exist_ok=True)
                if os.path.exists(os.path.join(_output_dir, output_files['SRC'])):
                    exist_src = True
                    shutil.copy2(os.path.join(_output_dir, output_files['SRC']), os.path.join(_output_dir, tmp_dir))
                if os.path.exists(os.path.join(_output_dir, output_files['BIN'])):
                    exist_bin = True
                    shutil.copy2(os.path.join(_output_dir, output_files['BIN']), os.path.join(_output_dir, tmp_dir))
                if exist_src or exist_bin:
                    correct_scanner_result(_output_dir, output_files, output_extension, exist_src, exist_bin)

            if remove_src_data:
                overwrite_excel(_output_dir, default_oss_name, "OSS Name")
                overwrite_excel(_output_dir, url, "Download Location")
            success, err_msg = merge_excels(_output_dir, final_report)

            if correct_mode:
                if exist_src:
                    shutil.move(os.path.join(_output_dir, tmp_dir, output_files['SRC']),
                                os.path.join(_output_dir, output_files['SRC']))
                if exist_bin:
                    shutil.move(os.path.join(_output_dir, tmp_dir, output_files['BIN']),
                                os.path.join(_output_dir, output_files['BIN']))
                shutil.rmtree(os.path.join(_output_dir, tmp_dir), ignore_errors=True)
        elif output_extension == ".yaml":
            merge_yaml_files = [output_files["SRC"], output_files["BIN"], output_files["DEP"]]
            success, err_msg = merge_yamls(_output_dir, merge_yaml_files, final_report,
                                           remove_src_data, default_oss_name, url)
        if success:
            if os.path.isfile(final_report):
                result_log["Output File"] = final_report
            else:
                result_log["Output File"] = 'Nothing is detected from the scanner so output file is not generated.'
        else:
            logger.error(f"Fail to generate a result file({final_report}): {err_msg}")

        _str_final_result_log = yaml.safe_dump(result_log, allow_unicode=True, sort_keys=True)
        logger.info(_str_final_result_log)
    except Exception as ex:
        logger.warning(f"Error to write final report: {ex}")

    try:
        if remove_src_data:
            logger.debug(f"Remove temporary source: {src_path}")
            shutil.rmtree(src_path)
    except Exception as ex:
        logger.debug(f"Error to remove temp files:{ex}")


def download_source(link, out_dir):
    start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    success = False
    temp_src_dir = ""
    try:
        success, final_excel_dir, result_log = init(out_dir)
        temp_src_dir = os.path.join(
            _output_dir, SRC_DIR_FROM_LINK_PREFIX + start_time)

        link = link.strip()
        logger.info(f"Link to download: {link}")
        success, msg = cli_download_and_extract(
            link, temp_src_dir, _output_dir)

        if success:
            logger.info(f"Downloaded Dir: {temp_src_dir}")
        else:
            temp_src_dir = ""
            logger.error(f"Download failed: {msg}")
    except Exception as ex:
        success = False
        logger.error(f"Failed to analyze from link: {ex}")
    return success, temp_src_dir


def init(output_path="", make_outdir=True):
    global _output_dir, _log_file, _start_time, logger

    result_log = {}
    output_root_dir = ""
    _start_time = datetime.now().strftime('%y%m%d_%H%M')

    if output_path != "":
        _output_dir = os.path.join(output_path, _output_dir)
        output_root_dir = output_path
    else:
        output_root_dir = _executed_path

    if make_outdir:
        Path(_output_dir).mkdir(parents=True, exist_ok=True)
        _output_dir = os.path.abspath(_output_dir)

    log_dir = os.path.join(output_root_dir, "fosslight_log")
    logger, result_log = init_log(os.path.join(log_dir, f"{_log_file}{_start_time}.txt"),
                                  True, logging.INFO, logging.DEBUG, PKG_NAME)

    return os.path.isdir(_output_dir), output_root_dir, result_log


def run_main(mode, path_arg, dep_arguments, output_file_or_dir, file_format, url_to_analyze, db_url,
             hide_progressbar=False, keep_raw_data=False, num_cores=-1, correct_mode=True, correct_fpath=""):
    global _executed_path, _start_time

    output_file = ""
    default_oss_name = ""
    src_path = ""
    _executed_path = os.getcwd()

    if mode == "compare":
        CUSTOMIZED_FORMAT = {'excel': '.xlsx', 'html': '.html', 'json': '.json', 'yaml': '.yaml'}
        if isinstance(path_arg, list) and len(path_arg) == 2:
            before_comp_f = path_arg[0]
            after_comp_f = path_arg[1]
        else:
            logger.error("Enter two FOSSLight report file with 'p' option.")
            return False
    else:
        CUSTOMIZED_FORMAT = {'excel': '.xlsx', 'yaml': '.yaml'}
        if isinstance(path_arg, list):
            if len(path_arg) == 1:
                src_path = path_arg[0]
            else:
                logger.warning(f"Cannot analyze with multiple path: {path_arg}")

    success, msg, output_path, output_file, output_extension = check_output_format(output_file_or_dir, file_format,
                                                                                   CUSTOMIZED_FORMAT)
    if output_path == "":
        output_path = _executed_path

    if not success:
        logger.error(msg)
        sys.exit(1)
    try:
        if mode == "compare":
            if before_comp_f == '' or after_comp_f == '':
                logger.error("before and after files are necessary.")
                return False
            if not os.path.exists(os.path.join(_executed_path, before_comp_f)):
                logger.error("Cannot find before FOSSLight report file (1st param with -y option).")
                return False
            if not os.path.exists(os.path.join(_executed_path, after_comp_f)):
                logger.error("Cannot find after FOSSLight report file (2nd param with -y option).")
                return False
            ret, final_excel_dir, result_log = init(output_path)

            run_compare(os.path.join(_executed_path, before_comp_f), os.path.join(_executed_path, after_comp_f),
                        final_excel_dir, output_file, output_extension, _start_time, _output_dir)
        else:
            run_src = False
            run_bin = False
            run_dep = False
            run_prechecker = False
            remove_downloaded_source = False

            if mode == "prechecker" or mode == "reuse":
                run_prechecker = True
            elif mode == "binary" or mode == "bin":
                run_bin = True
            elif mode == "source" or mode == "src":
                run_src = True
            elif mode == "dependency" or mode == "dep":
                run_dep = True
            else:
                run_src = True
                run_bin = True
                run_dep = True
                run_prechecker = True

            if src_path == "" and url_to_analyze == "":
                src_path, dep_arguments, url_to_analyze = get_input_mode(_executed_path, mode)

            if not hide_progressbar:
                timer = TimerThread()
                timer.setDaemon(True)
                timer.start()

            if url_to_analyze != "":
                remove_downloaded_source = True
                default_oss_name = extract_name_from_link(url_to_analyze)
                success, src_path = download_source(url_to_analyze, output_path)

            if not correct_fpath:
                correct_fpath = src_path

            if src_path != "":
                run_scanner(src_path, dep_arguments, output_path, keep_raw_data,
                            run_src, run_bin, run_dep, run_prechecker,
                            remove_downloaded_source, {}, output_file,
                            output_extension, num_cores, db_url,
                            default_oss_name, url_to_analyze,
                            correct_mode, correct_fpath)
        try:
            if not keep_raw_data:
                logger.debug(f"Remove temporary files: {_output_dir}")
                shutil.rmtree(_output_dir)
        except Exception as ex:
            logger.debug(f"Error to remove temp files:{ex}")
    except Exception as ex:
        logger.warning(str(ex))
        return False
    return True
