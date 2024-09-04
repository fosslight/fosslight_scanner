#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Scanner
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import sys
import logging
import shutil
import pandas as pd
import yaml
from fosslight_util.constant import LOGGER_NAME, FOSSLIGHT_SOURCE, FOSSLIGHT_BINARY
from fosslight_util.parsing_yaml import parsing_yml
from fosslight_util.write_scancodejson import write_scancodejson
from fosslight_util.read_excel import read_oss_report
from fosslight_util.oss_item import OssItem

logger = logging.getLogger(LOGGER_NAME)
SRC_SHEET = 'SRC_FL_Source'
BIN_SHEET = 'BIN_FL_Binary'
BIN_EXT_HEADER = {
    'BIN_FL_Binary': [
        'ID', 'Binary Path', 'OSS Name', 'OSS Version', 'License',
        'Download Location', 'Homepage', 'Copyright Text', 'Exclude',
        'Comment', 'Vulnerability Link', 'TLSH', 'SHA1'
    ]
}
BIN_HIDDEN_HEADER = {'TLSH', 'SHA1'}


def copy_file(source, destination):
    copied_file = ""
    try:
        shutil.copy(source, destination)
        if os.path.isdir(destination):
            copied_file = os.path.join(destination, os.path.basename(source))
        else:
            copied_file = destination
    except Exception as ex:
        logger.debug(f"Failed to copy {source} to {destination}: {ex}")
        return False, copied_file
    return True, copied_file


def run_analysis(path_to_run, params, func, str_run_start, output, exe_path):
    # This function will be replaced by call_analysis_api().
    logger.info("## Start to run " + str_run_start)
    return_value = ""
    try:
        if path_to_run:
            logger.info(f"|--- Path to analyze : {path_to_run}")
            os.chdir(output)
            sys.argv = params
            return_value = func()
            os.chdir(exe_path)
        else:
            logger.info("Analyzing path is missing...")
    except SystemExit:
        pass
    except Exception as ex:
        logger.error(f"{str_run_start}:{ex}")
    return return_value


def call_analysis_api(path_to_run, str_run_start, return_idx, func, *args, **kwargs):
    # return_idx == -1 : Raw return value itself
    logger.info(f"## Start to run {str_run_start}")
    success = True
    result = []
    try:
        if path_to_run:
            logger.info(f"|--- Path to analyze : {path_to_run}")
            result = func(*args, **kwargs)
        else:
            logger.info("Analyzing path is missing...")
    except SystemExit:
        success = False
    except Exception as ex:
        success = False
        logger.error(f"{str_run_start}:{ex}")
    try:
        if success and result and return_idx >= 0:
            if len(result) > return_idx:
                result = result[return_idx]
            else:
                success = False
    except Exception as ex:
        logger.debug(f"Get return value:{ex}")
        success = False
    return success, result or []


def update_oss_item(scan_item, oss_name, oss_version, download_loc):
    for file_items in scan_item.file_items.values():
        for file_item in file_items:
            if file_item.oss_items:
                for oi in file_item.oss_items:
                    if oi.name == '' and oi.version == '' and oi.download_location == '':
                        oi.name = oss_name
                        oi.version = oss_version
                        oi.download_location = download_loc
            else:
                file_item.oss_items.append(OssItem(oss_name, oss_version, '', download_loc))
    return scan_item


