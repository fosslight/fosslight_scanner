#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Scanner
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import sys
import re
import logging
import warnings
import yaml
import shutil
import shlex
import subprocess
from pathlib import Path
from datetime import datetime

from fosslight_binary import binary_analysis
from fosslight_dependency.run_dependency_scanner import run_dependency_scanner
from fosslight_util.download import cli_download_and_extract, compression_extension
from fosslight_util.download import extract_compressed_file as extract_file
from ._get_input import get_input_mode
from fosslight_util.set_log import init_log
from fosslight_util.timer_thread import TimerThread
import fosslight_util.constant as constant
from fosslight_util.output_format import check_output_format
from fosslight_util.cover import CoverItem
from fosslight_util.oss_item import ScannerItem
from fosslight_util.output_format import write_output_file

from .common import (
    call_analysis_api, update_oss_item,
    correct_scanner_result, create_scancodejson
)
from ._run_compare import run_compare

fosslight_source_installed = True
try:
    from fosslight_source.cli import run_scanners as source_analysis
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
SCANNER_MODE = [
    "all", "compare", "binary",
    "bin", "src", "source", "dependency", "dep"
]


def run_dependency(path_to_analyze, output_file_with_path, params="", path_to_exclude=[]):
    result = []

    package_manager = ""
    pip_activate_cmd = ""
    pip_deactivate_cmd = ""
    output_custom_dir = ""
    app_name = ""
    github_token = ""

    try:
        if params:
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
        success, scan_item = call_analysis_api(
            path_to_analyze, "Dependency Analysis",
            1, run_dependency_scanner,
            package_manager,
            os.path.abspath(path_to_analyze),
            output_file_with_path,
            pip_activate_cmd, pip_deactivate_cmd,
            output_custom_dir, app_name,
            github_token, path_to_exclude=path_to_exclude
        )
        if success:
            result = scan_item
    except Exception as ex:
        logger.warning(f"Run dependency: {ex}")

    return result


def source_analysis_wrapper(*args, **kwargs):
    selected_scanner = kwargs.pop('selected_scanner', 'all')
    source_write_json_file = kwargs.pop('source_write_json_file', False)
    source_print_matched_text = kwargs.pop('source_print_matched_text', False)
    source_time_out = kwargs.pop('source_time_out', 120)
    args = list(args)
    args.insert(2, source_write_json_file)
    args.insert(5, source_print_matched_text)

    return source_analysis(*args, selected_scanner=selected_scanner, time_out=source_time_out, **kwargs)


def run_scanner(src_path, dep_arguments, output_path, keep_raw_data=False,
                run_src=True, run_bin=True, run_dep=True, run_prechecker=False,
                remove_src_data=True, result_log={}, output_file="",
                output_extension="", num_cores=-1, db_url="",
                default_oss_name="", default_oss_version="", url="",
                correct_mode=True, correct_fpath="", ui_mode=False, path_to_exclude=[],
                selected_source_scanner="all", source_write_json_file=False, source_print_matched_text=False,
                source_time_out=120, binary_simple=False):
    final_excel_dir = output_path
    success = True
    all_cover_items = []
    all_scan_item = ScannerItem(PKG_NAME, _start_time)
    if not remove_src_data:
        success, final_excel_dir, result_log = init(output_path)

    if output_file == "":
        output_file = OUTPUT_REPORT_PREFIX + _start_time

    if output_extension == "":
        output_extension = ".xlsx"

    if not correct_fpath:
        correct_fpath = src_path

    try:
        final_excel_dir = os.path.abspath(final_excel_dir)
        abs_path = os.path.abspath(src_path)

        if success:
            output_files = {"SRC": f"fosslight_src_{_start_time}{output_extension}",
                            "BIN": f"fosslight_bin_{_start_time}{output_extension}",
                            "DEP": f"fosslight_dep_{_start_time}{output_extension}"}

            if run_src:
                try:
                    if fosslight_source_installed:
                        src_output = os.path.join(_output_dir, output_files["SRC"])
                        success, result = call_analysis_api(
                                    src_path,
                                    "Source Analysis",
                                    -1, source_analysis_wrapper,
                                    abs_path,
                                    src_output,
                                    num_cores,
                                    False,
                                    path_to_exclude=path_to_exclude,
                                    selected_scanner=selected_source_scanner,
                                    source_write_json_file=source_write_json_file,
                                    source_print_matched_text=source_print_matched_text,
                                    source_time_out=source_time_out
                        )
                        if success:
                            all_scan_item.file_items.update(result[2].file_items)
                            all_cover_items.append(result[2].cover)

                    else:  # Run fosslight_source by using docker image
                        src_output = os.path.join("output", output_files["SRC"])
                        output_rel_path = os.path.relpath(abs_path, os.getcwd())
                        command = shlex.quote(f"docker run -it -v {_output_dir}:/app/output "
                                              f"fosslight -p {output_rel_path} -o {src_output}")
                        if path_to_exclude:
                            command += f" -e {' '.join(path_to_exclude)}"
                        command_result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
                        logger.info(f"Source Analysis Result:{command_result.stdout}")

                except Exception as ex:
                    logger.warning(f"Failed to run source analysis: {ex}")

            if run_bin:
                success, result = call_analysis_api(src_path, "Binary Analysis",
                                                    1, binary_analysis.find_binaries,
                                                    abs_path,
                                                    os.path.join(_output_dir, output_files["BIN"]),
                                                    "", db_url, binary_simple,
                                                    correct_mode, correct_fpath,
                                                    path_to_exclude=path_to_exclude)
                if success:
                    all_scan_item.file_items.update(result.file_items)
                    all_cover_items.append(result.cover)

            if run_dep:
                dep_scanitem = run_dependency(src_path, os.path.join(_output_dir, output_files["DEP"]),
                                              dep_arguments, path_to_exclude)
                all_scan_item.file_items.update(dep_scanitem.file_items)
                all_cover_items.append(dep_scanitem.cover)

        else:
            return

    except Exception as ex:
        logger.error(f"Scanning: {ex}")

    try:
        output_file_without_ext = os.path.join(final_excel_dir, output_file)
        final_report = f"{output_file_without_ext}{output_extension}"
        cover = CoverItem(tool_name=PKG_NAME,
                          start_time=_start_time,
                          input_path=abs_path,
                          exclude_path=path_to_exclude,
                          simple_mode=False)
        merge_comment = []
        for ci in all_cover_items:
            merge_comment.append(str(f'[{ci.tool_name}] {ci.comment}'))
        cover.comment = '\n'.join(merge_comment)
        all_scan_item.cover = cover

        if correct_mode:
            all_scan_item = correct_scanner_result(all_scan_item)

        if remove_src_data:
            all_scan_item = update_oss_item(all_scan_item, default_oss_name, default_oss_version, url)
        success, err_msg, final_report = write_output_file(output_file_without_ext, output_extension, all_scan_item)
        if success:
            if os.path.isfile(final_report):
                logger.info(f'Generated the result file: {final_report}')
                result_log["Output File"] = final_report
            else:
                result_log["Output File"] = 'Nothing is detected from the scanner so output file is not generated.'
        else:
            logger.error(f"Fail to generate a result file({final_report}): {err_msg}")

        if ui_mode:
            ui_mode_report = f"{output_file_without_ext}.json"
            success, err_msg = create_scancodejson(all_scan_item, ui_mode_report, src_path)
            if success and os.path.isfile(ui_mode_report):
                logger.info(f'Generated the ui mode result file: {ui_mode_report}')
            else:
                logger.error(f'Fail to generate a ui mode result file({ui_mode_report}): {err_msg}')

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
    oss_name = ""
    oss_version = ""
    try:
        success, final_excel_dir, result_log = init(out_dir)
        temp_src_dir = os.path.join(
            _output_dir, SRC_DIR_FROM_LINK_PREFIX + start_time)

        link = link.strip()
        logger.info(f"Link to download: {link}")
        success, msg, oss_name, oss_version = cli_download_and_extract(
            link, temp_src_dir, _output_dir)

        if success:
            logger.info(f"Downloaded Dir: {temp_src_dir}")
        else:
            temp_src_dir = ""
            logger.error(f"Download failed: {msg}")
    except Exception as ex:
        success = False
        logger.error(f"Failed to analyze from link: {ex}")
    return success, temp_src_dir, oss_name, oss_version


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


