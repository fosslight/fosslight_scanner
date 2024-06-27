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
import fosslight_util.constant as constant
from fosslight_util.parsing_yaml import parsing_yml
from fosslight_util.write_yaml import create_yaml_with_ossitem
from fosslight_util.write_scancodejson import write_scancodejson
from fosslight_util.read_excel import read_oss_report
from fosslight_util.output_format import write_output_file
from fosslight_util.oss_item import OssItem

logger = logging.getLogger(constant.LOGGER_NAME)
SRC_SHEET = 'SRC_FL_Source'
BIN_SHEET = 'BIN_FL_Binary'
BIN_EXT_HEADER = {'BIN_FL_Binary': ['ID', 'Binary Path', 'OSS Name',
                                    'OSS Version', 'License', 'Download Location',
                                    'Homepage', 'Copyright Text', 'Exclude',
                                    'Comment', 'Vulnerability Link', 'TLSH', 'SHA1']}
BIN_HIDDEN_HEADER = {'TLSH', "SHA1"}


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
    else:
        return True, copied_file


def run_analysis(path_to_run, params, func, str_run_start, output, exe_path):
    # This function will be replaced by call_analysis_api().
    logger.info("## Start to run "+str_run_start)
    return_value = ""
    try:
        if path_to_run != "":
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
        if path_to_run != "":
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
        if success:
            if result and return_idx >= 0:
                if len(result) > return_idx:
                    result = result[return_idx]
                else:
                    success = False
    except Exception as ex:
        logger.debug(f"Get return value:{ex}")
        success = False
    if not result:
        result = []
    return success, result


def overwrite_excel(excel_file_path, oss_name, column_name='OSS Name'):
    if oss_name != "":
        try:
            files = os.listdir(excel_file_path)
            for file in files:
                if file.endswith(".xlsx"):
                    file = os.path.join(excel_file_path, file)
                    excel_file = pd.ExcelFile(file, engine='openpyxl')

                    for sheet_name in excel_file.sheet_names:
                        try:
                            df = pd.read_excel(file, sheet_name=sheet_name, engine='openpyxl')
                            if column_name in df.columns:
                                updated = (df[column_name] == '') | (df[column_name].isnull())
                                df.loc[updated, column_name] = oss_name
                                df.to_excel(file, sheet_name=sheet_name, index=False)
                        except Exception as ex:
                            logger.debug(f"overwrite_sheet {sheet_name}:{ex}")
        except Exception as ex:
            logger.debug(f"overwrite_excel:{ex}")


def merge_yamls(_output_dir, merge_yaml_files, final_report, remove_src_data=False,
                default_oss_name='', default_oss_version='', url=''):
    success = True
    err_msg = ''

    oss_total_list = []
    yaml_dict = {}
    try:
        for mf in merge_yaml_files:
            if os.path.exists(os.path.join(_output_dir, mf)):
                oss_list, _, _ = parsing_yml(os.path.join(_output_dir, mf), _output_dir)

                if remove_src_data:
                    existed_yaml = {}
                    for oi in oss_list:
                        oi.name = default_oss_name if oi.name == '' else oi.name
                        oi.version = default_oss_version if oi.version == '' else oi.version
                        oi.download_location = url if oi.download_location == '' else oi.download_location
                        create_yaml_with_ossitem(oi, existed_yaml)
                    with open(os.path.join(_output_dir, mf), 'w') as f:
                        yaml.dump(existed_yaml, f, default_flow_style=False, sort_keys=False)

                oss_total_list.extend(oss_list)

        if oss_total_list != []:
            for oti in oss_total_list:
                create_yaml_with_ossitem(oti, yaml_dict)
            with open(os.path.join(_output_dir, final_report), 'w') as f:
                yaml.dump(yaml_dict, f, default_flow_style=False, sort_keys=False)
        else:
            success = False
            err_msg = "Output file is not created as no oss items detected."
    except Exception as ex:
        err_msg = ex
        success = False

    return success, err_msg


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


def correct_scanner_result(_output_dir, output_files, output_extension, exist_src, exist_bin):
    src_oss_list = []
    bin_oss_list = []
    duplicates = False

    if exist_src:
        src_oss_list = check_exclude_dir(get_osslist(_output_dir, output_files['SRC'], output_extension, SRC_SHEET))
    if exist_bin:
        bin_oss_list = check_exclude_dir(get_osslist(_output_dir, output_files['BIN'], output_extension, BIN_SHEET))

    if exist_src and exist_bin:
        try:
            remove_src_idx_list = []
            for idx_src, src_item in enumerate(src_oss_list):
                dup_flag = False
                for bin_item in bin_oss_list:
                    if (not src_item.source_name_or_path):
                        continue
                    if src_item.source_name_or_path[0] == bin_item.source_name_or_path[0]:
                        dup_flag = True
                        if not bin_item.license and src_item.license:
                            src_item.exclude = bin_item.exclude
                            bin_item.set_sheet_item(src_item.get_print_array(constant.FL_BINARY)[0])
                            if bin_item.comment:
                                bin_item.comment += '/'
                            bin_item.comment += 'Loaded from SRC OSS info'
                if dup_flag:
                    remove_src_idx_list.append(idx_src)
            if remove_src_idx_list:
                duplicates = True
                for i in sorted(remove_src_idx_list, reverse=True):
                    del src_oss_list[i]
        except Exception as ex:
            logger.warning(f"correct the scanner result:{ex}")

    try:
        if exist_src:
            success, err_msg = write_output_with_osslist(src_oss_list, _output_dir, output_files['SRC'],
                                                         output_extension, SRC_SHEET)
            if not success:
                logger.warning(err_msg)
        if exist_bin:
            success, err_msg = write_output_with_osslist(bin_oss_list, _output_dir, output_files['BIN'],
                                                         output_extension, BIN_SHEET, BIN_EXT_HEADER, BIN_HIDDEN_HEADER)
            if not success:
                logger.warning(err_msg)
        if duplicates:
            logger.info('Success to correct the src/bin scanner result')
    except Exception as ex:
        logger.warning(f"Corrected src/bin scanner result:{ex}")
    return


def write_output_with_osslist(oss_list, output_dir, output_file, output_extension, sheetname, extended_hdr={}, hidden_hdr={}):
    new_oss_list = []
    sheet_list = {}
    sheet_list[sheetname] = []

    for src_item in oss_list:
        scanner_name = constant.supported_sheet_and_scanner[sheetname]
        new_oss_list.append(src_item.get_print_array(scanner_name)[0])
    sheet_list[sheetname].extend(new_oss_list)
    if os.path.exists(os.path.join(output_dir, output_file)):
        os.remove(os.path.join(output_dir, output_file))
    success, err_msg, _ = write_output_file(os.path.join(output_dir, output_file).rstrip(output_extension),
                                            output_extension, sheet_list, extended_hdr, hidden_hdr)
    return success, err_msg


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


def check_exclude_dir(oss_list):
    _exclude_dirs = ["venv", "node_modules", "Pods", "Carthage"]

    for oss_item in oss_list:
        if not oss_item.source_name_or_path:
            continue
        for exclude_dir in _exclude_dirs:
            if exclude_dir in oss_item.source_name_or_path[0].split(os.path.sep):
                oss_item.exclude = True
                break
    return oss_list