def create_scancodejson(final_report, output_extension, ui_mode_report, src_path=""):
    success = True
    err_msg = ''

    oss_total_list = []
    root_dir = ""
    root_strip = ""
    try:
        src_path = os.path.abspath(src_path)
        parent = os.path.basename(src_path)
        root_strip = src_path.replace(parent, "")
        root_dir = parent
    except Exception:
        root_dir = ""

    try:
        item_without_oss = OssItem("")
        oss_total_list = get_osslist(os.path.dirname(final_report), os.path.basename(final_report),
                                     output_extension, '')
        if src_path:
            for root, dirs, files in os.walk(src_path):
                root = root.replace(root_strip, "")
                for file in files:
                    item_path = os.path.join(root, file)
                    item_path = item_path.replace(parent + os.path.sep, '', 1)
                    included = any(item_path in x.source_name_or_path for x in oss_total_list)
                    if not included:
                        item_without_oss.source_name_or_path = item_path
            if len(item_without_oss.source_name_or_path) > 0:
                oss_total_list.append(item_without_oss)
        if root_dir:
            for oss in oss_total_list:
                tmp_path_list = oss.source_name_or_path
                oss.source_name_or_path = ""
                oss.source_name_or_path = [os.path.join(root_dir, path) for path in tmp_path_list]

        write_scancodejson(os.path.dirname(ui_mode_report), os.path.basename(ui_mode_report),
                           oss_total_list)
    except Exception as ex:
        err_msg = ex
        success = False

    return success, err_msg


def correct_scanner_result(all_scan_item):
    duplicates = False

    keys_needed = {FOSSLIGHT_SOURCE, FOSSLIGHT_BINARY}
    is_contained = keys_needed.issubset(all_scan_item.file_items.keys())
    if is_contained:
        src_fileitems = all_scan_item.file_items[FOSSLIGHT_SOURCE]
        bin_fileitems = all_scan_item.file_items[FOSSLIGHT_BINARY]
        try:
            remove_src_idx_list = []
            for idx_src, src_fileitem in enumerate(src_fileitems):
                src_fileitem.exclude = check_exclude_dir(src_fileitem.source_name_or_path)
                dup_flag = False
                for bin_fileitem in bin_fileitems:
                    bin_fileitem.exclude = check_exclude_dir(bin_fileitem.source_name_or_path)
                    if src_fileitem.source_name_or_path == bin_fileitem.source_name_or_path:
                        dup_flag = True
                        src_all_licenses_non_empty = all(oss_item.license for oss_item in src_fileitem.oss_items)
                        bin_empty_license_exists = all(not oss_item.license for oss_item in bin_fileitem.oss_items)

                        if src_all_licenses_non_empty and bin_empty_license_exists:
                            exclude = bin_fileitem.oss_items[0].exclude
                            bin_fileitem.oss_items = []
                            for src_oss_item in src_fileitem.oss_items:
                                src_oss_item.exclude = exclude
                                bin_fileitem.oss_items.append(src_oss_item)
                            bin_fileitem.comment = 'Loaded from SRC OSS info'
                if dup_flag:
                    remove_src_idx_list.append(idx_src)
            if remove_src_idx_list:
                duplicates = True
                for i in sorted(remove_src_idx_list, reverse=True):
                    del src_fileitems[i]
        except Exception as ex:
            logger.warning(f"correct the scanner result:{ex}")

    try:
        if duplicates:
            logger.info('Success to correct the src/bin scanner result')
    except Exception as ex:
        logger.warning(f"Corrected src/bin scanner result:{ex}")
    return all_scan_item


def get_osslist(_output_dir, output_file, output_extension, sheet_name=''):
    err_reason = ''
    oss_list = []
    oss_file_with_fullpath = os.path.join(_output_dir, output_file)

    if os.path.exists(oss_file_with_fullpath):
        if output_extension == '.xlsx':
            oss_list = read_oss_report(oss_file_with_fullpath, sheet_name)
        elif output_extension == '.yaml':
            oss_list, _, err_reason = parsing_yml(oss_file_with_fullpath, _output_dir)
        else:
            err_reason = f'Not supported extension: {output_extension}'
    if err_reason:
        logger.info(f'get_osslist: {err_reason}')
    return oss_list


def check_exclude_dir(source_name_or_path):
    _exclude_dirs = ["venv", "node_modules", "Pods", "Carthage"]
    exclude = False

    for exclude_dir in _exclude_dirs:
        if exclude_dir in source_name_or_path.split(os.path.sep):
            exclude = True
            break
    return exclude