def run_main(mode_list, path_arg, dep_arguments, output_file_or_dir, file_format, url_to_analyze,
             db_url, hide_progressbar=False, keep_raw_data=False, num_cores=-1,
             correct_mode=True, correct_fpath="", ui_mode=False, path_to_exclude=[],
             selected_source_scanner="all", source_write_json_file=False, source_print_matched_text=False,
             source_time_out=120, binary_simple=False):
    global _executed_path, _start_time

    output_file = ""
    default_oss_name = ""
    default_oss_version = ""
    src_path = ""
    _executed_path = os.getcwd()
    extract_folder = ""

    mode_not_supported = list(set(mode_list).difference(SCANNER_MODE))
    if mode_not_supported:
        logger.error(f"[Error]: An unsupported mode was entered.:{mode_not_supported}")
        sys.exit(1)
    if "compare" in mode_list and len(mode_list) > 1:
        logger.error("[Error]: Compare mode cannot be run together with other modes.")
        sys.exit(1)

    if "compare" in mode_list:
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

                for ext in compression_extension:
                    if src_path.endswith(ext):
                        temp_folder = f"temp_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        Path(temp_folder).mkdir(parents=True, exist_ok=True)

                        extract_success = extract_file(src_path, temp_folder, False)
                        if extract_success:
                            src_path = os.path.join(_executed_path, temp_folder)
                            extract_folder = src_path
                        break
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
        if "compare" in mode_list:
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
            remove_downloaded_source = False

            if "all" in mode_list or (not mode_list):
                run_src = True
                run_bin = True
                run_dep = True
            else:
                if "binary" in mode_list or "bin" in mode_list:
                    run_bin = True
                if "source" in mode_list or "src" in mode_list:
                    run_src = True
                if "dependency" in mode_list or "dep" in mode_list:
                    run_dep = True

            if run_dep or run_src or run_bin:
                if src_path == "" and url_to_analyze == "":
                    src_path, dep_arguments, url_to_analyze = get_input_mode(_executed_path, mode_list)

                if not hide_progressbar:
                    timer = TimerThread()
                    timer.setDaemon(True)
                    timer.start()

                if url_to_analyze != "":
                    remove_downloaded_source = True
                    success, src_path, default_oss_name, default_oss_version = download_source(url_to_analyze, output_path)

                if output_extension == ".yaml":
                    correct_mode = False
                    correct_fpath = ""
                else:
                    if not correct_fpath:
                        correct_fpath = src_path

                if src_path != "":
                    run_scanner(src_path, dep_arguments, output_path, keep_raw_data,
                                run_src, run_bin, run_dep, '',
                                remove_downloaded_source, {}, output_file,
                                output_extension, num_cores, db_url,
                                default_oss_name, default_oss_version, url_to_analyze,
                                correct_mode, correct_fpath, ui_mode, path_to_exclude,
                                selected_source_scanner, source_write_json_file, source_print_matched_text, source_time_out,
                                binary_simple)

                if extract_folder:
                    shutil.rmtree(extract_folder)
            else:
                logger.error("No mode has been selected for analysis.")
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
